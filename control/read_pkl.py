#!/usr/bin/env python3

"""
Description: read pkl file and echo data
"""

import pickle
import argparse
import yaml

def main(args):
    with open(args.path, 'rb') as file:
        skill_data = pickle.load(file)

    # 打印加载后的数据
    # print(data)
    assert skill_data[0]['skill_description'] == 'GuideMode', \
    "Trajectory not collected in guide mode"
    skill_state_dict = skill_data[0]['skill_state_dict']

    T = skill_state_dict['time_since_skill_started']
    pose = skill_state_dict['O_T_EE']

    # print("ts:", T)
    # print("pose:", pose)
    print("pose length:", len(pose))

    # return {
    #     'poses': np.array(skill_data['O_T_EE']),
    #     'timestamps': T
    # }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='dataset/xarm_traj.pkl', required=False, help='pickle path')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.path = config.get('path')
    main(args)