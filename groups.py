from pysc2.lib import actions
import numpy as np

from constants import _SELECT_UNITS, _SET_CONTROL, _SELECT_CONTROL, _MOVE_TO_TARGET, _FLANK_TARGET, _ATTACK_TARGET, _NO_OP
from constants import possible_action, moves
from constants import  _SELECT_ALL, _NOT_QUEUED, _SET_GROUP, _AI_SELF, _AI_HOSTILE, _QUEUED
from constants import _SELECT_RECT_ID, _CONTROL_GROUP_ID,_MOVE_SCREEN_ID, _ATTACK_SCREEN_ID, _NO_OP_ID
from constants import THRESH
from coordgrabber import Distance_Calc
import state_machine
import unitselection
from AStar2 import A_Star, arc_position

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

        self.prev_state         = None
        self.prev_action        = None
        self.prev_location      = location

        self.flanker            = False
        self.id                 = None
        self.in_position        = False
        self.initial_unit_coors = unit_locations
        self.selected           = False
        self.set                = False
        self.moving             = False
        self.target             = None

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

    def do_action(self, obs, score, group_queue, steps):

        all_units = unitselection.get_units(obs)


        target, radius = generate_target(obs, self)
        position = tuple(unitselection.get_unit_coors(all_units, _AI_SELF).mean(axis = 1))

        if Distance_Calc(target, position) < radius:
            self.in_position = True
        else:
            self.in_position = False

        if self.target == position:
            self.moving = False
        elif position is not self.prev_location:
            self.moving = True

        state = state_machine.get_state(obs, self, group_queue)
        action_key = self.qtable.get_action(state, steps)
        action = possible_action[action_key]

        if not obs.last() and not obs.first():
            self.qtable.update_qtable(
                self.prev_state, state, self.prev_action, score)

        while moves[action] not in obs.observation['available_actions']:
            self.qtable.bad_action(state, action_key)
            action_key = self.qtable.get_action(state, steps)
            action = possible_action[action_key]

        active = False
        func = actions.FunctionCall(_NO_OP, [])

        # print(state, action)

        if action == _SELECT_UNITS:
            """ Select half of our AI units and split groups """

            if self.set or state[1] or self.selected:
                self.qtable.bad_action(state, action_key)
                return active, func

            # Locate our AI units
            location = unitselection.get_unit_coors(all_units, _AI_SELF)
            # print(location)

            # Divide units
            group1, group2 = unitselection.group_splitter(location, 1)
            # print(group1)
            # print(group2)

            if len(group1) > 0 and len(group2) > 0:

                # generate a new group with last known location
                g2_mean = tuple(np.mean(group2, axis=0))
                g1_mean = tuple(np.mean(group1, axis=0))
                # print(g1_mean)

                newGroup = Group(g2_mean, group2)
                newGroup.flanker = True

                # enqueue  the new group into the queue
                group_queue.append(newGroup)
                # get our group location
                self.prev_location = g1_mean

                deselect(group_queue)
                self.selected = True
                # return selection

                # get the highest x and y points from group1
                max_coords = tuple(np.max(group1, axis=0))
                # get the lowest x and y points from group1
                min_coords = tuple(np.min(group1, axis=0))

                func = actions.FunctionCall(
                    _SELECT_RECT_ID, [_SELECT_ALL, max_coords, min_coords])
                active = True


        elif action == _SET_CONTROL:
            """ Set the currently selected units as a control group """

            if self.set or not self.selected or not state[1]:
                self.qtable.bad_action(state, action_key)
                return active, func

            self.set = True
            self.id = get_next_id(obs)
            func = actions.FunctionCall(
                _CONTROL_GROUP_ID, [_SET_GROUP, [self.id]])
            active = True


        elif action == _SELECT_CONTROL:
            """ Select the control group belonging to this group """

            if (self.selected and self.set) or (not self.set and not self.initial_unit_coors):
                self.qtable.bad_action(state, action_key)
                return active, func


            deselect(group_queue)
            self.selected = True


            if self.set:
                func = actions.FunctionCall(
                    _CONTROL_GROUP_ID, [_SELECT_ALL, [self.id]])
                active = True
            else:
                max_coords = tuple(np.max(self.initial_unit_coors, axis=0))
                # get the lowest x and y points from our group1
                min_coords = tuple(np.min(self.initial_unit_coors, axis=0))
                func = actions.FunctionCall(
                    _SELECT_RECT_ID, [_SELECT_ALL, max_coords, min_coords])
                active = True


        elif action == _MOVE_TO_TARGET:
            """ Use A* to move toward the direction of a target """

            if not self.set or not self.selected or not state[1]:
                self.qtable.bad_action(state, action_key)
                return active, func

            next_pos = A_Star(obs, position, target)
            active = True
            func = actions.FunctionCall(_MOVE_SCREEN_ID, [_QUEUED, next_pos])

            if next_pos == target:
                active = False
            self.moving = True
            self.target = target


        elif action == _FLANK_TARGET:
            """ Use dubin's path to flank an enemy grouping """

            if not self.flanker or not self.set or not self.selected or not self.in_position or not state[1]:
                self.qtable.bad_action(state, action_key)
                return active, func

            next_pos = arc_position(group_queue[1].prev_location, position, target, radius, THRESH)
            active = True
            func = actions.FunctionCall(_ATTACK_SCREEN_ID, [_QUEUED, next_pos])

            if next_pos == target:
                active = False
            self.moving = True
            self.target = target


        elif action == _ATTACK_TARGET:
            """ Attack the enemy by going in a stright line """

            if not self.set or not self.selected or not self.in_position:
                self.qtable.bad_action(state, action_key)
                return active, func
            next_pos = A_Star(obs, position, target)
            active = False
            func = actions.FunctionCall(_ATTACK_SCREEN_ID, [_QUEUED, next_pos])
            self.moving = True
            self.target = target


        elif action == _NO_OP:
            """ Wait for the other groups """

            teams_ready = True              # Are the other teams ready?
            for group in group_queue:        # First group is this_group, do not check
                if not group.in_position:
                    teams_ready = False
                    break

            if teams_ready or not self.in_position:
                self.qtable.bad_action(state, action_key)

            return False, func

        self.prev_state = state
        self.prev_location = position
        self.prev_action = action_key

        # print(active, func)

        return active, func

