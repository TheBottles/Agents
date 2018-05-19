from pysc2.lib import actions, features, point
from pysc2.bin import replay_info
from pysc2.env.environment import TimeStep, StepType
from pysc2 import run_configs
from s2clientprotocol import sc2api_pb2 as sc_pb
import importlib
import sys
from absl import flags
from pprint import pprint

FLAGS = flags.FLAGS
FLAGS(sys.argv)
flags.DEFINE_string("replay", None, "Path to a replay file.")
flags.mark_flag_as_required("replay")

# features.transform_obs returns an array with entries: 'cargo_slots_available'; 'player' ; 'game_loop' ; 'score_cummulative' ; 'cargo'
#                    'build_queue' ; 'screen' ; 'single_select' ; 'available_actions' ; 'control_groups' 

class Replay:
    # sets up the replay object and starts the replay    
    def __init__(self, path):
        self.run_config = run_configs.get()
        self.sc2_proc = self.run_config.start()
        # controller holds a lot of the actions to manipulate the game state
        self.controller = self.sc2_proc.controller
        replay_data = self.run_config.replay_data(path)
        info = self.controller.replay_info(replay_data)
        interface = sc_pb.InterfaceOptions(
            raw=False, score=True,
            feature_layer=sc_pb.SpatialCameraSetup(width=24))
        map_data = None
        if info.local_map_path:
            map_data = self.run_config.map_data(info.local_map_path)
        self.controller.start_replay(sc_pb.RequestStartReplay(
            replay_data=replay_data,
            map_data=map_data,
            options=interface,
            observed_player_id=0))
        self._episode_steps = 0
        self._state = StepType.FIRST
    # collects the data from the replay
    def start(self):
        _features = features.Features(self.controller.game_info())
        # loop steps through the replay until the game is over 
        while True:
            self.controller.step(1)
            obs = self.controller.observe()
            agent_obs = _features.transform_obs(obs.observation)
            # exit condition
            if obs.player_result: 
                self._state = StepType.LAST
            self._episode_steps += 1
            step = TimeStep(step_type=self._state, reward=0,
                            discount=0, observation=agent_obs)
            if obs.player_result:
                break
            self._state = StepType.MID
            print(agent_obs["multi_select"])
       
def main():
    path = '/home/spirt/Documents/ECS170/Replays'
    #round1.start()
    #print(round1._episode_steps)
    replay_info._replay_info(round1)
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
