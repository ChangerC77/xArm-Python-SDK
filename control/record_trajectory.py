#!/usr/bin/env python3

"""
Description: record data (action and timestamp) and save as pkl
"""

import argparse
import time
import pickle as pkl
import os
import yaml
import threading
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

def wait_for_enter(stop_event):
    """Thread function to wait for Enter key press"""
    input()  # This will block until Enter is pressed
    stop_event.set()

def main(args):
    # Create dataset directory if it doesn't exist
    os.makedirs(os.path.dirname(args.path), exist_ok=True)
    
    arm = XArmAPI(args.ip)
    time.sleep(0.5)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    print('start to record trajectory...')
    print('Press Enter to stop recording...')

    # continuous control
    arm.set_mode(2)
    arm.set_state(0)

    start_time = time.time()

    # record data
    record_data = {
        'joints': [],
        'end_effector_positions': [],
        'timestamps': []
    }

    # Create event to signal stopping
    stop_event = threading.Event()
    # Start thread to monitor for Enter key
    input_thread = threading.Thread(target=wait_for_enter, args=(stop_event,))
    input_thread.daemon = True
    input_thread.start()

    try:
        while not stop_event.is_set():
            # action
            record_data['joints'].append(arm.get_servo_angle(is_radian=False)[1])
            record_data['end_effector_positions'].append(arm.get_position(is_radian=False)[1])
            # time 
            record_data['timestamps'].append(str(int(time.time() * 1000 - start_time))) 

            # Small delay to prevent overwhelming the system
            time.sleep(0.01)

    except Exception as e:
        print(f"Error occurred: {e}")
        
    finally:
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
        arm.set_state(0)
        arm.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='dataset/xarm_traj.pkl')
    parser.add_argument('--ip', default='192.168.1.244', help='xArm IP address')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.ip = config.get('ip')
        args.path = config.get('path')

    main(args)