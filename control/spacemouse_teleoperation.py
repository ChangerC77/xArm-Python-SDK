#!/usr/bin/env python3

"""
Description: teleoperation with spacemouse
"""

import time
from spacemouse import Spacemouse
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip)
    arm.motion_enable(enable=True)

    print('Ready...')

    arm.set_mode(7)
    arm.set_state(0)
    time.sleep(1)
    max_pos_speed=0.15
    max_rot_speed=0.25
    dt = 2
    speed = 60

    target_pose = arm.get_position(is_radian=False)
    print("Target Pose: ", target_pose)
    position = target_pose[1][:3]
    rotation = target_pose[1][3:]

    with Spacemouse(deadzone=0.3) as sm:
        while True:
            sm_state = sm.get_motion_state_transformed()
            # print(sm_state)
            dpos = sm_state[:3] * (max_pos_speed * dt)
            drot = sm_state[3:] * (max_rot_speed * dt)

            if not sm.is_button_pressed(0):
                # translation mode
                drot[:] = 0
            else:
                dpos[:] = 0
    
            position += dpos
            rotation += drot
            # print(f"Position: {position}, Rotation: {rotation}")

            arm.set_position(x=position[0], y=position[1], z=position[2], roll=rotation[0], pitch=rotation[1], yaw=rotation[2], speed=speed, wait=False, is_radian=False)
            time.sleep(0.005) 

if __name__ == "__main__":
    ip = '192.168.1.239'
    main(ip)
            



