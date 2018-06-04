import math
import numpy as np

import constants
import unitselection


def get_state(obs, this_group, groups):
    # State information about the state of the game
    all_units = unitselection.get_units(obs)
    hostile_present = len(unitselection.get_alliance_units(all_units, constants.AI_HOSTILE)) > 0

    # State information about all groups
    multigroup = len(groups) > 1
    teams_ready = True  # Are the other teams ready?
    for group in groups[1:]:  # First group is this_group, do not check
        if not group.in_position:
            teams_ready = False
            break

    # State information about this particular group
    flanker = this_group.flanker
    ready = this_group.in_position
    selected = this_group.selected
    set = this_group.set
    initialized = bool(this_group.initial_unit_coors)

    state = tuple((hostile_present, multigroup, initialized, teams_ready, flanker, ready, selected, set))

    return state


""" The code below is sourced from pysc2 agent3.py """

EPS_START = 0.9
EPS_END = 0.025
EPS_DECAY = 2500


def get_eps_threshold(steps_done):
    return EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)


class QTable(object):
    def __init__(self, actions, lr=0.01, reward_decay=0.9, load_qt=None, load_st=None):
        self.lr = lr
        self.actions = actions
        self.reward_decay = reward_decay
        self.states_list = set()
        self.load_qt = load_qt
        if load_st:
            temp = self.load_states(load_st)
            self.states_list = set([tuple(temp[i]) for i in range(len(temp))])

        if load_qt:
            self.q_table = self.load_qtable(load_qt)
        else:
            self.q_table = np.zeros(
                (3, len(constants.possible_action)))  # create a Q table

    def get_action(self, state, steps):
        if not self.load_qt and np.random.rand() < get_eps_threshold(steps):
            return np.random.randint(0, len(self.actions))
        else:
            if state not in self.states_list:
                self.add_state(state)
            idx = list(self.states_list).index(state)
            q_values = self.q_table[idx]
            return int(np.argmax(q_values))

    def add_state(self, state):
        self.q_table = np.vstack(
            [self.q_table, np.zeros((1, len(constants.possible_action)))])
        self.states_list.add(state)

    def update_qtable(self, state, next_state, action, reward):
        if state not in self.states_list:
            self.add_state(state)
        if next_state not in self.states_list:
            self.add_state(next_state)
        state_idx = list(self.states_list).index(state)
        next_state_idx = list(self.states_list).index(next_state)
        q_state = self.q_table[state_idx, action]
        q_next_state = self.q_table[next_state_idx].max()
        q_targets = reward + (self.reward_decay * q_next_state)
        loss = q_targets - q_state
        self.q_table[state_idx, action] += self.lr * loss
        return loss

    def get_size(self):
        print(self.q_table.shape)

    def save_qtable(self, filepath):
        temp = np.array(list(self.q_table))
        np.save(filepath, temp)

    def load_qtable(self, filepath):
        return np.load(filepath)

    def save_states(self, filepath):
        temp = np.array(list(self.states_list))
        np.save(filepath, temp)

    def load_states(self, filepath):
        return np.load(filepath)


""" This portion was written by The Bottles """


class ModifiedQTable(QTable):
    def __init__(self, actions, lr=0.01, reward_decay=0.9, load_qt=None, load_st=None):
        super(ModifiedQTable, self).__init__(actions, lr=lr, reward_decay=reward_decay, load_qt=load_qt, load_st=load_st)

    def bad_action(self, state, action):
        # print("Not a valid action for this state")
        bad = tuple((-1, -1, -1, -1, -1, -1, -1, -1))
        self.update_qtable(state, bad, action, -9999)
