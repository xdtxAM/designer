#!/bin/bash

# 激活虚拟环境
source /home/pi/Desktop/MineSetting/bin/activate

# 切换到目标目录
cd /home/pi/Desktop/mineCode

# 在后台运行 test.py
python test.py &

# 等待一小段时间确保 test.py 启动（可选，调整时间）
sleep 1

# 执行 pi_homekit.py
python pi_homekit.py
