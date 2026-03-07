#!/usr/bin/env python3

"""
Description: joint position control
"""

import os
import sys
import time
import yaml
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip)
    time.sleep(0.5)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()
        
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    speed = 50
    angle = [-0.900002, -23.600017, 0.20002, 3.399989, -180.00002, 62.699975, 180.00002]
    arm.set_servo_angle(angle=angle, speed=speed, is_radian=False, wait=True)
    print("joint angles (degrees):", arm.get_servo_angle(is_radian=False)[1])

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        ip = config.get('ip')
    main(ip)