def generate_target(obs, group, thresh = THRESH):
    # Todo: handle case when there are no enemy coordiantes
    screen_features = unitselection.get_units(obs)
    targetxs, targetys = unitselection.get_unit_coors(screen_features, _AI_HOSTILE)

    if not targetxs.size:
        map = coordgrabber.get_map_size(obs)
        return (randint(0,map[0]), randint(0,map[1]))

    selfxs, selfys = unitselection.get_unit_coors(screen_features, _AI_SELF)
    selfx = selfxs.mean()
    selfy = selfys.mean()
    loc = (selfx, selfy)

    xmax = np.argmax(targetxs)
    xmin = np.argmin(targetxs)
    ymax = np.argmax(targetys)
    ymin = np.argmin(targetys)

    labely = (targetys[ymax] - targetys[ymin])
    labelx = (targetxs[xmax] - targetxs[xmin])

    if labelx > labely:
        # Our group units are closer to the top of the enemy units
        if Distance_Calc(loc, (targetxs[ymin], targetys[ymin])) < Distance_Calc(loc, (targetxs[ymax], targetys[ymax])):
            target = targetxs[ymin], targetys[ymin]
        # Our group units are closer to the bottom of the enemy units
        else: target =  targetxs[ymax], targetys[ymax]
    else:
        # Our group units are closer to the left of the enemy units
        if Distance_Calc(loc, (targetxs[xmin], targetys[xmin])) < Distance_Calc(loc, (targetxs[xmax], targetys[xmax])):
            target =  targetxs[xmin], targetys[xmin]
        # Our group units are closer to the right of the enemy units
        else: target =  targetxs[xmax], targetys[xmax]

    distances_from_center = []
    for enemy in zip(targetxs, targetys):
        distances_from_center.append(Distance_Calc(target, enemy))

    return target, (np.argmax(distances_from_center) + thresh)
