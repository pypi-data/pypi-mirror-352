from .container  import Container
from packer.pct_model.model import DRL_GAT
from packer.irrgular_tools import *
from tools import load_config
from packer.pack2d_model.pack.tool_2d import *

import time


def get_policy(args, method):
    # LSAH   MACS   RANDOM  OnlineBPH   DBL  BR  MTPE IR_HM BLBF FF
    infos = dict()
    infos['args'] = None
    
    if method in ['LeftBottom', 'HeightmapMin', 'LSAH', 'MACS', 'RANDOM', 'OnlineBPH', 'DBL', 'BR', 'SDFPack', 'SDF_Pack', 'MTPE', 'IR_HM', 'BLBF', 'FF']:
        PCT_policy = 'heuristic'
        
    elif method == 'PCT' or method == 'PackE':
        # args = get_pct_args()
        # infos['args'] = args
        args_method = load_config(args.config_learning_method)
        
        if args_method.no_cuda: args.device = 'cpu'
        if args_method.setting == 1:
            args_method.internal_node_length = 6
        elif args_method.setting == 2:
            args_method.internal_node_length = 6
        elif args_method.setting == 3:
            args_method.internal_node_length = 7
        if args_method.evaluate:
            args_method.num_processes = 1

        if args.data == 'random' or args.data == 'time_series':
            if args.setting == 1:
                args_method.model_path = args_method.model_path_random_time_series
            else:
                args_method.model_path = args_method.model_path_random_time_series_pybullet
        elif args.data == 'occupancy':
            if args.setting == 1:
                args_method.model_path = args_method.model_path_occupancy
            else:
                args_method.model_path = args_method.model_path_occupancy_pybullet
        elif args.data == 'flat_long':
            if args.setting == 1:
                args_method.model_path = args_method.model_path_flat_long
            else:
                args_method.model_path = args_method.model_path_flat_long_pybullet

        infos['args'] = args_method
        PCT_policy = DRL_GAT()
        # Load the trained model
        model_path = args_method.model_path
        PCT_policy = load_policy(model_path, PCT_policy)
        print('Pre-train model loaded!', model_path)
        PCT_policy.eval()

    return PCT_policy, infos



def method(env):
    

    
    obs, reward, done, infos = env.step(action)

    new_action = (rot,) + now_action[1:]
    # now_action[0] = rot
    
    if done:
        # obs = env.reset()
        pass
    
    return done, new_action, lz, obs



class Packer():
    def __init__(self, container_size) -> None:
        self.container = Container(container_size)
    
    def pack_box(self, env, infos, obs, method, policy):
        x, y, z = env.next_box
        planning_time = givenData.planning_times[infos['block_index']]
        action = givenData.actions[infos['block_index']]
        rotation_flag, lx, ly = action[0], action[1], action[2]

        if rotation_flag:
            box_size = y, x, z
        else:
            box_size = x, y, z

        rec = env.space.plain[action[1]:action[1] + box_size[0], action[2]:action[2] + box_size[1]]
        lz = np.max(rec)

        obs, reward, done, info = env.step(action)
        infos['next_obs'] = obs

        placeable = not done
        if placeable is False:
            return placeable, [], None, infos, planning_time

        pos = np.array([lx, ly, lz], dtype=np.float32)

        return placeable, pos, rotation_flag, infos, planning_time

    
    def add_box(self, box, pos):
        pos = self.container.add_new_box(box, pos)
        add_success = True
        if pos is None:
            add_success = False
        
        return add_success


