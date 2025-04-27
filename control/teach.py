#!/usr/bin/env python3

"""
Description: teach mode
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

"""
start or stop teach mode
"""

def teach(ip):
    print("choose teach mode? ")
    option = input("y/n: ")
    if option == 'y':
        arm = XArmAPI(ip, is_radian=True)
        arm.motion_enable(enable=True)
        arm.set_mode(0)
        arm.set_state(state=0)
        print("Press Ctrl+C to exit teach mode")
    
        arm.set_mode(2)
        arm.set_state(0)
    elif option == 'n':
        # Turn off manual mode 
        arm = XArmAPI(ip, is_radian=True)
        arm.motion_enable(enable=True)
        arm.set_mode(0)
        arm.set_state(0)
        print("exit teach mode")

if __name__ == '__main__':
    ip = '192.168.1.228'
    teach(ip)