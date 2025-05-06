import adafruit_dht
import board

"""
树莓派
使用 DHT11 传感器读取温湿度数据1
引脚连接：GPIO20
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

# 示例调用
if __name__ == "__main__":
    humidity, temperature = read_dht11()
    if humidity is not None and temperature is not None:
        print(f"湿度: {humidity:.2f}%, 温度: {temperature:.2f}°C")
    else:
        print("未能成功读取数据")
