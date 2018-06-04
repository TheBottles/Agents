from pysc2.lib import actions
from pysc2.lib import features

AI_RELATIVE        = features.SCREEN_FEATURES.player_relative.index
AI_SELECTED        = features.SCREEN_FEATURES.selected.index
NO_OP_ID           = actions.FUNCTIONS.no_op.id
ATTACK_SCREEN_ID   = actions.FUNCTIONS.Attack_screen.id
MOVE_SCREEN_ID     = actions.FUNCTIONS.Move_screen.id
SELECT_ARMY_ID     = actions.FUNCTIONS.select_army.id
SELECT_POINT_ID    = actions.FUNCTIONS.select_point.id
SELECT_RECT_ID     = actions.FUNCTIONS.select_rect.id
CONTROL_GROUP_ID   = actions.FUNCTIONS.select_control_group.id
BACKGROUND = 0
AI_SELF    = 1
AI_ALLIES  = 2
AI_NEUTRAL = 3
AI_HOSTILE = 4
SELECT_ALL = [0]
NOT_QUEUED = [0]
QUEUED     = [1]
SET_GROUP  = [1]

"""
    Actual possible set of actions:

        1. Select units
        2. Set a control group
        3. Select a control group
        4. Move (using AStar)
        5. Flank (using dubin's path)
        6. Attack
        7. No-op (this should only be done when waiting for other teams)
"""

THRESH = 15

# Custom Moves
NO_OP          = 0000
SELECT_UNITS   = 1000
SET_CONTROL    = 2000
SELECT_CONTROL = 3000
MOVE_TO_TARGET = 4000
FLANK_TARGET   = 5000
ATTACK_TARGET  = 6000


moves = {
    SELECT_UNITS   : SELECT_RECT_ID,
    SET_CONTROL    : CONTROL_GROUP_ID,
    SELECT_CONTROL : CONTROL_GROUP_ID,
    MOVE_TO_TARGET : MOVE_SCREEN_ID,
    FLANK_TARGET   : MOVE_SCREEN_ID,
    ATTACK_TARGET  : ATTACK_SCREEN_ID,
    NO_OP          : NO_OP_ID,
}

possible_action = [
    SELECT_UNITS,
    SET_CONTROL,
    SELECT_CONTROL,
    MOVE_TO_TARGET,
    FLANK_TARGET,
    ATTACK_TARGET,
    NO_OP,
]