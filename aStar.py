import numpy as np
from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features
from pysc2.env import sc2_env, run_loop, available_actions_printer
from pysc2 import maps
from absl import flags
from queue import PriorityQueue #Dan researched

_PLAYER_HOSTILE = 4
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index

#Implemented by Susie, touched up by Dan
def aStar(map, start, goal):
    
    open = PriorityQueue()
    closed = PriorityQueue()
    open.put(0, start) #f(state) = 0
    prev_cost = {}
    prev_cost[start]=0
    path = {}
    path[start] = None
    while not open.empty():
        current = open.get() #pop state with lowest f
        # if current in closed:
        # continue
        
        if current == goal:
            return path[current]
    
        neighbors = {
            (current[0]-1, current[1]+1),
                (current[0], current[1]+1),
                    (current[0]+1, current[1]+1),
                    (current[0]-1, current[1]),
                    (current[0]+1, current[1]),
                    (current[0]-1, current[1]-1),
                    (current[0], current[1]-1),
                    (current[0]+1, current[1]-1)
                }
        
        for next in neighbors:
            new_cost = prev_cost[current] + cost(current, next)
            if next not in prev_cost or new_cost>prev_cost[next]:
                prev_cost[next] = new_cost
                f = new_cost + heuristic(goal, next)
                open.put(f, next)
                path[next] = current




# WORRIED
#implement
def heuristic(a, b):
    #call distance to enemies
    return 1

#implement
def cost(point1, point2):
    
    return 1

#Implemented by Erick
def pathfinding(obs):
    """get the lists of x and y coordinates for the enemy locations"""
    enemy_y_location, enemy_x_location(obs.observation.['minimap'][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
    locations = {}
    '''Create dictionary with x and y location
        for i in range(len(enemy_x_location)):
        
        locations[enemy_x_location[i]] = enemy_y_location[i]
        self_y, self_x(obs.observation.[minimap']
