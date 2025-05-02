#!/usr/bin/env python3

"""
Description: get the info about the arm
"""
from xarm import XArmAPI

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def get_info(ip):
    arm = XArmAPI(ip)
    arm.motion_enable(enable=True)
    arm.set_tcp_load(1, [0, 0, 0])
    arm.set_tcp_offset([0, 0, 0, 0, 0, 0])
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
    ip = '192.168.1.239'
    get_info(ip)