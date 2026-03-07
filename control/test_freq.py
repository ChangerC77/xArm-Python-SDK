import time
import argparse
import yaml

from xarm.wrapper import XArmAPI

def main(args):
    # 1. 初始化机械臂
    arm = XArmAPI(args.ip)
    arm.clean_error()
    arm.clean_warn()
    arm.motion_enable(enable=True)
    
    # 实时控制必须使用模式 1 (ServoJ 模式)
    arm.set_mode(1) 
    arm.set_state(state=0)
    time.sleep(1)

    print(f"--- 开始频率测试 ---")
    print(f"目标频率: {args.freq} Hz (周期: {1.0/args.freq*1000:.2f} ms)")
    
    # 获取初始关节角度
    _, start_angles = arm.get_servo_angle()
    current_angles = list(start_angles)

    count = 0
    total_samples = args.freq * 10  # 测试持续 10 秒
    start_test_time = time.time()
    last_time = start_test_time
    
    intervals = []

    try:
        while count < total_samples:
            t_loop_start = time.time()

            # 2. 发送控制指令 (使用非阻塞模式 wait=False)
            # 我们只是在原地微动，确保安全
            ret = arm.set_servo_angle_j(current_angles, is_radian=False, wait=False)
            
            # 3. 时间统计
            t_now = time.time()
            dt = t_now - last_time
            intervals.append(dt)
            
            if count % args.freq == 0 and count > 0:
                avg_dt = sum(intervals[-args.freq:]) / args.freq
                actual_hz = 1.0 / avg_dt
                print(f"当前实时频率: {actual_hz:.2f} Hz | 间隔: {avg_dt*1000:.2f} ms")

            last_time = t_now
            count += 1

            # 4. 精确频率控制 (计算补偿休眠时间)
            elapsed = time.time() - t_loop_start
            sleep_time = (1.0 / args.freq) - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n测试被用户中断")

    finally:
        end_test_time = time.time()
        actual_total_hz = count / (end_test_time - start_test_time)
        
        print("\n--- 测试报告 ---")
        print(f"总计帧数: {count}")
        print(f"平均控制频率: {actual_total_hz:.2f} Hz")
        if len(intervals) > 0:
            max_dt = max(intervals) * 1000
            min_dt = min(intervals) * 1000
            print(f"最大延迟 (Max Latency): {max_dt:.2f} ms")
            print(f"最小延迟 (Min Latency): {min_dt:.2f} ms")
            print(f"抖动范围 (Jitter): {max_dt - min_dt:.2f} ms")

        arm.set_state(state=4) # 停止机械臂
        arm.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='192.168.1.244')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='YAML file path')
    parser.add_argument('--freq', type=int, default=100, help='目标频率 Hz')
    args = parser.parse_args()
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        args.ip = config.get('ip')
        args.freq = config.get('freq', args.freq)

    main(args)