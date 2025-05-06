import serial
import time

# 配置串口，选择正确的串口设备和波特率
# lcdser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)  # 根据实际情况调整
voiceser = serial.Serial('/dev/serial0', 115200, timeout=1)  # 根据实际情况调整


# 获取语音识别的返回数据
while True:
    # 获取 RX 串口数据
    # 如果串口有数据
    if voiceser.in_waiting > 0:
        data = voiceser.read()
        print(data)
        # 清空串口缓冲区
        voiceser.flushInput()
    voiceser.write("0".encode('gbk'))  # 转换为字节并发送
    time.sleep(2)
    print(1)
