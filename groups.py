from random import randint
from pysc2.lib import actions
import numpy as np

import constants
import coordgrabber
import state_machine
import unitselection
import pathfinder


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

        self.flanker = False
        self.id = None
        self.in_position = False
        self.initial_unit_coors = unit_locations
        self.selected = False
        self.set = False
        self.moving = False
        self.target = None

        self.moves = []

        self.bad = True

        if self.flanker:
            self.tablename = "flankerQTable.npy"
            self.statename = "flankerQState.npy"
        else:
            self.tablename = "qTable.npy"
            self.statename = "qState.npy"

        try:
            self.qtable = state_machine.ModifiedQTable(
                constants.possible_action, load_qt=self.tablename, load_st=self.statename)
        except FileNotFoundError:
            self.qtable = state_machine.ModifiedQTable(constants.possible_action)

    def apply_rewards(self, reward):
        if reward == 0: reward = -1
        for i in range(len(self.moves) - 1):
            prev_state = self.moves[i][0]
            next_state = self.moves[i + 1][0]
            action = self.moves[i][1]
            # print(prev_state, next_state, action)
            self.qtable.update_qtable(
                prev_state, next_state, action, reward)

    def update_tables(self):
        self.qtable.save_qtable(self.tablename)
        self.qtable.save_states(self.statename)

    def do_action(self, obs, group_queue, steps, multigroup):

        all_units = unitselection.get_units(obs)

        if self.selected:
            position = tuple(unitselection.get_selected_coors(obs).mean(axis=1).round().astype(int))
        elif self.prev_location:
            position = self.prev_location
        elif self.initial_unit_coors:
            position = self.initial_unit_coors.mean(axis=1).round().astype(int)
        else:
            position = tuple(
                unitselection.get_unit_coors(all_units, constants.AI_SELF).mean(axis=1).round().astype(int))

        if self.target == position:
            self.moving = False
        elif position is not self.prev_location:
            self.moving = True

        target, radius = generate_target(obs, position)

        if coordgrabber.distance(target, position) < radius:
            self.in_position = True
        else:
            self.in_position = False

        state = state_machine.get_state(obs, self, group_queue, multigroup)
        action_key = self.qtable.get_action(state, steps)
        action = constants.possible_action[action_key]

        while constants.moves[action] not in obs.observation['available_actions'] or not valid(state, action):
            self.qtable.bad_action(state, action_key)
            print("      --", "%4s" % self.id , "%4d" % action, state)
            action_key = self.qtable.get_action(state, steps)
            action = constants.possible_action[action_key]

        active = False
        func = actions.FunctionCall(constants.NO_OP, [])

        print("VALID --", "%4s" % self.id, "%4d" % action, state)

        if action == constants.SPLIT_UNITS:
            # Locate our AI units
            location = unitselection.get_unit_coors(all_units, constants.AI_SELF)
            # print(location)

            # Divide units
            group1, group2 = unitselection.group_splitter(location, 1)

            if len(group1) > 0 and len(group2) > 0:
                # print(group1)
                # print(group2)

                # generate a new group with last known location
                g2_mean = tuple(np.mean(group2, axis=0).round())
                g1_mean = tuple(np.mean(group1, axis=0).round())
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
                    constants.SELECT_RECT_ID, [constants.SELECT_ALL, max_coords, min_coords])
                active = True

        elif action == constants.SELECT_UNITS:
            """ Select half of our AI units and split groups """
            deselect(group_queue)
            self.selected = True
            # return selection

            # get the highest x and y points from group1
            max_coords = tuple(np.max(self.initial_unit_coors, axis=0))
            # get the lowest x and y points from group1
            min_coords = tuple(np.min(self.initial_unit_coors, axis=0))

            func = actions.FunctionCall(
                constants.SELECT_RECT_ID, [constants.SELECT_ALL, max_coords, min_coords])
            active = True

        elif action == constants.SET_CONTROL:
            """ Set the currently selected units as a control group """

            self.set = True
            self.id = get_next_id(obs)
            func = actions.FunctionCall(
                constants.CONTROL_GROUP_ID, [constants.SET_GROUP, [self.id]])
            active = False

        elif action == constants.SELECT_CONTROL:
            """ Select the control group belonging to this group """

            deselect(group_queue)
            self.selected = True

            if state.set:
                func = actions.FunctionCall(
                    constants.CONTROL_GROUP_ID, [constants.SELECT_ALL, [self.id]])
            else:
                max_coords = tuple(np.max(self.initial_unit_coors, axis=0))
                # get the lowest x and y points from our group1
                min_coords = tuple(np.min(self.initial_unit_coors, axis=0))
                func = actions.FunctionCall(
                    constants.SELECT_RECT_ID, [constants.SELECT_ALL, max_coords, min_coords])
            active = True

        elif action == constants.MOVE_TO_TARGET:
            """ Use A* to move toward the direction of a target """

            next_pos = pathfinder.a_star(obs, position, target)

            if coordgrabber.distance(next_pos, target) < radius:
                self.in_position = True

            self.moving = True
            self.target = target

            active = False
            func = actions.FunctionCall(constants.MOVE_SCREEN_ID, [constants.NOT_QUEUED, next_pos])

        elif action == constants.FLANK_TARGET:
            """ Use dubin's path to flank an enemy grouping """

            next_pos = pathfinder.arc_position(group_queue[1].prev_location, position, target, radius, constants.THRESH)

            next_pos = (min(next_pos[0], 83), min(next_pos[1], 83))
            next_pos = (max(next_pos[0], 0), max(next_pos[1], 0))

            if next_pos == target:
                self.in_position = True

            self.moving = True
            self.target = target

            active = False
            func = actions.FunctionCall(constants.ATTACK_SCREEN_ID, [constants.NOT_QUEUED, next_pos])

        elif action == constants.ATTACK_TARGET:
            """ Attack the enemy by going in a straight line """

            next_pos = pathfinder.a_star(obs, position, target)

            self.moving = True
            self.target = target

            active = False
            func = actions.FunctionCall(constants.ATTACK_SCREEN_ID, [constants.NOT_QUEUED, next_pos])

        elif action == constants.NO_OP:
            """ Wait for the other groups """
            active = False

        self.prev_state = state
        self.prev_location = position
        self.prev_action = action_key

        # print(active, func)

        self.moves.append([state, action_key])
        # print(state, func, action)
        return active, func


