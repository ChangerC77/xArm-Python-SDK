#!/usr/bin/env python3

"""
Description: get the info about the arm
"""
from xarm import XArmAPI

import os
import sys
import yaml
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def get_info(ip):
    arm = XArmAPI(ip)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)
    
    # eef position
    eef_pose = arm.get_position(is_radian=False)
    print('eef position(°):', eef_pose[1]) # tuple((code, [x, y, z, roll, pitch, yaw])), only when code is 0, the returned result is correct.
    # print('position(radian):', arm.get_position(is_radian=True))

    # joint position
    joint_position = arm.get_servo_angle(is_radian=False)
    print('joint position(°):', joint_position[1])
    # print('angles(radian):', arm.get_servo_angle(is_radian=True))

    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        ip = config.get('ip')
    get_info(ip)