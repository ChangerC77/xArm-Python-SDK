#!/usr/bin/env python3

"""
Description: go to home position
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip)
    arm.clean_error()
   
    time.sleep(0.1)
    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.228'
    main(ip)