import sys
from linkkit import linkkit
import logging
import json

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)

lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key="a11kATWqNc2",
    device_name="STM32",
    device_secret="d607129988ba41372dc8800e652a4ac2")

# 配置日志
lk.enable_logger(logging.DEBUG)

# 配置mqtt连接参数
lk.config_mqtt(
    port=1883,
    protocol="MQTTv311",
    transport="TCP",
    secure="",
    keep_alive=60,
    clean_session=True,
    max_inflight_message=20,
    max_queued_message=40,
    auto_reconnect_min_sec=1,
    auto_reconnect_max_sec=60
)

def on_device_dynamic_register(rc, value, userdata):
    print("dynamic register device success, rc:%d, value:%s" % (rc, value))

def on_connect(session_flag, rc, userdata):
    print("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))
    # 订阅属性上报响应
    topic = '/sys/%s/%s/thing/event/property/post_reply' % (
        lk._LinkKit__product_key, 
        lk._LinkKit__device_name
    )
    lk.subscribe_topic(topic)

def on_disconnect(rc, userdata):
    print("on_disconnect:rc:%d,userdata:" % rc)

def on_topic_message(topic, payload, qos, userdata):
    print("收到消息:")
    print("主题:", topic)
    print("内容:", str(payload, 'utf-8'))
    print("QoS:", qos)
    
    # 解析收到的消息
    try:
        data = json.loads(str(payload, 'utf-8'))
        if 'params' in data:
            print("解析后的参数:", data['params'])
    except json.JSONDecodeError:
        print("消息不是JSON格式")

def on_subscribe_topic(mid, granted_qos, userdata):
    print("on_subscribe_topic mid:%d, granted_qos:%s" %
          (mid, str(','.join('%s' % it for it in granted_qos))))

def on_unsubscribe_topic(mid, userdata):
    print("on_unsubscribe_topic mid:%d" % mid)

def on_publish_topic(mid, userdata):
    print("on_publish_topic mid:%d" % mid)

# 注册回调函数
lk.on_device_dynamic_register = on_device_dynamic_register
lk.on_connect = on_connect
lk.on_disconnect = on_disconnect
lk.on_topic_message = on_topic_message
lk.on_subscribe_topic = on_subscribe_topic
lk.on_unsubscribe_topic = on_unsubscribe_topic
lk.on_publish_topic = on_publish_topic

# 连接前配置
lk.config_device_info("STM32_Python_Device")

# 建立连接
lk.connect_async()

def post_property(state=True):
    """上报布尔属性到云平台（使用0/1表示）"""
    # 使用 0/1 表示布尔状态
    payload = "{\"id\":\"1\",\"version\":\"1.0\",\"params\":{\"LEDSwitch\":%d}}" % (1 if state else 0)
    
    # 构建完整topic
    topic = f'/sys/{lk._LinkKit__product_key}/{lk._LinkKit__device_name}/thing/event/property/post'
    
    # 发布消息
    rc, mid = lk.publish_topic(topic, payload)
    
    if rc == 0:
        print(f"布尔状态上报成功, 状态:{state}, mid:{mid}")
    else:
        print(f"布尔状态上报失败:{rc}")

def post_temp_array():
    """上报温度数组到云平台"""
    # 生成10个浮点数的温度数组（示例值）
    temp_array = [round(20.5 + i * 0.5, 2) for i in range(10)]  # 生成10个浮点数
    
    # 构建消息内容
    payload = {
        "id": "1",
        "version": "1.0",
        "params": {
            "tempArry": temp_array
        }
    }
    
    # 构建完整topic
    topic = f'/sys/{lk._LinkKit__product_key}/{lk._LinkKit__device_name}/thing/event/property/post'
    
    # 发布消息
    rc, mid = lk.publish_topic(topic, json.dumps(payload))
    
    if rc == 0:
        print(f"温度数组上报成功, mid:{mid}")
        print(f"上报的数组: {temp_array}")
    else:
        print(f"温度数组上报失败:{rc}")

# 修改主循环，添加数组上报选项
while True:
    try:
        msg = input("输入命令(1:断开连接 2:重连 3:发送消息 4:上报开启状态 5:上报关闭状态 6:上报温度数组 q:退出)> ")
        if msg == "1":
            lk.disconnect()
        elif msg == "2":
            lk.connect_async()
        elif msg == "3":
            payload = '{"message": "hello from device"}'
            lk.publish_topic(lk.to_full_topic("user/update"), payload)
        elif msg == "4":
            post_property(True)  # 上报开启状态
        elif msg == "5":
            post_property(False)  # 上报关闭状态
        elif msg == "6":
            post_temp_array()  # 上报温度数组
        elif msg.lower() == 'q':
            lk.disconnect()
            sys.exit()
        else:
            print("未知命令")
    except KeyboardInterrupt:
        lk.disconnect()
        sys.exit()
