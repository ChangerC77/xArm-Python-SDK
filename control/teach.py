#!/usr/bin/env python3

"""
Description: start or stop teach mode
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def teach(ip):
    print("open or close teach mode? (y/n)")
    option = input("y/n: ")
    if option == 'y':
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
        print("Press Ctrl+C to exit teach mode")
    
        arm.set_mode(2)
        arm.set_state(0)
    elif option == 'n':
        # Turn off manual mode 
        arm = XArmAPI(ip)
        arm.motion_enable(enable=True)
        arm.set_mode(0)
        arm.set_state(0)
        print("exit teach mode")

if __name__ == '__main__':
    ip = '192.168.1.239'
    teach(ip)