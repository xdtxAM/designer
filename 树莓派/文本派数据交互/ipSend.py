import requests
import json
import time
import socket


"""
主要功能是：发送树莓派IP地址到在线文本
发送文本内容到在线文本服务器，发送函数是 send_message
"""

# 常量配置
API_CONFIG = {
    'TXT_NAME': 'ceshixiangmu',  # 文本名称
    'PASSWORD': 'admin',  # 密码
    'BASE_URL': 'https://api.txttool.cn/txtpad',  # 在线文本 API 地址
    'VERIFY_URL': '/txt/detail/',  # 验证密码 API 地址
    'SAVE_URL': '/txt/save/',  # 保存 API 地址
    'PORT': 5002  # 树莓派端口
}

def get_ip_address():
    """
    获取树莓派的局域网 IP 地址
    
    返回:
    str: IP 地址
    """
    try:
        # 创建一个临时 socket 连接来获取本机 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"获取IP地址失败: {str(e)}")
        return "未知IP"

def get_access_url():
    """
    获取完整的访问地址
    
    返回:
    str: 格式化的访问地址
    """
    ip = get_ip_address()
    return f"http://{ip}:{API_CONFIG['PORT']}/login"

def send_ip_address():
    """
    发送树莓派访问地址
    
    返回:
    bool: 发送成功返回 True，失败返回 False
    """
    access_url = get_access_url()
    message = f"管理服务器的访问地址是: {access_url}\n\n当前时间是: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    return send_message(message)

def verify_password_and_get_vid():
    """
    验证密码并获取最新的 v_id
    
    返回:
    str or None: 成功返回 v_id，失败返回 None
    """
    url = f"{API_CONFIG['BASE_URL']}{API_CONFIG['VERIFY_URL']}"
    data = {
        "txt_name": API_CONFIG['TXT_NAME'],
        "password": API_CONFIG['PASSWORD']
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == 1:
                return result["data"]["v_id"]
            else:
                print(f"密码验证失败: {result}")
                return None
    except Exception as e:
        print(f"验证密码时发生错误: {str(e)}")
        return None

def send_message(content):
    """
    发送消息到在线文本
    
    参数:
    content (str): 要发送的消息内容
    
    返回:
    bool: 发送成功返回 True，失败返回 False
    """
    # 构造消息格式
    message_list = [
        {
            "title": time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": f"{content}\n"
        }
    ]
    
    # 获取最新的 vid
    last_vid = verify_password_and_get_vid()
    if last_vid is None:
        return False
        
    # 准备请求数据
    url = f"{API_CONFIG['BASE_URL']}{API_CONFIG['SAVE_URL']}"
    data = {
        "txt_name": API_CONFIG['TXT_NAME'],
        "txt_content": json.dumps(message_list),
        "password": API_CONFIG['PASSWORD'],
        "v_id": last_vid
    }
    
    try:
        # 发送 POST 请求
        response = requests.post(url, data=data)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == 1:
                return True
            else:
                print(f"API 返回错误: {result}")
                return False
        else:
            print(f"HTTP 错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"请求发生错误: {str(e)}")
        return False

# 使用示例
if __name__ == "__main__":
    # # 发送访问地址
    # if send_ip_address():
    #     print("访问地址发送成功！")
    #     print(f"当前访问地址: {get_access_url()}")
    # else:
    #     print("访问地址发送失败！")
    send_message("测试发送文本")