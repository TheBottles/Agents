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
from AStar2 import A_Star
from unitselection import *

np.set_printoptions(suppress=True)

_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_AI_SELECTED = features.SCREEN_FEATURES.selected.index
_NO_OP = actions.FUNCTIONS.no_op.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
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
    _ATTACK_SCREEN,
    _MOVE_RAND,
    _MOVE_MIDDLE,
    _MOVE_SCREEN
]



def get_target_coords(obs):
    # Todo: handle case when there are no enemy coordiantes
    screen_features = get_units(obs)
    targetxs, targetys = get_unit_coors(screen_features, _AI_HOSTILE)
    selfxs, selfys = get_unit_coors(screen_features, _AI_SELF)
    selfx = selfxs.mean()
    selfy = selfys.mean()
    loc = (selfx, selfy)

    xmax = np.argmax(targetxs)
    xmin = np.argmin(targetxs)
    ymax = np.argmax(targetys)
    ymin = np.argmin(targetys)
    #Todo: transform the rectangle area to be angled
    labely = (targetys[ymax] - targetys[ymin])
    labelx = (targetxs[xmax] - targetxs[xmin])

    if labelx > labely:
        if Distance_Calc(loc, (targetxs[ymin], targetys[ymin])) < Distance_Calc(loc, (targetxs[ymax], targetys[ymax])):
            return targetxs[ymin], targetys[ymin]
        else: return targetxs[ymax], targetys[ymax]
    else:
        if Distance_Calc(loc, (targetxs[xmin], targetys[xmin])) < Distance_Calc(loc, (targetxs[xmax], targetys[xmax])):
            return targetxs[xmin], targetys[xmin]
        else: return targetxs[xmax], targetys[xmax]

def get_eps_threshold(steps_done):
    return EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)

def get_state(obs):
    """ Takes in an observation
        Returns a 2-tuple:
            1st item is also a 2-tuple of boolean values indicating state
                -- this can be changed to accomidate more states (ex searching)
            2nd item is a 1x2 numpy array of xy coordinates to a target location
    """
    # need a better way to determine target destination, roach range is 4
    targetxs, targetys = get_target_coords(obs)
    screen_features = get_units(obs)
    marinexs, marineys = get_unit_coors(screen_features, 1)
    marinex, mariney = marinexs.mean(), marineys.mean()
    marine_on_target = np.min(targetxs) <= marinex <= np.max(
        targetxs) and np.min(targetys) <= mariney <= np.max(targetys)
    enemy = bool(get_alliance_units(screen_features, _AI_HOSTILE))
    return (enemy, int(marine_on_target)), [targetxs, targetys], (marinex, mariney)


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

    def get_action(self, state, allowed_actions):
        actions = list(set(possible_actions).intersection(allowed_actions))
        print(possible_actions)
        print(allowed_actions)
        print(actions)
        if not self.load_qt and np.random.rand() < get_eps_threshold(steps):
            # currently arbitrarily picks an action if the state does not already exist
            return np.random.randint(0, len(actions))
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
                possible_actions, load_qt="qTable-moveToBacon.npy", load_st="qStates-moveToBacon.npy")
        else:
            self.qtable = QTable(possible_actions)
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
            # pprint(obs)
            # exit()
        if obs.last():
            self.qtable.save_qtable('qTable')
            self.qtable.save_states('qStates')
            np.save('sampleobs', obs)


        # pprint(obs.observation)
            #pprint(obs)

        self.prev_state = state
        action = self.qtable.get_action(state, obs.observation['available_actions'])
        self.prev_action = action
        func = actions.FunctionCall(_NO_OP, [])
        units = get_units(obs)
        if possible_actions[action] == _NO_OP or possible_actions[action] == _MOVE_SCREEN:
            print("_NO_OP")
            func = actions.FunctionCall(_NO_OP, [])
        elif state[0] and possible_actions[action] == _MOVE_RAND:
            print("_MOVE_RAND")
            target_x, target_y = target_pos[0].max(), target_pos[1].max()
            func = actions.FunctionCall(
            _ATTACK_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
        elif state[0] and possible_actions[action] == _ATTACK_SCREEN:
            print("_ATTACK_SCREEN")
            target_x, target_y = A_Star(obs, current_pos, target_pos)
            func = actions.FunctionCall(
                _ATTACK_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
        elif possible_actions[action] == _SELECT_ARMY:
            print("_SELECT_ARMY")
            func = actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
        elif state[0] and possible_actions[action] == _SELECT_POINT:
            print("_SELET_POINT")
            # ai_view = obs.observation['screen'][_AI_RELATIVE]
            # backgroundxs, backgroundys = (ai_view == _BACKGROUND).nonzero()
            pprint(obs.observation['feature_screen'])
            pprint(obs.observation['feature_screen'].shape)

            backgroundxs, backgroundys = obs.observation['feature_screen'][_AI_RELATIVE].nonzero()
            point = np.random.randint(0, len(backgroundxs))
            backgroundx, backgroundy = backgroundxs[point], backgroundys[point]
            func = actions.FunctionCall(
                _SELECT_POINT, [_NOT_QUEUED, [backgroundy, backgroundx]])
        elif state[0] and possible_actions[action] == _MOVE_MIDDLE:
            func = actions.FunctionCall(_ATTACK_SCREEN, [_NOT_QUEUED, [32, 32]])

        try:
            return func
        except ValueError:
            return actions.FunctionCall(_NO_OP, [])
