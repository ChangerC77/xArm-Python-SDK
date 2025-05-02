#!/usr/bin/env python3

"""
Description: joint position control
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip)
    arm.motion_enable(enable=True)
    arm.set_tcp_load(1, [0, 0, 0])
    arm.set_tcp_offset([0, 0, 0, 0, 0, 0])
    arm.set_mode(0)
    arm.set_state(state=0)

    speed = 50
    angle = [12.99749, -7.349731, 74.683387, 93.783279, 6.648258, 95.126235, -42.974241] # initial joint position
    arm.set_servo_angle(angle=angle, speed=speed, is_radian=False, wait=True)
    print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=False))

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)