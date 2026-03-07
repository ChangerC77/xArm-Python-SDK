#!/usr/bin/env python3

"""
trajectory playback 
"""

import os
import sys
import time
import yaml
import argparse
import pickle
import numpy as np
from scipy.interpolate import interp1d

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from xarm.wrapper import XArmAPI

def load_trajectory(pkl_file):
    """Load and preprocess trajectory data"""
    with open(pkl_file, 'rb') as f:
        skill_data = pickle.load(f)
    
    assert skill_data[0]['skill_description'] == 'GuideMode', \
    "Trajectory not collected in guide mode"
    
    skill_state_dict = skill_data[0]['skill_state_dict']
    poses = np.array(skill_state_dict['O_T_EE'])
    timestamps = np.array([float(t) for t in skill_state_dict['time_since_skill_started']])
    
    # Calculate relative time (ms)
    timestamps = timestamps - timestamps[0]
    
    return {
        'poses': poses,
        'timestamps': timestamps
    }

def resample_trajectory(trajectory, target_freq=100):
    """
    Resample trajectory to fixed frequency
    target_freq: target frequency (Hz)
    """
    poses = trajectory['poses']
    timestamps = trajectory['timestamps']
    
    # Original trajectory duration (seconds)
    duration = (timestamps[-1] - timestamps[0]) / 1000.0
    
    # Create interpolators
    interpolators = [
        interp1d(timestamps, poses[:,i], kind='linear', fill_value="extrapolate")
        for i in range(6)  # 6 DOF
    ]
    
    # Generate new time sequence
    new_timestamps = np.linspace(timestamps[0], timestamps[-1], int(duration * target_freq))
    
    # Interpolate new trajectory
    new_poses = np.vstack([f(new_timestamps) for f in interpolators]).T
    
    return {
        'poses': new_poses,
        'timestamps': new_timestamps
    }

def playback(arm, trajectory, speed, acc):
    """Play trajectory with reliable movement"""
    poses = trajectory['poses']
    timestamps = trajectory['timestamps']
    
    # First ensure we're in position mode for initial movement
    arm.set_mode(0)
    arm.set_state(0)
    time.sleep(0.1)
    
    # Move to start position smoothly
    print("Moving to start position...")
    current_pos = arm.get_position(is_radian=False)[1]
    distance = np.linalg.norm(np.array(poses[0][:3]) - np.array(current_pos[:3]))
    
    # Calculate appropriate speed for initial movement
    init_speed = min(100, max(50, distance * 2))  # 50-100mm/s based on distance
    init_acc = min(500, max(200, distance * 5))    # 200-500mm/s²
    
    arm.set_position(x=poses[0][0], y=poses[0][1], z=poses[0][2],
                   roll=poses[0][3], pitch=poses[0][4], yaw=poses[0][5],
                   speed=init_speed, mvacc=init_acc,
                   is_radian=False, wait=True)
    
    # Wait for movement to complete
    while arm.get_is_moving():
        time.sleep(0.1)
    
    # Switch to servo mode for trajectory playback
    print("Switching to servo mode...")
    arm.set_mode(1)
    arm.set_state(0)
    time.sleep(0.2)  # Important delay for mode switching
    
    # Start trajectory playback
    print("Starting trajectory playback...")
    for i in range(1, len(poses)):
        try:
            # Send servo command
            code = arm.set_servo_cartesian(poses[i], speed=speed, mvacc=acc, is_radian=False)
            if code != 0:
                print(f"Servo command error at point {i}: {code}")
                break
                
            # Calculate appropriate delay
            if i < len(poses)-1:
                dt = (timestamps[i+1] - timestamps[i]) / 1000.0
                time.sleep(max(0.005, min(dt, 0.1)))  # 5ms-100ms
                
        except Exception as e:
            print(f"Error at point {i}: {e}")
            break

def main(args):
    # Initialize arm
    print("Connecting to xArm...")
    arm = XArmAPI(args.ip)
    time.sleep(0.5)

    # Clean errors
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    
    # Load trajectory
    print(f"Loading trajectory from {args.path}")
    try:
        raw_trajectory = load_trajectory(args.path)
    except Exception as e:
        print(f"Failed to load trajectory: {e}")
        arm.disconnect()
        return
    
    # Resample trajectory
    print("Resampling trajectory...")
    trajectory = resample_trajectory(raw_trajectory, target_freq=args.freq)
    
    # Playback trajectory
    print(f"Playing back trajectory (speed: {args.speed} mm/s, accel: {args.acc} mm/s²)")
    start_time = time.time()
    playback(arm, trajectory, speed=args.speed, acc=args.acc)
    print(f"Playback completed in {time.time()-start_time:.2f} seconds")
    
    # Cleanup
    arm.set_mode(0)
    arm.set_state(0)
    arm.disconnect()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='dataset/xarm_traj.pkl', help='Path to trajectory pickle file')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    parser.add_argument('--ip', default='192.168.1.239', help='xArm IP address')
    parser.add_argument('--speed', type=int, default=0, help='Movement speed (mm/s)')
    parser.add_argument('--acc', type=int, default=0, help='Movement acceleration (mm/s²)')
    parser.add_argument('--freq', type=int, default=100, help='Resampling frequency (Hz)')
    args = parser.parse_args()
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.ip = config.get('ip')
        args.path = config.get('path', args.path)
        args.freq = config.get('freq', args.freq)

    main(args)