import RPi.GPIO as GPIO
import time

IN_1 = 4
IN_2 = 17
IN_3 = 27
IN_4 = 22

# 使用 BCM 编号方式
GPIO.setmode(GPIO.BCM)

def leftTurn():
    GPIO.setwarnings(False)
    GPIO.setup(IN_1, GPIO.OUT)
    GPIO.setup(IN_2, GPIO.OUT)
    GPIO.setup(IN_3, GPIO.OUT)
    GPIO.setup(IN_4, GPIO.OUT)
    GPIO.output(IN_1, 1)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 1)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 1)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 1)
    time.sleep(0.002)
def rightTurn():
    GPIO.setwarnings(False)
    GPIO.setup(IN_1, GPIO.OUT)
    GPIO.setup(IN_2, GPIO.OUT)
    GPIO.setup(IN_3, GPIO.OUT)
    GPIO.setup(IN_4, GPIO.OUT)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 1)
    time.sleep(0.002)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 1)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)
    GPIO.output(IN_1, 0)
    GPIO.output(IN_2, 1)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)
    GPIO.output(IN_1, 1)
    GPIO.output(IN_2, 0)
    GPIO.output(IN_3, 0)
    GPIO.output(IN_4, 0)
    time.sleep(0.002)

def motorR(manyTime):
    """
    电机向「右」旋转, manyTime 为旋转次数
    旋转半圈, 旋转次数大概为 300
    """
    num = 0
    while num < manyTime:
        leftTurn()
        num = num + 1
def motorL(manyTime):#40
    """
    电机向「左」旋转, manyTime 为旋转次数
    旋转半圈, 旋转次数大概为 300
    """
    num = 0
    while num < manyTime: 
        rightTurn()
        num = num + 1





if __name__ == "__main__":
    try:
        motorR(300)
        time.sleep(1)
        motorL(100)
    except KeyboardInterrupt:
        GPIO.cleanup()
