#!/usr/bin/env python3

"""
Description: set the TCP load and offset
"""

import os
import sys
import time
import yaml
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI



def main(args):
    arm = XArmAPI(args.ip)
    arm.set_tcp_load(args.tcp_config.get('load_weight', 0.5), center_of_gravity=args.tcp_config.get('center_of_gravity', [0, 0, 0]))  # set TCP load
    arm.set_tcp_offset(args.tcp_config.get('offset', [0, 0, 0, 0, 0, 0]))

    time.sleep(3)
    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    parser.add_argument('--ip', type=str, default='192.168.1.244', help='xArm IP address')

    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.ip = config.get('ip')
        args.tcp_config = config.get('tcp_config', {})
    main(args)