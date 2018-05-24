import math
import numpy as np
from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.env import sc2_env, run_loop, available_actions_printer
from pysc2 import maps
from absl import flags
import os
import time
from s2clientprotocol import raw_pb2 as sc_raw
from s2clientprotocol import sc2api_pb2 as sc_pb
from pprint import pprint
from coordgrabber import *
from AStar2 import *

np.set_printoptions(suppress=True)

_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_AI_SELECTED = features.SCREEN_FEATURES.selected.index
_NO_OP = actions.FUNCTIONS.no_op.id
_MOVE_SCREEN = actions.FUNCTIONS.Attack_screen.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_MOVE_RAND = 1000
_MOVE_MIDDLE = 2000
_BACKGROUND = 0
_AI_SELF = 1
_AI_ALLIES = 2
_AI_NEUTRAL = 3
_AI_HOSTILE = 4
_SELECT_ALL = [0]
_NOT_QUEUED = [0]
EPS_START = 0.9
EPS_END = 0.025
EPS_DECAY = 2500
steps = 0


possible_actions = [
    _NO_OP,
    _SELECT_ARMY,
    _SELECT_POINT,
    _MOVE_SCREEN,
    _MOVE_RAND,
    _MOVE_MIDDLE
]



def get_target_coords(obs):
    # Todo: handle case when there are no enemy coordiantes
    targetxs, targetys = get_enemy_coords(obs)
    xmax = np.argmax(targetxs)
    xmin = np.argmin(targetxs)
    ymax = np.argmax(targetys)
    ymin = np.argmin(targetys)
    # print(xmin, xmax, ymin, ymax)
    # pprint(targetxs)
    # pprint(targetys)
    pprint(get_unit_types(obs, [targetxs, targetys]))
    #Todo: transform the rectangle area to be angled
    labely = (targetys[ymax] - targetys[ymin])
    labelx = (targetxs[xmax] - targetxs[xmin])
    if labelx > labely:
        return targetxs[ymin], targetys[ymin]
    else:
        return targetxs[xmin], targetys[xmin]

def get_eps_threshold(steps_done):
    return EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)


def get_state(obs):
    """ Takes in an observation
        Returns a 2-tuple:
            1st item is also a 2-tuple of boolean values indicating state
                -- this can be changed to accomidate more states (ex searching)
            2nd item is a 1x2 numpy array of xy coordinates to a target location
    """
    ai_view = obs.observation['screen'][_AI_RELATIVE]
    # need a better way to determine target destination, roach range is 4
    targetxs, targetys = get_target_coords(obs)
    marinexs, marineys = (ai_view == _AI_SELF).nonzero()
    marinex, mariney = marinexs.mean(), marineys.mean()
    marine_on_target = np.min(targetxs) <= marinex <= np.max(
        targetxs) and np.min(targetys) <= mariney <= np.max(targetys)

    ai_selected = obs.observation['screen'][_AI_SELECTED]
    marine_selected = int((ai_selected == 1).any())

    return (marine_selected, int(marine_on_target)), [targetxs, targetys], (marinex, mariney)


class QTable(object):
    def __init__(self, actions, lr=0.01, reward_decay=0.9, load_qt=None, load_st=None):
        self.lr = lr
        self.actions = actions
        self.reward_decay = reward_decay
        self.states_list = set()
        self.load_qt = load_qt
        if load_st:
            temp = self.load_states(load_st)
            self.states_list = set([tuple(temp[i]) for i in range(len(temp))])

        if load_qt:
            self.q_table = self.load_qtable(load_qt)
        else:
            self.q_table = np.zeros(
                (3, len(possible_actions)))  # create a Q table

    def get_action(self, state):
        if not self.load_qt and np.random.rand() < get_eps_threshold(steps):
            # currently arbitrarily picks an action if the state does not already exist
            return np.random.randint(0, len(self.actions))
        else:
            if state not in self.states_list:
                self.add_state(state)
            idx = list(self.states_list).index(state)
            q_values = self.q_table[idx]
            return int(np.argmax(q_values))

    def add_state(self, state):
        self.q_table = np.vstack(
            [self.q_table, np.zeros((1, len(possible_actions)))])
        self.states_list.add(state)

    def update_qtable(self, state, next_state, action, reward):
        if state not in self.states_list:
            self.add_state(state)
        if next_state not in self.states_list:
            self.add_state(next_state)
        state_idx = list(self.states_list).index(state)
        next_state_idx = list(self.states_list).index(next_state)
        q_state = self.q_table[state_idx, action]
        q_next_state = self.q_table[next_state_idx].max()
        q_targets = reward + (self.reward_decay * q_next_state)
        loss = q_targets - q_state
        self.q_table[state_idx, action] += self.lr * loss
        return loss

    def get_size(self):
        print(self.q_table.shape)

    def save_qtable(self, filepath):
        np.save(filepath, self.q_table)

    def load_qtable(self, filepath):
        return np.load(filepath)

    def save_states(self, filepath):
        temp = np.array(list(self.states_list))
        np.save(filepath, temp)

    def load_states(self, filepath):
        return np.load(filepath)


class FlankingAgent(base_agent.BaseAgent):
    def __init__(self, load_qt=None, load_st=None):
        super(FlankingAgent, self).__init__()
        if load_qt and load_st:
            self.qtable = QTable(
                possible_actions, load_qt="qTable-MoveToBacon.npy", load_st="qStates-MoveToBacon.npy")
        else:
            self.qtable = QTable(
                possible_actions, load_qt="qTable-MoveToBacon.npy", load_st="qStates-MoveToBacon.npy")
        self.steps = 0

    def step(self, obs):
        '''Step function gets called automatically by pysc2 environment'''
        super(FlankingAgent, self).step(obs)
        state, target_pos, current_pos = get_state(obs)

        if not obs.first():
            score = obs.observation['score_cumulative'][3] + \
                obs.observation['score_cumulative'][5] + \
                obs.observation['score_cumulative'][0]
            self.qtable.update_qtable(
                self.prev_state, state, self.prev_action, score)
        if obs.last():
            self.qtable.save_qtable('qTable-MoveToBacon')
            self.qtable.save_states('qStates-MoveToBacon')
            np.save('sampleobs', obs)
            #pprint(obs)

        self.prev_state = state
        action = self.qtable.get_action(state)
        self.prev_action = action
        func = actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, target_pos])

        if possible_actions[action] == _NO_OP:
            func = actions.FunctionCall(_NO_OP, [])
        elif state[0] and possible_actions[action] == _MOVE_SCREEN:
            target_x, target_y = A_star(obs, current_pos, target_pos)
            func = actions.FunctionCall(
                _MOVE_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
        elif possible_actions[action] == _SELECT_ARMY:
            func = actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
        elif state[0] and possible_actions[action] == _SELECT_POINT:
            ai_view = obs.observation['screen'][_AI_RELATIVE]
            backgroundxs, backgroundys = (ai_view == _BACKGROUND).nonzero()
            point = np.random.randint(0, len(backgroundxs))
            backgroundx, backgroundy = backgroundxs[point], backgroundys[point]
            func = actions.FunctionCall(
                _SELECT_POINT, [_NOT_QUEUED, [backgroundy, backgroundx]])
        elif state[0] and possible_actions[action] == _MOVE_RAND:
            target_x, target_y = target_pos[0].max(), target_pos[1].max()
            #movex, movey = np.random.randint(target_x, 64), np.random.randint(target_y, 64)
            func = actions.FunctionCall(
                _MOVE_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
        elif state[0] and possible_actions[action] == _MOVE_MIDDLE:
            func = actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, [32, 32]])
        return func
