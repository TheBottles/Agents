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
from pathfinder import a_star, arc_position


from unitselection import *
from constants import *
import state_machine


def get_next_id(obs):
    groups = obs.observation['control_groups']
    # pprint(groups)
    for i in range(len(groups)):
        if not groups[i][1]:
            return i
    return -1


def deselect(group_queue):
    for group in group_queue:
        group.selected = False


class Group():

    def __init__(self, location=None, unit_locations=None):

        self.prev_state = None
        self.prev_action = None
        self.prev_location = location

        self.control_id = None
        self.set = False
        self.selected = False
        self.flanker = False

        self.bad = True

        if self.flanker:
            self.tablename = "flankerQTable.npy"
            self.statename = "flankerQState.npy"
        else:
            self.tablename = "qTable.npy"
            self.statename = "qState.npy"

        try:
            self.qtable = state_machine.ModifiedQTable(
                possible_action, load_qt=self.tablename, load_st=self.statename)
        except FileNotFoundError:
            self.qtable = QTable(possible_action)

    def update_tables(self):
        self.qtable.save_qtable(self.tablename)
        self.qtable.save_states(self.statename)

    def do_action(self, obs, score, group_queue):

        state, target_pos, current_pos = get_state(
            obs, self.selected, self.set, self.flanker, group_queue)

        self.prev_state = state
        action = self.qtable.get_action(state)
        self.prev_action = action
        self.prev_location = current_pos
        self.moving = state[1]
        func = actions.FunctionCall(_NO_OP, [])
        units = get_units(obs)

        # print(action)
        # print(score)

        if self.set and obs.observation['control_groups'][self.control_id][0] == 0:
            self.group_died = True

        if self.group_died:
            return False, func

        if not obs.last():
            score_sum = score
            if self.bad:
                score_sum -= 1000
            self.qtable.update_qtable(
                self.prev_state, state, self.prev_action, score)

        self.bad = False



        if not possible_action[action] == _FLANK_ENEMY and possible_action[action] not in obs.observation['available_actions']:
            # print(action)
            print("Cannot perform", possible_action[action].name, "right now")
            pass
        elif possible_action[action] == _FLANK_ENEMY and _MOVE_SCREEN not in obs.observation['available_actions']:
            print("Cannot perform flank right now")
            pass
        elif possible_action[action] == _CONTROL_GROUP:
            print("Controlling group", self.control_id)

            if not self.selected and not self.set:
                print("    Select unset units")
                if not self.initial_unit_coors:
                    print("        Cannot initialize units from null list")
                    pass
                else:
                    max_coords = tuple(np.max(self.initial_unit_coors, axis=0))
                    # get the lowest x and y points from our group1
                    min_coords = tuple(np.min(self.initial_unit_coors, axis=0))
                    func = actions.FunctionCall(
                        _SELECT_RECT, [_SELECT_ALL, max_coords, min_coords])
                    deselect(group_queue)
                    self.selected = True
                    return True, func

            elif self.selected and not self.set:
                print("    Set control group")
                self.control_id = get_next_id(obs)
                func = actions.FunctionCall(
                    _CONTROL_GROUP, [_SET_GROUP, [self.control_id]])
                self.set = True
                return True, func

            elif self.set and not self.selected:
                print("    Select control group")
                func = actions.FunctionCall(
                    _CONTROL_GROUP, [_SELECT_ALL, [self.control_id]])
                deselect(group_queue)
                self.selected = True
                return True, func

            else:
                print(
                    "    Units set and selected, but trying to control group, need to move or attack instead")

        elif possible_action[action] == _FLANK_ENEMY:
            print("Attempting to flank")
            units = get_units(obs)
            enemy_pos= get_unit_coors(units, _AI_HOSTILE).mean(axis = 1)

            assert(len(enemy_pos) == 2)

            if not self.flanker:
                print(self.control_id, "is not the flanking group")
                pass
            elif distance(enemy_pos, self.prev_location) > 15:
                print(self.control_id, "is too far to flank")
                pass

            elif group_queue <= 1:
                print(self.control_id, "not enough units to flank")
                pass
            else:
                headon_pos = group_queue[1].prev_location
                waypoint_x, waypoint_y = arc_position(
                    headon_pos, self.prev_location, enemy_pos, 15, 5)

                func = actions.FunctionCall(_MOVE_SCREEN, [_NOT_QUEUED, [waypoint_, waypoint_y]])
                return False, func

        elif possible_action[action] == _ATTACK_SCREEN:
            print("Attempting to move or attack")
            if self.selected:
                # assume units are already selected here
                print("    DO A* AND ATTACK")
                target_x, target_y = a_star(obs, current_pos, target_pos)
                # target_x, target_y = target_pos

                if (target_x, target_y) == target_pos:
                    TYPE_MOVE = _ATTACK_SCREEN
                    active = False
                else:
                    TYPE_MOVE = _MOVE_SCREEN
                    active = True

                func = actions.FunctionCall(
                    TYPE_MOVE, [_NOT_QUEUED, [target_x, target_y]])
                return active, func
            else:
                print("    Units were not selected!")

        elif state[3] and possible_action[action] == _SELECT_ARMY:
            print("Select entire army")
            func = actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
            deselect(group_queue)
            self.selected = True
            return True, func

        elif len(group_queue) < 2 and not state[3] and possible_action[action] == _SELECT_RECT:
            # assume that all units are grouped together
            print("Select some units from army")
            # find the clusters
            #num_clusters, cluster_sets, clusters, len(units[0])
            #num_clusters, cluster_sets, clusters, total_units = count_group_clusters(obs, _AI_SELF)
            # get half of the clusters
            screen_features = get_units(obs)
            location = get_unit_coors(screen_features, _AI_SELF)
            group1, group2 = group_splitter(location, 1)

            if len(group1) > 0 and len(group2) > 0:
                # generate a new group with last known location
                # print("--------------------------------------------------")
                g2_mean = tuple(np.mean(group2, axis=0))
                g1_mean = tuple(np.mean(group1, axis=0))
                print(g1_mean)

                newGroup = Group(g2_mean, group2)
                newGroup.Flanker = True
                # pop the new group into the queue
                group_queue.append(newGroup)
                # get our group location
                self.prev_location = g1_mean
                self.selected = True
                self.initial_unit_coors = group1
                # return selection

                # get the highest x and y points from our group1
                max_coords = tuple(np.max(group1, axis=0))
                # get the lowest x and y points from our group1
                min_coords = tuple(np.min(group1, axis=0))
                func = actions.FunctionCall(
                    _SELECT_RECT, [_SELECT_ALL, max_coords, min_coords])
                return True, func

        print("Releasing Control")
        self.bad = True
        self.selected = False
        if self.prev_action == _NO_OP:
            return True, func  # this is done to prevent an infinite loop
        else:
            return False, func  # return false because we didn't perfom action
