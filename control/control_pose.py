#!/usr/bin/env python3

"""
Description: go to home position
"""

import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip, is_radian=True)
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    pose = [206.511002, 1.99, 113.876999, 179.978706, -0.018736, 0.003724]
    arm.set_position(x=pose[0], y=pose[1], z=pose[2], roll=pose[3], pitch=pose[4], yaw=pose[5], speed=100, is_radian=False, wait=True)

    print(arm.get_position(is_radian=False))

if __name__ == '__main__':
    ip = '192.168.1.228'
    main(ip)