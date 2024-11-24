import json
import paho.mqtt.client as mqtt
from queue import Queue
import time


"""
ThingsCloud MQTT 通信示例
供其他的 Python 程序调用
已经设定了 if __name__ == "__main__": 用于测试
"""

# MQTT 连接配置
MQTT_HOST = "bj-2-mqtt.iot-api.com"
MQTT_PORT = 1883
PUBLISH_TOPIC = "attributes"
SUBSCRIBE_TOPIC = "attributes/push"

# 不同的参数设置，用户名和密码
MQTT_USERNAME = "7ic4lq0bb6hnzg5y"
MQTT_PASSWORD = "3AIk2tvGje"


# 消息队列，用于保存接收到的消息
message_queue = Queue()

# 连接回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
        client.subscribe(SUBSCRIBE_TOPIC)
    else:
        print(f"连接失败，返回码: {rc}")

# 消息接收回调
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    # print(f"收到消息: {msg.topic} {message}")
    message_queue.put(message)  # 将消息放入队列

# 发布消息
def publish_message(client, data):
    payload = json.dumps(data)
    client.publish(PUBLISH_TOPIC, payload)
    print(f"已发布消息: {payload}")

def create_mqtt_client():
    # 创建 MQTT 客户端并设置回调
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # 连接到 MQTT 服务器
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    # 启动后台线程处理网络
    client.loop_start()
    return client, message_queue


if __name__ == "__main__":
    client, message_queue = create_mqtt_client()
    print("MQTT 客户端已创建")

    # 发布消息
    publish_message(client, {"mq135": True})
    while True:
        # 处理MQTT消息，下发的
        if not message_queue.empty():
            # 从队列中取出消息
            message = message_queue.get()
            print(f"主程序处理消息: {message}")
            payload = json.loads(message)
        
        time.sleep(0.1)
            