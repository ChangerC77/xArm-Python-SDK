#!/usr/bin/env python3

"""
Description: teleoperation with spacemouse
"""

import time
from spacemouse import Spacemouse
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

import tracker
import openvr
from scipy.spatial.transform import Rotation as R
import numpy as np

def load_calibration(path):
    data = np.load(path)
    return data["pose_0"],data["transform"]

def apply_transform(poses_all, transform,pose_0):
    flag=False
    if poses_all.ndim==2:
        poses_all=poses_all[None,...]
        flag=True
    assert poses_all.shape[1:]==(4,4)
    ## PCA only on translation
    poses_all[:,:3,3] = (poses_all[:,:3,3]-pose_0[:3,3])@np.linalg.inv(transform[:3,:3]).T
    ## rotation relative to pose_0
    poses_all[:,:3,:3] = np.linalg.inv(pose_0[:3,:3])@poses_all[:,:3,:3]
    if flag:
        poses_all=poses_all[0,...]
    return poses_all

 
"""四元数转欧拉角"""
def quaternion2euler(quaternion):
    r = R.from_quat(quaternion)
    euler = r.as_euler('xyz', degrees=True)
    return euler

def main(ip):
    # load calibration file
    pose_0, transform = load_calibration('calibration/calibration.npz')

    """ robot """
    arm = XArmAPI(ip)
    time.sleep(0.5)

    #clean error and warn
    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)

    arm.set_mode(7)
    arm.set_state(0)
    speed = 300
    target_pose = arm.get_position(is_radian=False)

    position = np.array(target_pose[1][:3])
    rotation = target_pose[1][3:]

    """ tracker """
    vr_manager = tracker.VRSystemManager()
    data_manager = tracker.DataConverter()
    if not vr_manager.initialize_vr_system():
        return
    
    print('Ready...')

    time.sleep(1)

    # 记录上一帧的 pose（初始化为 None）
    last_pose = None
    last_rota = None

    try:
        while True:
            poses = vr_manager.get_tracker_data()
            if poses[1].bPoseIsValid:
                device_class = vr_manager.vr_system.getTrackedDeviceClass(1)
                if device_class == openvr.TrackedDeviceClass_GenericTracker:
                    current_pose = data_manager.convert_to_numpy(poses[1].mDeviceToAbsoluteTracking)  # [x, y, z, r_w, r_x, r_y, r_z]
                    
                    scale_factor = 500

                    transformed_pose= apply_transform(current_pose, transform, pose_0)
                    transformed_pose[1,3] *= -1
                    current_pose= transformed_pose[:3,3] * scale_factor
                    current_rota = np.array(transformed_pose[:3,:3]) * 0.5
                    # 从旋转矩阵创建Rotation对象
                    rot = R.from_matrix(current_rota)

                    # 转换为欧拉角 (默认ZYX顺序)
                    current_rota = rot.as_euler('xyz', degrees=True)  # 'xyz'表示旋转顺序，degrees=True表示返回角度制

                    # 如果是第一帧，直接记录，不计算相对值
                    if last_pose is None:
                        last_pose = current_pose
                        last_rota = current_rota
                        continue  # 跳过第一次计算

                    # 计算当前帧与上一帧的相对变化量
                    delta_pose = current_pose - last_pose
                    last_pose = current_pose  # 更新 last_pose
                    delta_rota = current_rota - last_rota
                    last_rota = current_rota  # 更新 last_rota

                    position += delta_pose
                    rotation += delta_rota
      
                    # 控制机械臂
                    arm.set_position(
                        x=position[0],
                        y=position[1],
                        z=position[2],
                        roll=rotation[1],
                        pitch=-rotation[0],
                        yaw=-rotation[2],
                        speed=speed,
                        wait=False,
                        is_radian=False
                    )

                    time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nStopping data collection...")
        arm.set_mode(0)
        arm.set_state(state=0)

        arm.move_gohome(wait=True)
    finally:
        vr_manager.shutdown_vr_system()
       
if __name__ == "__main__":
    ip = '192.168.1.239'
    main(ip)
            



