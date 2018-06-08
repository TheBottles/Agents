from pysc2.agents import base_agent

from constants import NO_OP_ID, AI_SELF
from groups import *
import unitselection
import time

import os

def get_unit_health(obs, unit_type):
    unit_hp = obs.observation['feature_units']
    total_hp = 0
    for unit in unit_hp:
        if unit[1] == unit_type:
            total_hp = total_hp + unit[2]
    return total_hp


class FlankingAgent(base_agent.BaseAgent):
    def __init__(self):
        super(FlankingAgent, self).__init__()
        self.steps = 0
        self.groups = []
        self.prev_state = None
        self.prev_action = None
        self.score = 0
        self.multigroup = False

        self.reward = 0
        self.wins = 0
        self.loss = 0
        self.reward = 0

        self.refresh()

    def refresh(self):
        self.groups = []
        self.groups.append(Group())
        self.groups[0].control_id = 0
        self.multigroup = False
        self.prev_enemies = 0

    def step(self, obs):

        '''Step function gets called automatically by pysc2 environment'''
        super(FlankingAgent, self).step(obs)

        units = unitselection.get_units(obs)
        enemy_units = len(unitselection.get_alliance_units(units, constants.AI_HOSTILE))
        ai_units = len(unitselection.get_alliance_units(units, constants.AI_SELF))

        if enemy_units > self.prev_enemies:
            self.wins += 1
            print()
        elif ai_units == 0:
            self.loss += 1

        self.prev_enemies = enemy_units

        self.steps += 1

        if obs.last():
            self.prev_enemies = np.infty
            # os.system('clear')
            relative_score = obs.observation['score_cumulative'][0] + (obs.reward * 10)
            for sub_agent in self.groups:
                sub_agent.apply_rewards(relative_score)
                sub_agent.update_tables()
            print(obs.observation['score_cumulative'][0] + obs.reward *10, "\n")

            if self.wins + self.loss > 0:
                print("%.2f%% percent win rate" % (self.wins/ (self.wins + self.loss) * 100))

            print("Wins: %d, Loss: %d" % (self.wins, self.loss))



        # print("cumulative", obs.observation['score_cumulative'])

        if not self.multigroup and len(self.groups) > 1:
            if all([group.set for group in self.groups]):
                self.multigroup = True

        elif self.multigroup and all(not units[1] for units in obs.observation['control_groups']):
            self.refresh()

        while self.groups:
            # print("WHILE LOOP")

            # hostile_health = self.get_unit_health(obs, _AI_HOSTILE)
            # ai_health = self.get_unit_health(obs, _AI_SELF)
            # step_score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])- self.score - (2 * hostile_health) + ai_health
            # self.score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])

            group = self.groups[0]


            if group.set and obs.observation['control_groups'][group.id][0] == 0:
                self.groups.pop(0)
                group.group_died = True
                continue

            active, func = group.do_action(obs, self.groups, self.steps, self.multigroup)

            if not active:
                self.groups.pop(0)
                self.groups.append(group)

            # print("        ",[group.id for group in self.groups])
            return func

        self.groups.append(Group())
        self.groups[0].control_id = 0

        return actions.FunctionCall(NO_OP_ID, [])
