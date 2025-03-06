import paho.mqtt.client as mqtt
import json
import time
import random
# 参数
profile_name = "test1"
product_id = "NQQFOOYZ55"  # 请替换为你的产品 ID
device_name = "STM32"  # 请替换为你的设备名称
broker_address = f"{product_id}.iotcloud.tencentdevices.com"
broker_port = 1883
client_id = f"{product_id}{device_name}"
username = "NQQF12OOYZ55STM32;12010126;AC12GVZ;17403227702"  # 请替换为你的用户名
password = "accd0960e3e3ae1f2bbf1706324f876044e499c6313469bece5814fd9e5b2127bd;hmacsha256"  # 请替换为你的密码
connection_timeout = 60  # 连接超时时间（秒）
keep_alive_interval = 60  # 心跳间隔时间（秒）
auto_reconnect = True  # 断网自动重连

# MQTT 事件回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    elif rc == 5:
        print("Connection refused - not authorised. Check your username and password.")
    else:
        print(f"Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode('utf-8')}")

# 创建 MQTT 客户端
client = mqtt.Client(client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# 连接到 MQTT Broker
print(f"Connecting to broker {broker_address} with client ID {client_id}")
client.connect(broker_address, broker_port, connection_timeout)

# 开启自动重连
client.reconnect_delay_set(min_delay=1, max_delay=120)

# 启动 MQTT 客户端
client.loop_start()

# 订阅主题
topic_to_subscribe = f"$thing/down/property/{product_id}/{device_name}"
print(f"Subscribing to topic {topic_to_subscribe}")
client.subscribe(topic_to_subscribe)

# 发布消息
topic_to_publish = f"$thing/up/property/{product_id}/{device_name}"



print(f"Publishing to topic {topic_to_publish}")

# 保持客户端运行
try:
    while True:
        # 组装 json 消息 data 
        data = {
            "method":"report",
            "clientToken":"123",
            "timestamp":1628646783,
            "params":{
                "te": 0
            }
        }
        # 将 data 转换为 json 字符串
        data_json = json.dumps(data)
        print(f"Publishing to topic {topic_to_publish}")
        client.publish(topic_to_publish, data_json)
        time.sleep(5)
except KeyboardInterrupt:
    print("Disconnecting from MQTT Broker...")
    client.loop_stop()
    client.disconnect()
