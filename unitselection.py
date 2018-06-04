# Format followed from https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3

import numpy as np
import scipy.cluster.hierarchy as hcluster

from constants import AI_SELF


def get_units(obs):
    """ takes in an observation and returns the units as an array """
    return obs.observation['feature_units']


def get_alliance_units(units, alliance):
    """
        get_alliance_units takes in an array of feature units and the alliance number
        and returns the units which have the target alliance.
    """
    return [unit for unit in units if unit[1] == alliance]


def gen_coordinates(units):
    """ takes in an array of units and returns a 2xn array of coordinates"""

    coors = [[], []]
    for unit in units:
        coors[0].append(unit[12])
        coors[1].append(unit[13])
    return np.array(coors)


def get_unit_coors(units, alliance):
    """ shortcut for getting unit coordinates of an alliance """

    return gen_coordinates(get_alliance_units(units, alliance))


def count_group_clusters(obs, who=AI_SELF):
    """ Defines clusters within a map relative to the AI """

    units = get_unit_coors(get_units(obs), who)
    if np.any(units[0]):
        thresh = 10  # this should translate to 10 pixels
        clusters = hcluster.fclusterdata(units.T, thresh, criterion='distance')
        cluster_sets = set(clusters)
        num_clusters = len(set(clusters))
        return num_clusters, cluster_sets, clusters, len(units[0])
    else:
        return 0, 0, 0, 0


def group_splitter(cluster, axis=0):
    """ Splits a cluster into two, either vertically or horizontally """

    group1 = []
    group2 = []
    horizontal_split = cluster[axis].mean()
    for point in enumerate(zip(cluster[0], cluster[1])):
        if point[1][axis] < horizontal_split:
            group1.append(point[1])
        else:
            group2.append(point[1])
    return group1, group2
