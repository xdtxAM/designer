#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 定义高低电平传感器连接的GPIO引脚
GAS_SENSOR_PIN = 18

# 设置引脚为输入，并启用内部上拉电阻
GPIO.setup(GAS_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("xxxx传感器已启动 (GPIO-{}). 按 CTRL+C 退出".format(GAS_SENSOR_PIN))
    
    # 简单循环读取传感器状态
    while True:
        # 读取传感器状态
        if GPIO.input(GAS_SENSOR_PIN):
            print("正常环境，xxx")
        else:
            print("警告！xxxx！")
        
        # 每秒检测一次
        time.sleep(1)

except KeyboardInterrupt:
    print("程序已退出")
finally:
    # 清理GPIO设置
    GPIO.cleanup()
