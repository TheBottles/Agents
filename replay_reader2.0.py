from pysc2.lib import actions, features, point
from pysc2.bin import replay_info, replay_actions
from pysc2.env.environment import TimeStep, StepType
from pysc2.lib import gfile
from pysc2 import run_configs
from s2clientprotocol import sc2api_pb2 as sc_pb
from future.builtins import range  # pylint: disable=redefined-builtin
import six
from six.moves import queue

import importlib
import sys
from absl import flags
from pprint import pprint
import collections
import multiprocessing
import os
import signal
import sys
import threading
import time

# python3 replay_reader2.0.py --replays /home/spirt/Documents/ECS170/Replays

FLAGS = flags.FLAGS
flags.mark_flag_as_required("replays")
FLAGS(sys.argv)

# Code taken from the main of the replay_actions file in pysc2 and modified

# Prints the stats every 10 seconds 
# We'll probably want to extract the made actions section and dump to a csv
def stats_printer(stats_queue):
    """A thread that consumes stats_queue and prints them every 10 seconds."""
    proc_stats = [replay_actions.ProcessStats(i) for i in range(FLAGS.parallel)]
    print_time = start_time = time.time()
    width = 107
    running = True
    while running:
        print_time += 10
        while time.time() < print_time:
            try:
                s = stats_queue.get(True, print_time - time.time())
                if s is None:  # Signal to print and exit NOW!
                    running = Falsea
                    break
                proc_stats[s.proc_id] = s
            except queue.Empty:
                pass
        replay_stats = replay_actions.ReplayStats()
        for s in proc_stats:
            replay_stats.merge(s.replay_stats)
        print((" Summary %0d secs " % (print_time - start_time)).center(width, "="))
        print(replay_stats.made_abilities)
        print(" Process stats ".center(width, "-"))
        print("\n".join(str(s) for s in proc_stats))
        print("=" * width)    
class Replay:
    # sets up the replay object and starts the replay    
    def __init__(self, path):
        self.path = path
         
    # collects the data from the replay
    def start(self):
        run_config = run_configs.get()
        # input replay does not exist
        if not gfile.Exists(FLAGS.replays):
            sys.exit("{} doesn't exist.".format(FLAGS.replays))
        
        stats_queue = multiprocessing.Queue()
        stats_thread = threading.Thread(target=stats_printer, args=(stats_queue,))
        stats_thread.start()
        try:
            # For some reason buffering everything into a JoinableQueue makes the
            # program not exit, so save it into a list then slowly fill it into the
            # queue in a separate thread. Grab the list synchronously so we know there
            # is work in the queue before the SC2 processes actually run, otherwise
            # The replay_queue.join below succeeds without doing any work, and exits.
            print("Getting replay list:", FLAGS.replays)
            replay_list = sorted(run_config.replay_paths(FLAGS.replays))
            print(len(replay_list), "replays found.\n")
            replay_queue = multiprocessing.JoinableQueue(FLAGS.parallel * 10)
            replay_queue_thread = threading.Thread(target=replay_actions.replay_queue_filler,
                                               args=(replay_queue, replay_list))
            replay_queue_thread.daemon = True
            replay_queue_thread.start()

            for i in range(FLAGS.parallel):
                p = replay_actions.ReplayProcessor(i, run_config, replay_queue, stats_queue)
                p.daemon = True
                p.start()
                time.sleep(1)  # Stagger startups, otherwise they seem to conflict somehow

            replay_queue.join()  # Wait for the queue to empty.
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, exiting.")
        finally:
            stats_queue.put(None)  # Tell the stats_thread to print and exit.
            stats_thread.join()
         
def main():
    path = '/home/spirt/Documents/ECS170/Replays'
    replays = Replay(path)
    replays.start()
if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
