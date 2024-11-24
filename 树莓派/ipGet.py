import socket

"""
获取局域网内的 IP 地址
"""
def get_local_ip():
    try:
        # 创建一个 socket 对象
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公网地址（这里用 Google 的 DNS 服务器 8.8.8.8 和任意端口）
        s.connect(("8.8.8.8", 80))
        # 获取 socket 的本地地址部分
        ip_address = s.getsockname()[0]
        # 关闭 socket
        s.close()
        return ip_address
    except Exception as e:
        return f"无法获取本地 IP 地址: {e}"

if __name__ == "__main__":
    print(f"树莓派的本地 IP 地址: {get_local_ip()}")
