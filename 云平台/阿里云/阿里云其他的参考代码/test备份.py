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

def post_property():
    """上报属性到云平台"""
    # 构建消息内容
    payload = "{\"id\":\"1\",\"version\":\"1.0\",\"params\":{\"key\":1}}"
    
    # 构建完整topic
    topic = f'/sys/{lk._LinkKit__product_key}/{lk._LinkKit__device_name}/thing/event/property/post'
    
    # 发布消息
    rc, mid = lk.publish_topic(topic, payload)
    
    if rc == 0:
        print(f"属性上报成功, mid:{mid}")
    else:
        print(f"属性上报失败:{rc}")

# 在主循环中添加属性上报选项
while True:
    try:
        msg = input("输入命令(1:断开连接 2:重连 3:发送消息 4:上报属性 q:退出)> ")
        if msg == "1":
            lk.disconnect()
        elif msg == "2":
            lk.connect_async()
        elif msg == "3":
            payload = '{"message": "hello from device"}'
            lk.publish_topic(lk.to_full_topic("user/update"), payload)
        elif msg == "4":
            post_property()  # 上报属性
        elif msg.lower() == 'q':
            lk.disconnect()
            sys.exit()
        else:
            print("未知命令")
    except KeyboardInterrupt:
        lk.disconnect()
        sys.exit()
