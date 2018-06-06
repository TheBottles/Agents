import math
import numpy as np
import constants


def get_enemy_coords(obs):
    """ Takes in an observation
        Returns 2d array of x and y coordinates of enemy locations
    """
    ai_view = obs.observation['screen'][constants.AI_RELATIVE]
    return (ai_view == constants.AI_HOSTILE).nonzero()


def get_num_enemies(obs):
    """ Takes in an observation
        Returns number of enemies on the viewable screen
    """
    ai_view = obs.observation['screen'][constants.AI_RELATIVE]
    return np.count_nonzero((ai_view == constants.AI_HOSTILE).nonzero())


def get_map_size(obs):
    """ Takes in an observation
        Returns the size of the map in a tuple
    """
    ai_view = obs.observation['feature_screen'][constants.AI_RELATIVE]
    return np.array(ai_view.shape) - 1


def distance(loc1, loc2):
    """Distance from any point to our goal coordinates"""
    x_distance = math.pow((loc1[0] - loc2[0]), 2)
    y_distance = math.pow((loc1[1] - loc2[1]), 2)
    final = math.sqrt(x_distance + y_distance)
    return final
