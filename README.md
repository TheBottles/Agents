# Agents

To run the agents on Mac (linux should work too):

- Download and install StarCraft II
- In the game, create a directory "Maps" and "Replays"
- Under Maps, create directory "mini_games" and should contains all the files downloaded from mini_games
  - mini_games can be found in the forked repository pysc2
    https://github.com/TheBottles/pysc2/tree/master/pysc2/maps/mini_games

### Command

        $ python -m pysc2.bin.agent --map MoveToBeacon --agent <PYTHONFILE.PYTHONCLASS>

##### Example

        $ python -m pysc2.bin.agent --map MoveToBeacon --agent agent1.Agent1
