#!/usr/bin/env python3

"""
Description: read force raw data and external data
"""

import time
from xarm.wrapper import XArmAPI

def main(ip):
    arm = XArmAPI(ip, enable_report=True)
    arm.motion_enable(enable=True)
    arm.ft_sensor_enable(0)

    arm.clean_error()
    arm.clean_warn()
    arm.ft_sensor_enable(1)
    time.sleep(0.5)
    arm.ft_sensor_set_zero()

    while arm.connected and arm.error_code == 0:
        # ft_raw_force and ft_ext_force will update by reporting socket
        # Fx, Fy, Fz, Tx, Ty, Tz
        print('raw_force: Fx: {}, Fy: {}, Fz: {}, Tx: {}, Ty:{}, Tz:{}'.format(arm.ft_raw_force[0], arm.ft_raw_force[1], arm.ft_raw_force[2], arm.ft_raw_force[3], arm.ft_raw_force[4], arm.ft_raw_force[5]))
        print('exe_force: Fx: {}, Fy: {},Fz: {}, Tx: {}, Ty:{}, Tz: {}'.format(arm.ft_ext_force[0], arm.ft_ext_force[1], arm.ft_ext_force[2], arm.ft_ext_force[3], arm.ft_ext_force[4], arm.ft_ext_force[5]))
        time.sleep(0.2)

    arm.ft_sensor_enable(0)
    arm.disconnect()


if __name__ == '__main__':
    ip = '192.168.1.239'
    main(ip)