# import adafruit_dht
# import board
import time
import json
import random

"""
引脚连接：
DHT11——GPIO20
"""

def read_dht11():
    dht_device = adafruit_dht.DHT11(board.D20)  # GPIO20
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return humidity, temperature
    except RuntimeError as e:
        # print(f"读取失败: {e}")
        return None, None
    finally:
        dht_device.exit()

# 模拟数据
def read_dht11_mock():
    return random.randint(0, 100), random.randint(0, 100)

def read_mq135_mock():
    return random.randint(0, 1)

def read_peo_mock():
    return random.randint(0, 1)

def get_sensor_data():
    humidity, temperature = read_dht11_mock()
    mq135 = read_mq135_mock()
    peo = read_peo_mock()
    return humidity, temperature, mq135, peo

def main():
    humidity, temperature, mq135, peo = get_sensor_data()
    print(f"湿度: {humidity:.2f}%, 温度: {temperature:.2f}°C, 空气质量: {mq135}, 人体: {peo}")
    time.sleep(1)
    # 保存到文件
    with open("sensor.json", "w") as f:
        json.dump({"hum": humidity, "tem": temperature, "mq135": mq135, "peo": peo}, f)
    time.sleep(1)

# 示例调用
if __name__ == "__main__":
    try:
        while True:
            main()
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序已停止")
        sys.exit(0)