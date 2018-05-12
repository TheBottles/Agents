# Agents

To run the agents on Mac (linux should work too):

- Download and install StarCraft II
- In the game directory, create a directory "Maps" and "Replays"
    - Mac: `/Applications/StarCraft II/`
    - Windows: `C:\Program Files (x86)\StarCraft II\`
- Under Maps, create directory "mini_games" and should contains all the files downloaded from mini_games
    - mini_games can be found in the forked repository pysc2
    https://github.com/TheBottles/pysc2/tree/master/pysc2/maps/mini_games

### Command
        $ python -m pysc2.bin.agent --map MoveToBeacon --agent <PATH_TO_PYTHON_FILE.PYTHON_CLASS>

##### Example

        $ python -m pysc2.bin.agent --map MoveToBeacon --agent agent1.Agent1
