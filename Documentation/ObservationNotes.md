# Observation Object notes

An observation object is the state of the world and is passed into the step
function which is used by an agent to make actions. In our case, it is the
`obs` object.

`obs` is a dictionary containing the following keys: </br>
-`.step_type`</br>
-`.reward`</br>
-`.discount`</br>
-`.observation[]`</br>
-- `single_select`</br>
-- `multi_select`</br>
-- `build_queue`</br>
-- `cargo`</br>
-- `cargo_slots_available`</br>
-- `screen`</br>
-- `minimap`</br>
-- `game_loop`</br>
-- `score_cumulative`</br>
-- `player`</br>
-- `control_groups`</br>
-- `available_actions`</br>
-`.first()`</br>
-`.last()`</br>
