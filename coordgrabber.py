# Coordinate grabber
import numpy as np
from pysc2.lib import features
from pprint import pprint

_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_AI_HOSTILE = 4
_AI_SELF = 1

def get_enemy_coords(obs):
    """ Takes in an observation
        Returns 2d array of x and y coordinates of enemy locations
    """
    ai_view = obs.observation['screen'][_AI_RELATIVE]
    return (ai_view == _AI_HOSTILE).nonzero()


def get_self_coords(obs):
    """ Takes in an observation
        Returns 2xN numpy array of x and y coordinates of AI (our) locations
    """
    ai_view = obs.observation['screen'][_AI_RELATIVE]
    return (ai_view == _AI_SELF).nonzero()

def get_unit_types(obs, units):
    for each in obs.observation['screen']:
        pprint(each)
    return np.take(obs.observation['screen'][_UNIT_TYPE],units)

def get_num_enemies(obs):
    """ Takes in an observation
        Returns number of enemies on the viewable screen
    """
    ai_view = obs.observation['screen'][_AI_RELATIVE]
    return np.count_nonzero((ai_view == _AI_HOSTILE).nonzero())

def get_map_size(obs):
    """ Takes in an observation
        Returns the size of the map in a tuple
    """
    ai_view = obs.observation['screen'][_AI_RELATIVE]
    return ai_view.shape
