#!/usr/bin/env python3

"""
Description: clear error with YAML config
"""

import os
import sys
import time
import yaml
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

def main(ip):
    print(f"connecting xarm with: {ip}")
    arm = XArmAPI(ip)
    arm.clean_error()
    
    time.sleep(0.1)
    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        ip = config.get('ip')

    main(ip)