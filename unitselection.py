# Format followed from https://itnext.io/how-to-locate-and-select-units-in-pysc2-2bb1c81f2ad3

# from sklearn.cluster import KMeans
import numpy as np
import scipy.cluster.hierarchy as hcluster
from pysc2.lib import features

_AI_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index
_AI_HOSTILE = 4
_AI_SELF = 1

# def count_num_units(obs, unit_type):
#     unit_graph = obs.observation['screen'][_UNIT_TYPE]
#     unit_x, unit_y = (unit_graph == unit_type).nonzero()
#
#     units = []
#
#     num_pixels = len(unit_y)
#     for i in range(0, num_pixels):
#         units.append((unit_x[i], unit_y[i]))
#
#     unit_pixels = 1 # this should the the pixel coverage per unit
#
#     kmeans = KMeans(n_clusters = num_pixels / unit_pixels)

""" takes in an observation and returns the units as an array """
def get_units(obs):
    print(obs.observation['feature_units'][0])
    return obs.observation['feature_units']

"""
    get_alliance_units takes in an array of feature units and the alliance number
    and returns the units which have the target alliance.
"""
def get_alliance_units(units, alliance):
    return [ unit for unit in units if unit[1] == alliance]

""" takes in an array of units and returns a 2xn array of coordinates"""
def gen_coorinates(units):
    coors = [[],[]]
    for unit in units:
        coors[0].append(unit[12])
        coors[1].append(unit[13])
    return np.array(coors)


""" shortcut for getting unit coordinates of an alliance """
def get_unit_coors(units, alliance):
    return gen_coordinates(get_alliance_units(units, alliance))


# """ Defines clusters within a map relative to the AI """
# def count_group_clusters(obs, who = _AI_SELF):
#     unit_graph = obs.observation['screen'][_AI_RELATIVE]
#     units = np.array((unit_graph == who).nonzero())
#     if np.any(units[0]):
#         thresh = 10 # this should translate to 10 pixels
#         clusters = hcluster.fclusterdata(units.T, thresh, criterion = 'distance')
#         cluster_sets = set(clusters)
#         num_clusters = len(set(clusters))
#         return num_clusters, cluster_sets, clusters, len(units[0])
#     else:
#         return 0, 0, 0, 0
#
# """ Splits a cluster into two, either vertically or horizontally """
# def group_splitter(cluster, axis = 0):
#     group1 = []
#     group2 = []
#     horizontal_split = cluster[axis].mean()
#     for point in cluster:
#         if point[axis] < horizontal_split: group1.append(point)
#         else: group2.append(point)
#     return group1, group2
