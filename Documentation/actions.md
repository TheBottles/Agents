# Actions Documentation
for pysc2

Author: Jennifer Salas  
ECS 170 Spring 2018

### General

**Description:**

The `actions` library is a collection of supporting functions and classes to control an agent in the game of StarCraft II. All of the descriptions have been direclty pulled or paraphrased from the `actions.py` source code.

The collection of actions include:

1. **move_camera**
    - Moves the camera to a specified location.
    - params: action, minimap
2. **select_point**
    - Selects a unit at a point.
    - params: action, select_point_act, screen
3. **select_rect**
    - Selects units within a rectangle.
    - params: action, select_add, screen, screen2
4. set_idle_worker
    - Selects an idle worker.
    - params: action, select_worker
5. **select_army**
    - Selects all army units.
    - params: action, select_add
6. select_warp_gates
    - Selects all warp gates.
    - params: action, select_add
7. select_larva
    - Selects all larva
    - params: action
8. **select_unit**
    - Selects a specific unit from the multi-unit selection.
    - params: action, select_unit_act, select_unit_id
9. **control_group**
    - Acts on a control group, selecting, setting etc.
    - params: action, control_group_act, control_gorup_id
10. unload
    - Unload a unit from a transport/bunker/nydus/etc.
    - params: action, unload_id
11. build_queue
    - Cancel a unit in the build queue.
    - params: action, build_queue_id
12. cmd_quick
    - Do a quick command like 'Stop' or 'Stim'.
    - params: action, ability_id, queued
13. cmd_screen
    - Do a command that needs a point on the screen.
    - params: action, ability_id, queued, screen
14. cmd_minimap
    - Do a command that needs a point on the minimap.
    - params: action, ability_id, queued, minimap
15. autocast
    - Toggle autocast
    - params: action, ability_id

The classes include:

1. ArgumentType
    - Represents a single argument type.
    - Attributes:
        - id: The argument id. This is unique.
        - name: The name of the argument, also unique.
        - sizes: The max+1 of each of the dimensions this argument takes.
        - fn: The function to convert the list of integers into something more meaningful to be set in the protos to send to the game.
2. Arguments
    - List of argument types.
    - Attributes:
        1. screen: A point on the screen.
        2. minimap: A point on the minimap.
        3. screen2: The second point for a rectangle. This is needed so that no function takes the same type twice.
        4. queued: Whether the action should be done now or later.
        5. control_group_act: What to do with the control group.
        6. control_group_id: Which control group to do it with.
        7. select_point_act: What to do with the unit at the point.
        8. select_add: Whether to add the unit to the selection or replace it.
        9. select_unit_act: What to do when selecting a unit by id.
        10. select_unit_id: Which unit to select by id.
        11. select_worker: What to do when selecting a worker.
        12. build_queue_id: Which build queue index to target.
        13. unload_id: Which unit to target in a transport/nydus/command center.
3. *Function*
    - Represents a function action.
    - Attributes:
        1. id: The function id, which is what the agent will use.
        2. name: The name of the function. Should be unique.
        3. ability_id: The ability id to pass to sc2.
        4. general_id: 0 for normal abilities, and the ability_id of another ability if it can be represented by a more general action.
        5. function_type: One of the functions in FUNCTION_TYPES for how to construct the sc2 action proto out of python types.
        6. args: A list of the types of args passed to function_type.
        7. avail_fn: For non-abilities, this function returns whether the function is valid.
4. Functions
    - Represents the full set of functions.
    - Most in depth part and requires more research.
5. FunctionCall
    - Represents a function call action.
    - Attributes:
        1. function: Store the function id, eg 2 for select_point.
        2. arguments: The list of arguments for that function, each being a list of ints. For select_point this could be: [[0], [23, 38]].
6. ValidActions
    - The set of types and functions that are valid for an agent to use.
    - Attributes:
        1. types: A namedtuple of the types that the functions require. Unlike TYPES above, this includes the sizes for screen and minimap.
        2. functions: A namedtuple of all the functions.

**Location:**  

    pysc2/pysc2/lib.actions.py
