import paho.mqtt.client as mqtt
import json
import time
import serial
from sensor import main as monitor_sensor_main
# import RPi.GPIO as GPIO

"""
云平台参数
"""
# 温度：tem
# 湿度：hum
# 火焰：fir
# 空气：mq135
# 红外：peo
# 设防：als

"""
发送文本到串口屏，使用串口通信
"""
def send_command(serial_port, command):
    """
    发送指令到串口屏
    :param serial_port: 打开的串口对象
    :param command: 发送的指令字符串
    """
    # print(f"发送指令: {command}")
    serial_port.write(command.encode('gb2312'))  # 转换为字节并发送，使用GB2312编码支持中文
    time.sleep(0.1)  # 等待屏幕处理
    # response = serial_port.read(100)  # 读取最多100字节返回
    # if response:
    #     print(f"屏幕返回: {response.decode('utf-8', errors='ignore')}")
    # else:
    #     print("屏幕无返回")

# # 初始化串口
# ser = serial.Serial(
#     port="/dev/serial0",  # 树莓派的UART设备
#     baudrate=115200,      # 根据屏幕设置修改波特率
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS,
#     timeout=1             # 超时时间（秒）
# )
# if ser.is_open:
#     print("串口已打开")



# MQTT服务器的连接参数
mqtt_host = "a10onwnZ9IA.iot-as-mqtt.cn-shanghai.aliyuncs.com"
port = 1883
client_id = "a10onwnZ9IA.raspi|securemode=2,signmethod=hmacsha256,timestamp=1757989781152|"
username = "raspi&a10onwnZ9IA"
password = "32242bbf227adb287855d21b69dd4bce7c21b8118059da55b8876851e65a6577"
# 订阅和发布的topics (修正重复定义)
subscribe_topic = "/sys/a10onwnZ9IA/raspi/thing/service/property/set"
publish_topic = "/sys/a10onwnZ9IA/raspi/thing/event/property/post"


"""
全局变量定义
"""
upload_interval = 3



# 当与服务器连接成功后调用的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 订阅topic
    client.subscribe(subscribe_topic)
    print(f"Connected to {mqtt_host}:{port}")

# 当收到从服务器发送的消息时调用的回调函数
def on_message(client, userdata, msg):
    global mode, alarm_distance, alarm_switch
    print(f"Topic: {msg.topic} Message: {str(msg.payload.decode('utf-8'))}")
    # Topic: /sys/a10onwnZ9IA/raspi/thing/service/property/set Message: {"method":"thing.service.property.set","id":"335650181","params":{"fan":1},"version":"1.0.0"}
    # 解析消息
    data = json.loads(msg.payload.decode('utf-8'))['params']
    # 检查各个设备的控制指令

    # 如果下发是 als
    if 'als' in data:
        print(f"设防状态设置为: {data['als']}")
        als = data['als']
        # 更新设防状态到显示屏
        # send_command(ser, f"SET_TXT(5,'{als}');\r\n")


# 串口数据接收处理函数
def handle_serial_data(serial_port):
    if serial_port.in_waiting:  # 检查是否有待处理的数据
        try:
            data = serial_port.readline().decode('gb2312').strip()  # 读取一行数据
            print(f"收到串口数据: {data}")
            return data
        except Exception as e:
            print(f"读取串口数据错误: {e}")
    return None

"""
MQTT 配置
"""
# 创建MQTT客户端实例
client = mqtt.Client(client_id)
# 设置用户名和密码
client.username_pw_set(username, password)
# 设置连接和消息接收的回调函数
client.on_connect = on_connect
client.on_message = on_message
# 在连接到MQTT服务器之前，设置定时发送
client.connect(mqtt_host, port, 60)
# 启动后台网络循环
client.loop_start()

# 定时发送数据
try:
    last_upload_time = time.time()
    while True:
        monitor_sensor_main()
        # 发送数据到串口屏
        # send_command(ser, f"SET_TXT(0,'{distance_left}');\r\n")
        # send_command(ser, f"SET_TXT(1,'{distance_right}');\r\n")
        # send_command(ser, f"SET_TXT(2,'{distance_back}');\r\n")

        # 从文件中读取数据
        with open("sensor.json", "r") as f:
            sensor_data = json.load(f)
        tem = sensor_data["tem"]
        hum = sensor_data["hum"]
        mq135 = sensor_data["mq135"]
        peo = sensor_data["peo"]

        
        # 如果时间间隔大于上传间隔，则上传数据
        if time.time() - last_upload_time >= upload_interval:
            # 构建payload
            payload = {
                "id": "1",
                "version": "1.0",
                "params": {
                    "tem": tem,
                    "hum": hum,
                    "mq135": mq135,
                    "peo": peo
                }
            }
            
            # 发布消息
            client.publish(publish_topic, json.dumps(payload))
            print(f"Message published to {publish_topic}")

            # 更新上传时间
            last_upload_time = time.time()

        # 等待
        time.sleep(0.2)      
except KeyboardInterrupt:
    print("程序已停止")
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()
