import RPi.GPIO as GPIO
import time

# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)

# 定义GPIO引脚
TRIG = 17
ECHO = 27

# 设置引脚模式
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # 确保触发引脚处于低电平
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    
    # 发送10us的触发信号
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # 记录发送时间和接收时间
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    # 计算时间差
    pulse_duration = pulse_end - pulse_start
    
    # 计算距离：声速 = 343m/s = 34300cm/s
    # 距离 = (时间 × 声速) / 2
    distance = pulse_duration * 17150
    # 转换成整数
    distance = int(distance)

    
    return distance

if __name__ == "__main__":
    try:
        while True:
            dist = get_distance()
            print(f"距离: {dist} 厘米")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("程序已停止")
        GPIO.cleanup() 
