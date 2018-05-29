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
from qtable import *
from unitselection import *


_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_AI_SELECTED = features.SCREEN_FEATURES.selected.index
_NO_OP = actions.FUNCTIONS.no_op.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_RECT = actions.FUNCTIONS.select_rect.id
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

SELECT_ADD_OPTIONS = [
    ("select", False),
    ("add", True),
]

possible_action = [
    _NO_OP,
    _SELECT_ARMY,
    # _SELECT_POINT,
    _SELECT_RECT,
    _ATTACK_SCREEN,
    # _MOVE_RAND,
    # _MOVE_MIDDLE,
    # _MOVE_SCREEN
]

class Group():

    def __init__(self, location = None):
        self.moving = False
        self.selected = False
        self.target = None
        self.prev_state = None
        self.prev_action = None
        self.prev_location = location

    def do_action(self, obs, qtable, group_queue):

        state, target_pos, current_pos = get_state(obs)

        self.prev_state = state
        action = qtable.get_action(state, obs.observation['available_actions'])
        self.prev_action = action
        self.moving = state[1]
        func = actions.FunctionCall(_NO_OP, [])
        units = get_units(obs)
        if not obs.last():
            score = obs.observation['score_cumulative'][3] + \
                obs.observation['score_cumulative'][5] + \
                obs.observation['score_cumulative'][0]
            qtable.update_qtable(
                self.prev_state, state, self.prev_action, score)

        if possible_action[action] == _ATTACK_SCREEN:
            print("DO A* AND ATTACK") # assume units are already selected here
            target_x, target_y = A_Star(obs, current_pos, target_pos)
            func = actions.FunctionCall(
                _ATTACK_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
            return False, func
        elif possible_action[action] == _SELECT_ARMY:
            print("Select entire army")
            func = actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
            return True, func
        elif possible_action[action] == _SELECT_RECT:
            print("select some from army") # assume that all units are grouped together
            # find the clusters
            #num_clusters, cluster_sets, clusters, len(units[0])
            #num_clusters, cluster_sets, clusters, total_units = count_group_clusters(obs, _AI_SELF)
            # get half of the clusters
            screen_features = get_units(obs)
            location = get_unit_coors(screen_features, _AI_SELF)
            group1, group2 = group_splitter(location, 1)
            # generate a new group with last known location
            print("___--------------------------------------------------")
            g2_mean = tuple(np.mean(group2, axis = 0))
            g1_mean = tuple(np.mean(group1, axis = 0))
            print(g1_mean)
            newGroup = Group(g2_mean)
            # pop the new group into the queue
            group_queue.append(newGroup)
            # get our group location
            self.prev_location = g1_mean
            self.selected = True
            # return selection

            # get the highest x and y points from our group1
            max_coords = tuple(np.max(group1, axis = 0))
            # get the lowest x and y points from our group1
            min_coords = tuple(np.min(group1, axis = 0))
            func = actions.FunctionCall( _SELECT_RECT, [[0], max_coords, min_coords])
            print("RETT")
            return True, func
        else:
            print("RELEASE CONTROL HERE")
            self.selected = False
            if self.prev_action == _NO_OP: return True, func # this is done to prevent an infinite loop
            else: return False, func #return false because we didn't perfom action
