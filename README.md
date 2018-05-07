# Agents

To run the agents on Mac (linux should work too): </br>

-Make sure you downloaded the game</br>
-In the game, create a directory "Maps" and "Replays"</br>
-Under Maps, create directory "mini_games" and should contains all the files downloaded from mini_games</br>

$ python -m pysc2.bin.agent --map MoveToBeacon --agent PYTHONFILE.PYTHONCLASS </br>
ex. $ python -m pysc2.bin.agent --map MoveToBeacon --agent agent1.Agent1 </br>

