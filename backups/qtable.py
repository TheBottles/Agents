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
from pathfinder import a_star
from unitselection import *

from random import randint

from constants import *

np.set_printoptions(threshold=np.nan)

def get_flank_coords(obs, flanker):
    # Todo: handle case when there are no enemy coordiantes
    screen_features = get_units(obs)
    targetxs, targetys = get_unit_coors(screen_features, _AI_HOSTILE)

    if not targetxs.size: return (randint(0,63), randint(0,63))

    if flanker: return targetxs.mean(), targetys.mean()

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

    # if
    if labelx > labely:
        # Our group units are closer to the top of the enemy units
        if distance(loc, (targetxs[ymin], targetys[ymin])) < distance(loc, (targetxs[ymax], targetys[ymax])):
            target = targetxs[ymin], targetys[ymin]
        # Our group units are closer to the bottom of the enemy units
        else: target =  targetxs[ymax], targetys[ymax]
    else:

        if distance(loc, (targetxs[xmin], targetys[xmin])) < distance(loc, (targetxs[xmax], targetys[xmax])):
            target =  targetxs[xmin], targetys[xmin]
        else: target =  targetxs[xmax], targetys[xmax]
    #
    # print("Target:", target)
    #
    # for x,y in zip(targetxs, targetys):
    #     print("    ", x,y)
    return target

def get_state(obs, selected = False, controlled = False, flanker = False, groups = []):
    """ Takes in an observation
        Returns a 2-tuple:
            1st item is also a 2-tuple of boolean values indicating state
                -- this can be changed to accomidate more states (ex searching)
            2nd item is a 1x2 numpy array of xy coordinates to a target location
    """
    screen_features = get_units(obs)

    # need a better way to determine target destination, roach range is 4
    targetxs, targetys = get_flank_coords(obs, flanker)
    marineys, marinexs = obs.observation['feature_screen']['selected'].nonzero()
    if len(marinexs) > 0:
        marinex, mariney = marinexs.mean(), marineys.mean()
        marine_on_target = np.min(targetxs) <= marinex <= np.max(
            targetxs) and np.min(targetys) <= mariney <= np.max(targetys)
    else:
        marinex, mariney = (0,0)
        marine_on_target = False
    enemy = bool(get_alliance_units(screen_features, _AI_HOSTILE))

    multiple = len(groups) > 1

    return (enemy, selected, int(marine_on_target), multiple, controlled, flanker), [targetxs, targetys], (marinex, mariney)

def get_eps_threshold(steps_done):
    return EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)

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
                (3, len(possible_action)))  # create a Q table

    def get_action(self, state):
        if not self.load_qt and np.random.rand() < get_eps_threshold(steps):
            return np.random.randint(0, len(self.actions))
        else:
            if state not in self.states_list:
                self.add_state(state)
            idx = list(self.states_list).index(state)
            q_values = self.q_table[idx]
            return int(np.argmax(q_values))

    def add_state(self, state):
        self.q_table = np.vstack(
            [self.q_table, np.zeros((1, len(possible_action)))])
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
