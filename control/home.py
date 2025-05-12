#!/usr/bin/env python3

"""
Description: go to home position
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip, is_radian=True)
    arm.set_tcp_load(0, [0, 0, 0])
    arm.set_tcp_offset([0, 0, 0, 0, 0, 0])
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    arm.move_gohome(wait=True)

if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)