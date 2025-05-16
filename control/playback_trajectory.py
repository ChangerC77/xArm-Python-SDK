#!/usr/bin/env python3

"""
play the data collected in teleoperation
"""

import os
import sys
import time
import argparse
import pickle
import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from xarm.wrapper import XArmAPI

def load_trajectory(pkl_file):
    """加载轨迹数据并确保时间戳为float类型"""
    with open(pkl_file, 'rb') as f:
        skill_data = pickle.load(f)
    
    assert skill_data[0]['skill_description'] == 'GuideMode', \
    "Trajectory not collected in guide mode"
    skill_state_dict = skill_data[0]['skill_state_dict']

    T = skill_state_dict['time_since_skill_started']
    pose = skill_state_dict['O_T_EE']
    
    return {
        'poses': pose,
        'timestamps': T
    }

def playback(arm, trajectory):
    poses = trajectory['poses']
    ts = trajectory['timestamps']
    
    for i in range(1, len(ts), 10):
        # print("pose", poses[i])
        arm.set_position(x=poses[i][0], y=poses[i][1], z=poses[i][2], roll=poses[i][3], pitch=poses[i][4], yaw=poses[i][5], speed=100, is_radian=False, wait=True)
        time.sleep(0.01)

def main(args):
    # 初始化机械臂
    arm = XArmAPI(args.ip)
    time.sleep(0.5)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(0)
    
    # 归零
    print("Homing...")
    arm.move_gohome(wait=True)
    
    # 加载轨迹
    print(f"Loading {args.path}")
    trajectory = load_trajectory(args.path)
    
    # 执行回放
    playback(arm, trajectory)
    
    # 断开连接
    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='dataset/xarm_traj.pkl', required=False, help='pickle path')
    parser.add_argument('--ip', default='192.168.1.239', help='xArm IP address')
    args = parser.parse_args()
    main(args)