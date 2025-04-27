#!/usr/bin/env python3

"""
Description: read data from spacemouse
"""

import numpy as np
import time
from spacemouse import Spacemouse

def main():
    # 初始化位置和旋转量
    position = np.zeros(3)  # [x, y, z]
    rotation = np.zeros(3)  # [roll, pitch, yaw]

    # 控制参数
    max_pos_speed = 0.15  # 最大平移速度 (m/s)
    max_rot_speed = 0.25  # 最大旋转速度 (rad/s)
    dt = 0.02             # 50Hz 控制周期

    with Spacemouse(deadzone=0.3) as sm:
        try:
            while True:
                start_time = time.time()
                
                # 1. 获取 Spacemouse 输入（范围 [-1, 1]）
                sm_state = sm.get_motion_state_transformed()
                
                # 2. 计算增量（速度 × 时间步长）
                dpos = sm_state[:3] * (max_pos_speed * dt)
                drot = sm_state[3:] * (max_rot_speed * dt)

                # 3. 模式切换（按钮0按下时为旋转模式）
                if not sm.is_button_pressed(0):
                    drot[:] = 0  # 平移模式
                else:
                    dpos[:] = 0  # 旋转模式

                # 4. 更新位置和旋转（累积增量）
                position += dpos
                rotation += drot
                print(f"Rotation: {rotation}")

                # 5. 控制循环频率
                elapsed = time.time() - start_time
                time.sleep(max(0, dt - elapsed))

        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    main()