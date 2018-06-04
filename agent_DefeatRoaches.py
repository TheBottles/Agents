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
from groups import *

np.set_printoptions(threshold=np.nan)


from constants import _AI_HOSTILE, _NO_OP_ID, _AI_SELF

class FlankingAgent(base_agent.BaseAgent):
    def __init__(self, load_qt=None, load_st=None):
        super(FlankingAgent, self).__init__()
        self.steps = 0
        self.groups = []
        self.prev_state = None
        self.prev_action = None
        self.score = 0

    def get_unit_health(self, obs, type):
   		unit_hp = obs.observation['feature_units']
   		total_hp = 0
   		for unit in unit_hp:
   			if(unit[1] == type):
   				total_hp = total_hp+unit[2]
   		return total_hp

    def step(self, obs):

        '''Step function gets called automatically by pysc2 environment'''
        super(FlankingAgent, self).step(obs)

        # print(obs.observation['control_groups'])

        self.steps += 1

        if obs.first():
            self.groups = []
            self.groups.append(Group())
            self.groups[0].control_id = 0
        elif obs.last():
            for subagent in self.groups:
                subagent.update_tables()

        while self.groups:
            # print("WHILE LOOP")
            hostile_health = self.get_unit_health(obs, _AI_HOSTILE)
            ai_health = self.get_unit_health(obs, _AI_SELF)

            step_score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])- self.score - (2 * hostile_health) + ai_health
            self.score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])

            group = self.groups[0]

            if group.set and obs.observation['control_groups'][group.id][0] == 0:
                self.groups.pop(0)
                group.group_died = True
                continue

            active, func = group.do_action(obs, step_score, self.groups, self.steps)

            if not active:
                self.groups.pop(0)
                self.groups.append(group)

            return func

        self.groups.append(Group())
        self.groups[0].control_id = 0

        return actions.FunctionCall(_NO_OP_ID, [])
