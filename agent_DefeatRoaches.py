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
from AStar2 import A_Star
from unitselection import *
from qtable import *
from groups import *

np.set_printoptions(threshold=np.nan)


_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_AI_SELECTED = features.SCREEN_FEATURES.selected.index
_NO_OP = actions.FUNCTIONS.no_op.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_RECT = actions.FUNCTIONS.select_rect.id
_CONTROL_GROUP = actions.FUNCTIONS.select_control_group.id
_MOVE_RAND = 1000
_MOVE_MIDDLE = 2000
_BACKGROUND = 0
_AI_SELF = 1
_AI_ALLIES = 2
_AI_NEUTRAL = 3
_AI_HOSTILE = 4
_SELECT_ALL = [0]
_NOT_QUEUED = [0]
_SET_GROUP = [1]
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
    # _SELECT_ARMY,
    # _SELECT_POINT,
    _CONTROL_GROUP,
    _SELECT_RECT,
    _ATTACK_SCREEN,
    # _MOVE_RAND,
    # _MOVE_MIDDLE,
    # _MOVE_SCREEN
]

class FlankingAgent(base_agent.BaseAgent):
    def __init__(self, load_qt=None, load_st=None):
        super(FlankingAgent, self).__init__()
        self.qtable = QTable(possible_action)
        self.steps = 0
        self.groups = []
        self.prev_state = None
        self.prev_action = None


    def step(self, obs):
        '''Step function gets called automatically by pysc2 environment'''
        super(FlankingAgent, self).step(obs)

        if obs.first():
            self.groups = []
            self.groups.append(Group())
            self.groups[0].control_id = 0
            self.group_died = False

        while self.groups:
            # print("WHILE LOOP")
            group = self.groups[0]

            if group.set and obs.observation['control_groups'][group.control_id][0] == 0:
                self.groups.pop(0)
                self.group_died = True
                continue

            active, func = group.do_action(obs, self.qtable, self.groups, self.group_died)

            if not active:
                self.groups.pop(0)
                self.groups.append(group)

            return func

        return actions.FunctionCall(_NO_OP, [])