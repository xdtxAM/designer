#!/usr/bin/python
# -*- coding: UTF-8 -*-1
import base64
import hashlib
import hmac
import random
import string
import time
import sys
# 生成指定长度的随机字符串
def RandomConnid(length):
    return  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
# 生成接入物联网平台需要的各参数
def IotHmac(productID, devicename, devicePsk):
     # 1. 生成 connid 为一个随机字符串，方便后台定位问题
     connid   = RandomConnid(5)
     # 2. 生成过期时间，表示签名的过期时间,从纪元1970年1月1日 00:00:00 UTC 时间至今秒数的 UTF8 字符串
     expiry   = int(time.time()) + 600 * 60000 * 2
     # 3. 生成 MQTT 的 clientid 部分, 格式为 ${productid}${devicename}
     clientid = "{}{}".format(productID, devicename)
     # 4. 生成 MQTT 的 username 部分, 格式为 ${clientid};${sdkappid};${connid};${expiry}
     username = "{};12010126;{};{}".format(clientid, connid, expiry)
     # 5. 对 username 进行签名，生成token
     secret_key = devicePsk.encode('utf-8')  # convert to bytes
     data_to_sign = username.encode('utf-8')  # convert to bytes
     secret_key = base64.b64decode(secret_key)  # this is still bytes
     token = hmac.new(secret_key, data_to_sign, digestmod=hashlib.sha256).hexdigest()
     # 6. 根据物联网平台规则生成 password 字段
     password = "{};{}".format(token, "hmacsha256")
     return {
        "clientid" : clientid,
        "username" : username,
        "password" : password
     }
if __name__ == '__main__':
    print(IotHmac("YGLZJ7QP7L", "esp32", "bYKGpzuVosjl0WPGBaBvdA=="))
