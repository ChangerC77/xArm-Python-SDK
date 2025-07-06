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
    # angle = [86.586356, -18.808887, 6.007405, 33.076395, 3.213376, 51.606251, 134.999972] # initial joint position
    # angle = [1.764366, -0.529208, -0.046031, 0.807547, -0.075704, 1.225679, -0.581361]
    angle = [1.478742, -0.607456, 0.128854, 0.780796, -0.071136, 1.63369, -1.524777]
    arm.set_servo_angle(angle=angle, speed=speed, is_radian=True, wait=True)
    print(arm.get_servo_angle(), arm.get_servo_angle(is_radian=False))

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)