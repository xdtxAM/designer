from things_MQTT import create_mqtt_client, publish_message
import json
import time


# 创建MQTT客户端
client, message_queue = create_mqtt_client()



def getMqttMessage():
    if not message_queue.empty():
        # 从队列中取出消息
        message = message_queue.get()
        print(f"主程序处理消息: {message}")
        payload = json.loads(message)
        return payload
    return None

if __name__ == "__main__":
    # 发布消息
    publish_message(client, {"mq135": True})

    while True:
        payload = getMqttMessage()
        if payload:
            print(payload)
        time.sleep(0.1)