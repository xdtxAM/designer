import socket
import subprocess
import platform
import sys
import os

def clear_screen():
    """清除屏幕内容"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_local_ip():
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"获取IP地址时出错: {e}")
        return "127.0.0.1"

def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
        elif system == 'Darwin':
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        elif system == 'Linux':
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
            except FileNotFoundError:
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode('utf-8'), check=True)
                except FileNotFoundError:
                    print("未找到xclip或xsel，请安装其中一个以支持剪贴板功能")
                    return False
        return True
    except Exception as e:
        print(f"复制到剪贴板时出错: {e}")
        return False

def option1():
    """选项1：获取本地IP并生成代理设置"""
    print("正在获取本地IP地址...")
    local_ip = get_local_ip()
    print(f"获取到的IP地址: {local_ip}")
    print()
    
    proxy_cmd = f"export https_proxy=http://{local_ip}:7897 http_proxy=http://{local_ip}:7897 all_proxy=socks5://{local_ip}:7897"
    
    print("生成的代理设置:")
    print(proxy_cmd)
    print()
    
    if copy_to_clipboard(proxy_cmd):
        print("代理设置命令已复制到剪贴板!")
    else:
        print("复制到剪贴板失败，请手动复制上面的命令")
    
    input("\n按Enter键返回主菜单...")

def option2():
    """选项2：复制curl检查Google连接命令"""
    curl_cmd = "curl -I https://www.google.com"
    
    if copy_to_clipboard(curl_cmd):
        print(f'"{curl_cmd}" 已复制到剪贴板!')
    else:
        print("复制到剪贴板失败，请手动复制: curl -I https://www.google.com")
    
    input("\n按Enter键返回主菜单...")

def show_menu():
    """显示主菜单"""
    clear_screen()
    print("================================")
    print("       代理工具菜单")
    print("================================")
    print("1. 获取本地IP并生成代理设置")
    print("2. 复制Google连接检查命令")
    print("3. 退出")
    print("================================")
    print()
    
    choice = input("请输入选项 (1-3): ")
    
    if choice == "1":
        option1()
    elif choice == "2":
        option2()
    elif choice == "3":
        print("感谢使用，再见!")
        sys.exit(0)
    else:
        print("无效的选项，请重新选择。")
        input("按Enter键继续...")

def main():
    """主函数"""
    while True:
        show_menu()

if __name__ == "__main__":
    main()
    
