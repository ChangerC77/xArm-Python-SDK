#!/usr/bin/env python3

"""
Description: record data (action and timestamp) and save as pkl
"""

import argparse
import time
import pickle as pkl
import os
import signal
import sys
import threading
from xarm.wrapper import XArmAPI

class Record_Xarm:
    def __init__(self, ip, save_path):
        self.arm = XArmAPI(ip)
        self.data_dict = {
            'joints': [],
            'eef_poses': [],
            'timestamps': []
        }
        self.stop = False
        self.save_path = save_path
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        time.sleep(0.5)

    def record_data(self):
        print('start to record trajectory...')
        while True:
            # action
            self.data_dict['joints'].append(self.arm.get_servo_angle(is_radian=False)[1])
            self.data_dict['eef_poses'].append(self.arm.get_position(is_radian=False)[1])
            # time 
            self.data_dict['timestamps'].append(int(time.time() * 1000))
            time.sleep(0.016)
            if self.stop:
                break

    
    def create_formated_skill_dict(self, joints, end_effector_positions, timestamps):
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
        action_dict = {
            'skill_description': 'GuideMode',
            'robot_dict': {
                'q': joints,          # 关节角度
                'eef': end_effector_positions,  # 末端位姿
                'timestamps': timestamps  # 时间戳
            }
        }
        return action_dict  # 0表示技能开始时间
    
    def save_data(self, record_data, ftype):
        action_dict = self.create_formated_skill_dict(
            record_data['joints'],
            record_data['eef_poses'],
            record_data['timestamps']
        )

        save_name = os.path.join(self.save_path, 'traj.pkl')
        
        if ftype =='pickle':
            with open(save_name, 'wb') as f:
                pkl.dump(action_dict, f)
            print(f"save trajectory finished: {save_name}")


    def signal_handler(self, sig, frame):
        if sig == signal.SIGTERM:
            self.stop = True
        self.save_data(self.data_dict, ftype='pickle')
        time.sleep(5)
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root_dir", 
        type=str, 
        default="/home/robotics/data_save", 
        help="Path to the base folder where data will be saved."
    )
    parser.add_argument(
        "--traj_number", 
        type=int, 
        default=255, 
        help="Trajectory ID."
    )
    parser.add_argument('--ip', default='192.168.1.239', help='xArm IP address')
    args = parser.parse_args()

    save_path = os.path.join(args.root_dir, str(args.traj_number).zfill(4), 'traj')
    os.makedirs(save_path, exist_ok=True)

    xarm_recorder = Record_Xarm(args.ip, save_path)
    xarm_recorder.record_data()