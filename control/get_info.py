#!/usr/bin/env python3

"""
Description: get the info about the arm
"""
import os
import sys
home_dir = os.path.expanduser('~')  # 获取用户家目录
prometheus_dir = os.path.join(home_dir, 'Prometheus')  # 构建 ~/Prometheus 路径
sys.path.append(prometheus_dir)  # 添加到 Python 路径
from xarm import XArmAPI

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def get_info(ip):
    arm = XArmAPI(ip)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)
    
    # eef position
    eef_pose = arm.get_position(is_radian=False)
    print('eef position(°):', eef_pose[1]) # tuple((code, [x, y, z, roll, pitch, yaw])), only when code is 0, the returned result is correct.
    # print('position(radian):', arm.get_position(is_radian=True))

    # joint position
    joint_position = arm.get_servo_angle(is_radian=True)
    print('joint position(°):', joint_position[1])
    # print('angles(radian):', arm.get_servo_angle(is_radian=True))

    # tcp load
    print('* tcp_load:', arm.tcp_load)
    print('* tcp_offset:', arm.tcp_offset)

    arm.disconnect()

if __name__ == '__main__':
    ip = '192.168.1.239'
    get_info(ip)