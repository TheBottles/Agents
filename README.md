# Agents

To run the agents on Mac (linux should work too):

- Download and install StarCraft II
- In the game directory, create a directory "Maps" and "Replays"
    - Mac: `/Applications/StarCraft II/`
    - Windows: `C:\Program Files (x86)\StarCraft II\`
- Under Maps, create directory "mini_games" and should contains all the files downloaded from mini_games
    - Mac: `/Applications/StarCraft II/Maps/mini_games/`
    - Windows: `C:\Program Files (x86)\StarCraft II\Maps\mini_games\`
    - mini_games can be found in the forked repository pysc2
    https://github.com/TheBottles/pysc2/tree/master/pysc2/maps/mini_games

### Command
        $ python -m pysc2.bin.agent --map DefeatRoaches --agent <PATH_TO_PYTHON_FILE.PYTHON_CLASS>

##### Example

        $ python -m pysc2.bin.agent --map DefeatZerglingsAndBanelings --agent agent_DefeatRoaches.FlankingAgent
        $ python -m pysc2.bin.agent --map DefeatRoaches --agent agent_DefeatRoaches.FlankingAgent

        $ python -m pysc2.bin.agent --map DefeatZerglingsAndBanelings --agent agents.agent2.Agent2
        $ python -m pysc2.bin.agent --map DefeatRoaches --agent agents.agent2.Agent2

Note: for this command to work, you must cd into the folder containing the `agent.py` file.
