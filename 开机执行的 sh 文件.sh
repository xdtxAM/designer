#!/bin/bash

# 激活虚拟环境「在任何位置都可以」
source /home/pi/Desktop/MineSetting/bin/activate

# 切换到目标目录「进入目标程序的工作目录」
cd /home/pi/Desktop/mineCode

# & 命令会让 test.py 在后台运行，不阻塞后续命令的执行
python test.py &

# 等待一小段时间确保 test.py 启动（可选，调整时间）
sleep 1

# 执行下一段程序
python pi_homekit.py

# ！！！，必须授予可执行权限
# chmod +x 文件名.sh
