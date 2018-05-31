import numpy as np
import unitselection


AI_SELF = 1
AI_HOSTILE = 4
PLAYER_RELATIVE = 5
SELECTED = 6

np.set_printoptions(threshold=np.nan)

class QTable(object):
    def __init__(self, possible_action):
        self.hello = 4

    def get_state(self, obs):
        #Enemies Present
        enemies = 1 if AI_HOSTILE in obs.observation['feature_minimap'][PLAYER_RELATIVE] else 0

        #TODO: Group Units Selected
        groupUnits = 2

        #TODO: Attacking or Moving
        attackOrMoving = 2

        #TODO: Multiple groups present
        multipleGroups = 2

        return (enemies,groupUnits,attackOrMoving,multipleGroups)

    def get_env(self, obs, idk1, idk2, idk3, idk4):
        screen_features = unitselection.get_units(obs)
        print("-------------")
        print(screen_features)
        #state
        state = self.get_state(obs);


        #current position of the ones selected
        currentx, currenty = unitselection.get_unit_coors(screen_features, AI_SELF) #wrong
        current_pos = (np.mean(currentx),np.mean(currenty))

        #target TODO: depends, top or bottom, depends on selected group
        targetxs, targetys = unitselection.get_unit_coors(screen_features, AI_HOSTILE)
        target_pos = (np.mean(targetxs),np.mean(targetys))


        return state, target_pos, current_pos
    def get_action(self, idk1):
        return 3
