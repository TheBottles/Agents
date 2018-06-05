from pysc2.agents import base_agent

from constants import NO_OP_ID
from groups import *


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

    def step(self, obs):

        '''Step function gets called automatically by pysc2 environment'''
        super(FlankingAgent, self).step(obs)

        # print(obs.observation['control_groups'])

        self.steps += 1

        if obs.last():
            for subagent in self.groups:
                subagent.apply_rewards(obs.reward)
                subagent.update_tables()
            print(obs.reward)
            self.groups = []
            self.groups.append(Group())
            self.groups[0].control_id = 0

        while self.groups:
            # print("WHILE LOOP")

            # hostile_health = self.get_unit_health(obs, _AI_HOSTILE)
            # ai_health = self.get_unit_health(obs, _AI_SELF)
            # step_score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])- self.score - (2 * hostile_health) + ai_health
            # self.score = (obs.observation['score_cumulative'][3]+obs.observation['score_cumulative'][5])

            if len(self.groups) > 1:
                self.multigroup = True
            group = self.groups[0]
            if group.set and obs.observation['control_groups'][group.id][0] == 0:
                self.groups.pop(0)
                group.group_died = True
                continue

            active, func = group.do_action(obs, self.groups, self.steps, self.multigroup)

            if not active:
                self.groups.pop(0)
                self.groups.append(group)

            return func

        self.groups.append(Group())
        self.groups[0].control_id = 0

        return actions.FunctionCall(NO_OP_ID, [])
