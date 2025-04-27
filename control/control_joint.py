#!/usr/bin/env python3

"""
Description: go to home position
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

"""
joint position control
"""

def main(ip):
    arm = XArmAPI(ip)
    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    speed = 50
    angle = [90, 0, 0, 0, 0, 0] 
    # angle = [206.511002, 1.99, 113.876999, 179.978706, -0.018736, 0.003724] # home position
    arm.set_servo_angle(angle=angle, speed=speed, is_radian=False, wait=True)
    print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=False))

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.228'
    main(ip)