def generate_target(obs, position, thresh=constants.THRESH):
    # Todo: handle case when there are no enemy coordiantes
    screen_features = unitselection.get_units(obs)
    target_xs, target_ys = unitselection.get_unit_coors(screen_features, constants.AI_HOSTILE)

    if not target_xs.size:
        map = coordgrabber.get_map_size(obs)
        return randint(0, map[0]), randint(0, map[1])

    x_max = np.argmax(target_xs)
    x_min = np.argmin(target_xs)
    y_max = np.argmax(target_ys)
    y_min = np.argmin(target_ys)

    label_y = (target_ys[y_max] - target_ys[y_min])
    label_x = (target_xs[x_max] - target_xs[x_min])

    if not position:
        target = target_xs.mean(), target_ys.mean()
    elif label_x > label_y:
        # Our group units are closer to the top of the enemy units
        if coordgrabber.distance(position, (target_xs[y_min], target_ys[y_min])) < coordgrabber.distance(position, (
                target_xs[y_max], target_ys[y_max])):
            target = target_xs[y_min], target_ys[y_min]
        # Our group units are closer to the bottom of the enemy units
        else:
            target = target_xs[y_max], target_ys[y_max]
    else:
        # Our group units are closer to the left of the enemy units
        if coordgrabber.distance(position, (target_xs[x_min], target_ys[x_min])) < coordgrabber.distance(position, (
                target_xs[x_max], target_ys[x_max])):
            target = target_xs[x_min], target_ys[x_min]
        # Our group units are closer to the right of the enemy units
        else:
            target = target_xs[x_max], target_ys[x_max]

    distances_from_center = []
    for enemy in zip(target_xs, target_ys):
        distances_from_center.append(coordgrabber.distance(target, enemy))

    return target, (np.argmax(distances_from_center) + thresh)


def valid(state, action):
    if (action == constants.SPLIT_UNITS) and (
            state.set or state.selected or state.multigroup or state.init or state.split):
        return False

    elif (action == constants.SELECT_UNITS) and (state.set or state.selected or state.multigroup or not state.init):
        return False

    elif (action == constants.SET_CONTROL) and (state.set or not state.selected or not state.split):
        return False

    elif (action == constants.SELECT_CONTROL) and (state.selected or not state.set):
        return False

    elif (action == constants.NO_OP) and state.groups_ready:
        return False

    elif (action == constants.ATTACK_TARGET) and not (state.set and state.selected and state.multigroup):
        return False

    elif (action == constants.FLANK_TARGET) and not (
            state.split and state.flanking and state.set and state.selected and state.multigroup):
        return False

    elif (action == constants.MOVE_TO_TARGET) and not (state.set and state.selected and state.multigroup):
        return False

    return True
