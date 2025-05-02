#!/usr/bin/env python3

"""
Description: 6 dof eef pose control
"""

import os
import sys
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip, is_radian=True)
    arm.motion_enable(enable=True)
    arm.set_tcp_load(1, [0, 0, 0])
    arm.set_tcp_offset([0, 0, 0, 0, 0, 0])
    arm.set_mode(0)
    arm.set_state(state=0)

    pose = [-31.899017, 456.46994, 570.661926, 178.268026, 0.91381, 131.99647]
    arm.set_position(x=pose[0], y=pose[1], z=pose[2], roll=pose[3], pitch=pose[4], yaw=pose[5], speed=100, is_radian=False, wait=True)

    print(arm.get_position(is_radian=False))

if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)