#!/usr/bin/env python3

"""
Description: 机械臂示教数据发布逻辑 (仅限 7 关节，不含夹爪)
功能：获取 xArm 关节角度与末端位姿，发布 ROS 话题，并统计硬件采样频率。
"""

import argparse
import yaml
import time
import rospy
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from xarm.wrapper import XArmAPI

class Record_Xarm:
    def __init__(self, ip, feq):
        self.feq = feq
        self.arm = XArmAPI(ip)
        # 关节名称：去掉 gripper，仅保留 7 个关节
        self.joint_names = [
            'joint1', 'joint2', 'joint3', 'joint4', 
            'joint5', 'joint6', 'joint7'
        ]
        
        # 清除错误和警告
        if self.arm.warn_code != 0:
            self.arm.clean_warn()
        if self.arm.error_code != 0:
            self.arm.clean_error()

        self.arm.motion_enable(enable=True)
        self.arm.set_mode(0)
        self.arm.set_state(state=0)
        
        print("--- 正在进入示教模式 (7关节) ---")
        self.arm.set_mode(2)  # 示教模式
        self.arm.set_state(0)
        
        rospy.init_node('xarm_recorder', anonymous=True)
        
        # 发布末端执行器位姿
        self.eef_pub = rospy.Publisher('/eef_pose', PoseStamped, queue_size=20)
        # 发布关节状态
        self.joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=20)

        # --- 时间统计变量 ---
        self.first_frame_time = None  
        self.last_frame_time = None   
        self.frame_count = 0    

    def disconnect(self):
        """显式断开与机械臂的连接"""
        if hasattr(self, 'arm') and self.arm:
            self.arm.set_state(state=4) # 停止动作
            self.arm.disconnect()
            print("已成功断开与 xArm 的连接。")      

    def run(self):
        # 设置 ROS 循环频率
        rate = rospy.Rate(self.feq)
        print(f"开始发布数据，目标频率: {self.feq}Hz")
        print("Press Ctrl+C to exit")
        
        while not rospy.is_shutdown():
            try:
                # 记录开始获取数据的时间点 (Wall Time)
                current_time_wall = time.time()
                
                # 1. 获取硬件数据
                code_angles, joint_angles = self.arm.get_servo_angle(is_radian=True)
                code_pose, eef_pose = self.arm.get_position(is_radian=True)
                
                # 检查数据获取是否成功
                if code_angles == 0 and code_pose == 0:
                    self.frame_count += 1
                    
                    if self.first_frame_time is None:
                        self.first_frame_time = current_time_wall
                        self.last_frame_time = current_time_wall
                        rospy.loginfo(f"[STAT] 成功读取首帧 | 时间戳: {self.first_frame_time:.6f}s")
                    else:
                        # 计算时间差与频率
                        delta_time = current_time_wall - self.last_frame_time
                        instant_freq = 1.0 / delta_time if delta_time > 0 else 0.0
                        
                        print(f"[STAT] 帧序: {self.frame_count:05d} | 间隔: {delta_time*1000:6.2f}ms | 频率: {instant_freq:6.2f}Hz")
                        self.last_frame_time = current_time_wall

                    # 2. 发布 ROS 消息
                    current_time_ros = rospy.Time.now()
                    
                    # 发布关节状态 (仅限 7 个关节数据)
                    joint_msg = JointState()
                    joint_msg.header.stamp = current_time_ros
                    joint_msg.name = self.joint_names
                    joint_msg.position = joint_angles  # 不再追加夹爪的 [0.0]
                    self.joint_pub.publish(joint_msg)
                    
                    # 发布末端位姿信息
                    pose_msg = PoseStamped()
                    pose_msg.header.stamp = current_time_ros
                    pose_msg.header.frame_id = "base_link"
                    pose_msg.pose.position.x = eef_pose[0]
                    pose_msg.pose.position.y = eef_pose[1]
                    pose_msg.pose.position.z = eef_pose[2]
                    pose_msg.pose.orientation.x = eef_pose[3]
                    pose_msg.pose.orientation.y = eef_pose[4]
                    pose_msg.pose.orientation.z = eef_pose[5]
                    pose_msg.pose.orientation.w = eef_pose[6] if len(eef_pose) > 6 else 1.0
                    self.eef_pub.publish(pose_msg)
                
                rate.sleep()
                
            except Exception as e:
                rospy.logerr(f"采样循环出错: {e}")
                time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='192.168.1.244', help='xArm IP地址')
    parser.add_argument("--feq", type=int, default=100, help="发布频率(Hz)")
    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.ip = config.get('ip')
        args.feq = config.get('feq', args.feq)
    try:
        recorder = Record_Xarm(args.ip, args.feq)
        recorder.run()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        print(f"运行出错: {e}")
    finally:
        # 无论如何确保断开连接
        if recorder:
            recorder.disconnect()