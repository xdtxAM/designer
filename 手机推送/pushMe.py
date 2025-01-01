import requests

def send_push_notification():
    # API endpoint
    url = "https://push.i-i.me"
    
    # Your push key
    push_key = "STR4hzBd25TfIjkzZNvT"
    
    # Message details
    title = "[f]饲料不足警告"  # [f] indicates failure level alert
    content = "检测到饲料过低，请管理员及时补充"
    
    # Request parameters
    params = {
        "push_key": push_key,
        "title": title,
        "content": content
    }
    
    try:
        # Send GET request
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            print("通知发送成功")
        else:
            print(f"通知发送失败: {response.status_code}")
            
    except Exception as e:
        print(f"发送出错: {str(e)}")

if __name__ == "__main__":
    send_push_notification()
