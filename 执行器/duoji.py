import RPi.GPIO as GPIO
import time


"""
舵机控制程序
设置引脚为BCM模式，设置舵机引脚为输出，初始化PWM信号，频率为50Hz
修改：自定义 SERVO_PIN 引脚
"""
# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)

# 定义GPIO引脚
SERVO_PIN = 23

# 设置舵机引脚为输出
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 初始化PWM信号，频率为50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# 定义函数：将角度转换为占空比
def set_servo_angle(angle):
    # 将角度转换为舵机对应的占空比
    duty_cycle = 2 + (angle / 180) * 10
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # 保证舵机完成动作
    pwm.ChangeDutyCycle(0)  # 停止信号，避免舵机嗡鸣

# 定义函数：直接转动到0度
def move_to_0():
    print("转到 0 度...")
    set_servo_angle(0)

# 定义函数：直接转动到180度
def move_to_90():
    print("转到 90 度...")
    set_servo_angle(90)

if __name__ == '__main__':
    try:
        while True:
            move_to_0()
            time.sleep(1)
            move_to_90()
            time.sleep(1)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
