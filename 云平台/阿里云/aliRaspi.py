import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from main import main

# MQTT配置
mqtt_host = "a1DWH3V55C6.iot-as-mqtt.cn-shanghai.aliyuncs.com"
port = 1883
client_id = "a1DWH3V55C6.rasp|securemode=2,signmethod=hmacsha256,timestamp=1745768512115|"
username = "rasp&a1DWH3V55C6"
password = "e3866c4a79b2da574bbecd90d10e18bf88dbcf336061547bc6b1917ff3425191"

# MQTT topics
subscribe_topic = "/sys/a1DWH3V55C6/rasp/thing/service/property/set"
publish_topic = "/sys/a1DWH3V55C6/rasp/thing/event/property/post"

# 全局变量
client = None
mode = 0
shelf = 0
led = 0
light_value = 0
water_value = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(subscribe_topic)
    
def on_message(client, userdata, msg):
    global mode, shelf, led
    try:
        message = json.loads(msg.payload.decode('utf-8'))
        print(message)
                
    except json.JSONDecodeError:
        print("消息格式错误，无法解析JSON")
    except Exception as e:
        print(f"处理消息时出错: {str(e)}")
        
def publish_status(distance_front,distance_left,distance_right,light_status,tilt_status,red):
    payload = {
        "id": "1",
        "version": "1.0",
        "params": {
            "qd": distance_front,
            "zd": distance_left,
            "yd": distance_right,
            "lig": light_status,
            "dd": tilt_status,
            "bj":red
        }
    }
    client.publish(publish_topic, json.dumps(payload))
    print(payload)

def setup_mqtt():
    global client
    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message

def pub():
    setup_mqtt()
    client.connect(mqtt_host, port, 60)
    client.loop_start()

    try:
        last_publish_time = time.time()
        while True:
            distance_front,distance_left,distance_right,light_status,tilt_status,red = main() 
            current_time = time.time()
            if current_time - last_publish_time >= 1:  # 每3秒发送一次   
                publish_status(distance_front,distance_left,distance_right,light_status,tilt_status,red)
                last_publish_time = current_time
            
    except KeyboardInterrupt:
        print("程序终止")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    while True:
        pub()
