# Observation Object notes

An observation object is the state of the world and is passed into the step
function which is used by an agent to make actions. In our case, it is the
`obs` object.

`obs` is a dictionary containing the following keys:
- `single_select`
- `multi_select`
- `build_queue`
- `cargo`
- `cargo_slots_available`
- `screen`
- `minimap`
- `game_loop`
- `score_cumulative`
- `player`
- `control_groups`
- `available_actions`
