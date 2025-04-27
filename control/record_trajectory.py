#!/usr/bin/env python3

"""
Description: record data (action and timestamp) using teleoperation with spacemouse and save as pkl
"""

import numpy as np
import argparse
import time
from spacemouse import Spacemouse
from scipy.spatial.transform import Rotation as R
import pickle as pkl
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def create_formated_skill_dict(joints, end_effector_positions, timestamps):
    """
    创建标准化技能字典
    参数:
        joints: 关节角度列表, 每个元素是6个关节角度的数组
        end_effector_positions: 末端位姿列表, 每个元素是[x,y,z,roll,pitch,yaw]
        timestamps: 时间戳列表
    返回:
        格式化后的字典,适合保存为pkl
    """
    # 转换为numpy数组并确保数据类型一致
    skill_dict = {
        'skill_description': 'GuideMode',
        'skill_state_dict': {
            'q': joints,          # 关节角度
            'O_T_EE': end_effector_positions,  # 末端位姿
            'time_since_skill_started': timestamps  # 时间戳
        }
    }
    return {0: skill_dict}  # 0表示技能开始时间

def main(args):
    arm = XArmAPI(args.ip, is_radian=True)
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    arm.move_gohome(wait=True)

    print('Ready...')

    # continuous control
    arm.set_mode(7)
    arm.set_state(0)
    time.sleep(1)
    max_pos_speed=0.15
    max_rot_speed=0.25
    dt = 2
    speed = 60

    target_pose = arm.get_position(is_radian=False)
    start_time = time.time()
    last_time = None
    position = target_pose[1][:3]
    rotation = target_pose[1][3:]

    # record data
    record_data = {
        'joints': [],
        'end_effector_positions': [],
        'timestamps': []
    }

    with Spacemouse(deadzone=0.3) as sm:
        while last_time is None or (last_time - start_time) < args.time:
        # while True:
            # action
            record_data['joints'].append(arm.get_servo_angle(is_radian=False)[1])
            record_data['end_effector_positions'].append(arm.get_position(is_radian=False)[1])
            # time 
            record_data['timestamps'].append(str(int(time.time() * 1000 - start_time))) 

            # spacemouse
            sm_state = sm.get_motion_state_transformed()
            dpos = sm_state[:3] * (max_pos_speed * dt)
            drot = sm_state[3:] * (max_rot_speed * dt)

            if not sm.is_button_pressed(0):
                # translation mode
                drot[:] = 0
            else:
                dpos[:] = 0
    
            position += dpos
            rotation += drot
            # print(f"Position: {position}, Rotation: {rotation}")

            arm.set_position(x=position[0], y=position[1], z=position[2], roll=rotation[0], pitch=rotation[1], yaw=rotation[2], speed=speed, wait=False, is_radian=False)
            time.sleep(0.01)
            last_time = time.time()
    
    # 保存数据
    skill_dict = create_formated_skill_dict(
        record_data['joints'],
        record_data['end_effector_positions'],
        record_data['timestamps']
    )

    with open(args.path, 'wb') as f:
        pkl.dump(skill_dict, f)
    print(f"save trajectory finished: {args.path}")

    # 安全关闭
    arm.set_mode(0)
    arm.disconnect()

if __name__ == "__main__":
    # init
    parser = argparse.ArgumentParser()
    parser.add_argument('--time', '-t', type=float, default=35)
    parser.add_argument('--path', '-p', default='dataset/xarm_traj.pkl')
    parser.add_argument('--ip', default='192.168.1.228', help='xArm IP address')
    args = parser.parse_args()

    main(args)
