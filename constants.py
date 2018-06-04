from pysc2.lib import actions
from pysc2.lib import features
from pysc2.lib.actions import Function

_AI_RELATIVE        = features.SCREEN_FEATURES.player_relative.index
_AI_SELECTED        = features.SCREEN_FEATURES.selected.index
_NO_OP_ID           = actions.FUNCTIONS.no_op.id
_ATTACK_SCREEN_ID   = actions.FUNCTIONS.Attack_screen.id
_MOVE_SCREEN_ID     = actions.FUNCTIONS.Move_screen.id
_SELECT_ARMY_ID     = actions.FUNCTIONS.select_army.id
_SELECT_POINT_ID    = actions.FUNCTIONS.select_point.id
_SELECT_RECT_ID     = actions.FUNCTIONS.select_rect.id
_CONTROL_GROUP_ID   = actions.FUNCTIONS.select_control_group.id
_BACKGROUND = 0
_AI_SELF    = 1
_AI_ALLIES  = 2
_AI_NEUTRAL = 3
_AI_HOSTILE = 4
_SELECT_ALL = [0]
_NOT_QUEUED = [0]
_QUEUED     = [1]
_SET_GROUP  = [1]

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
_NO_OP          = 0000
_SELECT_UNITS   = 1000
_SET_CONTROL    = 2000
_SELECT_CONTROL = 3000
_MOVE_TO_TARGET = 4000
_FLANK_TARGET   = 5000
_ATTACK_TARGET  = 6000


moves = {
    _SELECT_UNITS   : _SELECT_RECT_ID,
    _SET_CONTROL    : _CONTROL_GROUP_ID,
    _SELECT_CONTROL : _CONTROL_GROUP_ID,
    _MOVE_TO_TARGET : _MOVE_SCREEN_ID,
    _FLANK_TARGET   : _MOVE_SCREEN_ID,
    _ATTACK_TARGET  : _ATTACK_SCREEN_ID,
    _NO_OP          : _NO_OP_ID,
}

possible_action = [
    _SELECT_UNITS,
    _SET_CONTROL,
    _SELECT_CONTROL,
    _MOVE_TO_TARGET,
    _FLANK_TARGET,
    _ATTACK_TARGET,
    _NO_OP,
]
