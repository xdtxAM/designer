import serial
import time


"""
发送文本到串口屏，使用串口通信
参数说明：
1. serial_port: 串口对象，如果是树莓派，可以使用 serial.Serial(port="/dev/serial0", baudrate=115200) 打开串口
2. command: 发送的指令字符串
"""
def send_command(serial_port, command):
    """
    发送指令到串口屏
    :param serial_port: 打开的串口对象
    :param command: 发送的指令字符串
    """
    print(f"发送指令: {command}")
    serial_port.write(command.encode('gb2312'))  # 转换为字节并发送，使用GB2312编码支持中文
    time.sleep(0.1)  # 等待屏幕处理
    # response = serial_port.read(100)  # 读取最多100字节返回
    # if response:
    #     print(f"屏幕返回: {response.decode('utf-8', errors='ignore')}")
    # else:
    #     print("屏幕无返回")

if __name__ == "__main__":
    try:
        # 初始化串口
        ser = serial.Serial(
            port="/dev/serial0",  # 树莓派的UART设备
            baudrate=115200,      # 根据屏幕设置修改波特率
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1             # 超时时间（秒）
        )
        if ser.is_open:
            print("串口已打开")
        while True:
            # 发送指令
            send_command(ser, "SET_TXT(8,'12.1');\r\n")
            send_command(ser, "SET_TXT(3,'22.1');\r\n")
            send_command(ser, "SET_TXT(5,'检测到可燃气体');\r\n")
            time.sleep(1)


    except serial.SerialException as e:
        print(f"串口异常: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()  # 关闭串口
            print("串口已关闭")
