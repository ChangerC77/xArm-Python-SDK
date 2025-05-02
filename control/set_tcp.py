#!/usr/bin/env python3

"""
Description: set the TCP load and offset
"""

import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI



def main(ip):
    arm = XArmAPI(ip)
    arm.set_tcp_load(0.5, center_of_gravity=[0, 0, 0])  # set TCP load
    arm.set_tcp_offset([0, 0, 0, 0, 0, 0])

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)