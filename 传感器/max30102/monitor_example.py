from max30102_master.heartrate_monitor import HeartRateMonitor
import time

def get_latest_reading(measure_time=10):
    """
    获取最新的心率和血氧读数
    Args:
        measure_time: 测量时间（秒）
    Returns:
        tuple: (心率, 血氧) 如果测量失败返回 (0, 0)
    """
    hrm = HeartRateMonitor(print_raw=False, print_result=False)
    
    try:
        hrm.start_sensor()
        time.sleep(measure_time)
        
        # 获取最新的测量结果
        latest_bpm = hrm.bpm  # 当前心率
        latest_spo2 = hrm.spos[-1] if hrm.spos else 0  # 最新血氧值
        
        hrm.stop_sensor()
        return latest_bpm, latest_spo2
        
    except Exception as e:
        print(f"测量出错: {str(e)}")
        if hrm:
            hrm.stop_sensor()
        return 0, 0

if __name__ == "__main__":
    # 使用示例
    bpm, spo2 = get_latest_reading(measure_time=10)
    if bpm > 0 and spo2 > 0:
        print(f"心率: {bpm:.1f} BPM")
        print(f"血氧: {spo2:.1f}%")
    else:
        print("未获取到有效数据") 