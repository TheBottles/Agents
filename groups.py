from qtable import *

class Group():

    def __init__(self, location = None):
        self.moving = False
        self.selected = False
        self.target = None
        self.prev_state = None
        self.prev_action = None
        self.prev_location = location

    def do_action(self, obs, qtable, group_queue):

        state, moving, groups, target, location = get_state(obs)

        self.prev_state = state
        action = qtable.get_action(state, obs.observation['available_actions'])
        self.prev_action = action
        self.moving = moving
        func = actions.FunctionCall(_NO_OP, [])
        units = get_units(obs)


        if possible_action[action] == _ATTACK_SCREEN:
            print("DO A* AND ATTACK") # assume units are already selected here
            target_x, target_y = A_Star(obs, current_pos, target_pos)
            func = actions.FunctionCall(
                _ATTACK_SCREEN, [_NOT_QUEUED, [target_y, target_x]])
            return False, func
        elif possible_action[action] == _SELECT_ARMY:
            print("Select entire army")
            func = actions.FunctionCall(_SELECT_ARMY, [_SELECT_ALL])
            return True, func
        elif possible_action[action] == _SELECT_RECT:
            print("select some from army") # assume that all units are grouped together
            # find the clusters
            #num_clusters, cluster_sets, clusters, len(units[0])
            num_clusters, cluster_sets, clusters, total_units = count_group_clusters(obs, _AI_SELF)
            # get half of the clusters
            group1, group2 = group_splitter(cluster, 0)
            # generate a new group with last known location
            newGroup = Group((group2[0].mean(), group1[1].mean()))
            # pop the new group into the queue
            group_queue.put(newGroup)
            # get our group location
            self.prev_location = (group1[0].mean(), group1[1].mean())
            selk.selected = True
            # return selection

            # get the highest x and y points from our group1
            xmax = group[0][np.argmax(group1[0])]
            ymax = group[1][np.argmax(group1[1])]

            # get the lowest x and y points from our group1
            xmin = group[0][np.argmin(group1[0])]
            ymin = group[1][np.argmin(group1[1])]

            func = action.FunctionCall( _SELECT_RECT, [False, [ymax, xmax], [ymin, xmin]])
            return True, func
        else:
            print("RELEASE CONTROL HERE")
            self.selected = False
            if self.prev_action == _NO_OP: return True, func # this is done to prevent an infinite loop
            else: return False, func #return false because we didn't perfom action
