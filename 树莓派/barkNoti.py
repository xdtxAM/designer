import requests
import urllib.parse

def bark_notify(title, message):
    """
    发送 Bark 通知
    
    参数:
    title (str): 通知标题
    message (str): 通知内容
    """
    # Bark Key
    bark_key = "Udqvmoy293cs99yWke3oLW"
    
    # 对标题和内容进行 URL 编码
    encoded_title = urllib.parse.quote(title)
    encoded_message = urllib.parse.quote(message)
    
    # 构建请求 URL
    url = f'https://api.day.app/{bark_key}/{encoded_title}/{encoded_message}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("通知发送成功！")
            return True
        else:
            print(f"发送失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"发送出错: {str(e)}")
        return False

# 示例使用
if __name__ == "__main__":
    # 直接调用函数发送通知
    bark_notify("检测到陌生人", "已抓拍并保存到数据库")
