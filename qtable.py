import numpy as np
from unitselection import *


AI_SELF = 1
AI_HOSTILE = 4
PLAYER_RELATIVE = 5
SELECTED = 6

np.set_printoptions(threshold=np.nan)

class QTable(object):
    def __init__(self):
        self.hello = 4

    def get_state(self, obs):
        #Enemies Present
        enemies = 1 if AI_HOSTILE in obs.observation['feature_minimap'][PLAYER_RELATIVE] else 0

        #Group Units Selected
        groupUnits = 2

        #Attacking or Moving
        attackOrMoving = 2

        #Multiple groups present
        multipleGroups = 2

        return (enemies,groupUnits,attackOrMoving,multipleGroups)

    def get_env(self, obs):
        #state
        state = self.get_state(obs);


        #current position of the ones selected
        screen_features = get_units(obs)
        #currenty, currentx = np.nonzero( obs.observation['feature_minimap'][SELECTED] == 1 ) #Why this doesnt work? :/
        currentx, currenty = get_unit_coors(screen_features, AI_SELF)
        current_pos = (np.mean(currentx),np.mean(currenty))

        #target TODO: depends, top or bottom, depends on selected group
        targetxs, targetys = get_unit_coors(screen_features, AI_HOSTILE)
        target_pos = (np.mean(targetxs),np.mean(targetys))



        return state, target_pos, current_pos
    def get_action():
        return "hello from the other side,"