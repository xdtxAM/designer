import paho.mqtt.client as mqtt
import json

# MQTT服务器的连接参数
mqtt_host = "a1sE2uDnUsF.iot-as-mqtt.cn-shanghai.aliyuncs.com"
port = 1883
client_id = "a11kATWqNc2.STM32|securemode=2,signmethod=hmacsha256,timestamp=1735661355281|"
username = "STM32&a11kATWqNc2"
password = "67a5b4b504349ee46eb63e46802fbf0827bc79ac0a0e11d2225a1ed2f8c20435"

# 订阅和发布的topics (修正重复定义)
subscribe_topic = "/sys/a11kATWqNc2/STM32/thing/service/property/set"
publish_topic = "/sys/a11kATWqNc2/STM32/thing/event/property/post"

# 要发布的数据
payload = {
    "id": "1",
    "version": "1.0",
    "params": {
        "temp": 26,
        "humi": 26,
        "Fan": 1,
        "Mode": 0,
        "Meiju": 1
    }
}

# 当与服务器连接成功后调用的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 订阅topic
    client.subscribe(subscribe_topic)
    # 发布消息
    client.publish(publish_topic, json.dumps(payload))
    print(f"Message published to {publish_topic}")

# 当收到从服务器发送的消息时调用的回调函数
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} Message: {str(msg.payload.decode('utf-8'))}")

# 创建MQTT客户端实例
client = mqtt.Client(client_id)

# 设置用户名和密码
client.username_pw_set(username, password)

# 设置连接和消息接收的回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接到MQTT服务器
client.connect(mqtt_host, port, 60)

# 开始循环以处理网络流量、调度回调和处理重新连接
client.loop_forever()
