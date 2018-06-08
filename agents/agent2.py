import numpy as np
from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.env import sc2_env, run_loop, available_actions_printer
from pysc2 import maps
from absl import flags

import unitselection
import constants

_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_NO_OP = actions.FUNCTIONS.no_op.id
_MOVE_SCREEN = actions.FUNCTIONS.Attack_screen.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_BACKGROUND = 0
_AI_SELF = 1
_AI_ALLIES = 2
_AI_NEUTRAL = 3
_AI_HOSTILE = 4
_SELECT_ALL = [0]
_NOT_QUEUED = [0]

def get_target(ai_relative_view):
    '''returns the location indices of the beacon on the map'''
    return (ai_relative_view == _AI_HOSTILE).nonzero()

wins = 0
loss = 0
prev_enemies = 0

class Agent2(base_agent.BaseAgent):
    """An agent for doing a simple movement form one point to another."""

    wins = 0
    loss = 0
    prev_enemies = 0


    def step(self, obs):

        units = unitselection.get_units(obs)
        enemy_units = len(unitselection.get_alliance_units(units, constants.AI_HOSTILE))
        ai_units = len(unitselection.get_alliance_units(units, constants.AI_SELF))

        if enemy_units > Agent2.prev_enemies:
            Agent2.wins += 1
            print()
        elif ai_units == 0:
            Agent2.loss += 1

        Agent2.prev_enemies = enemy_units

        if Agent2.wins + Agent2.loss == 300:
            if Agent2.wins + Agent2.loss > 0:
                print("%.2f%% percent win rate" % (Agent2.wins/ (Agent2.wins + Agent2.loss) * 100))
            print("Wins: %d, Loss: %d" % (Agent2.wins, Agent2.loss))
            raise KeyboardInterrupt



        if obs.last():
            prev_enemies = np.infty
            if Agent2.wins + Agent2.loss > 0:
                print("%.2f%% percent win rate" % (Agent2.wins/ (Agent2.wins + Agent2.loss) * 100))

            print("Wins: %d, Loss: %d" % (Agent2.wins, Agent2.loss))

        '''Step function gets called automatically by pysc2 environment'''
        super(Agent2, self).step(obs)
        if _MOVE_SCREEN in obs.observation['available_actions']:
            ai_view = obs.observation['feature_screen'][_AI_RELATIVE]
            # get the beacon coordinates
            beacon_xs, beacon_ys = get_target(ai_view)
            if not beacon_ys.any():
                return actions.FunctionCall(_NO_OP, [])
            # get the middle of the beacon and move there
            target = [beacon_ys.mean(), beacon_xs.mean()]
            return actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, target])
        else:
            return actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
