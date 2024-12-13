#include <HardwareSerial.h>

/********************************************************************************
* STM32 与 ESP8266 通信
* STM32 接收 ESP8266 发送的数据
* 之后，把数据解析后，发送到 PC 端
* 再根据 ESP8266 发送的数据，控制 LED 灯
********************************************************************************/


// 使用PB10作为TX引脚，与ESP模块通信
HardwareSerial SerialESPSTM32(PB11, PB10);  // 11是RX，10是TX
/* 接线说明
STM32 PB11 接收 -> ESP-Mini D1 发送
STM32 PB10 发送 -> ESP-Mini D2 接收
*/

// 和 本地计算机，通过 USB 转 TTL 串口通信
HardwareSerial SerialPC(PA10, PA9);  // 10是RX，9是TX。PA10和USB转TTL的TX连接
/* 接线说明
STM32 PA10 -> USB 转 TTL 模块的 TX
STM32 PA9 -> USB 转 TTL 模块的 RX
*/


// led 灯PC13
#define LED_BUILTIN PC13
// 定义 LED-1 ADC引脚
#define LED_1 PA0

// 定义一个结构体用于存储传感器数据，并确保无字节填充
struct __attribute__((packed)) SensorData {
  float test1;
  float test2;
  float test3;
  float test4;
  float test5;
  float test6;
};


// 函数：给 ESP8266 发送传感器数据
void sendSensorData(const SensorData& data) {
  uint8_t byteData[sizeof(SensorData)];
  const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&data);

  // 复制数据
  for (size_t i = 0; i < sizeof(SensorData); ++i) {
    byteData[i] = ptr[i];
  }

  // 计算简单校验和
  uint8_t checksum = 0;
  for (size_t i = 0; i < sizeof(SensorData); i++) {
    checksum ^= byteData[i];
  }

    // 发送数据和校验和
    SerialESPSTM32.write(byteData, sizeof(SensorData));
    SerialESPSTM32.write(checksum);
}


// 初始化
void setup() {
    // 初始化串口与ESP通信
    SerialESPSTM32.begin(115200);
    // 初始化串口与PC通信
    SerialPC.begin(115200);

    // 初始化LED灯
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(LED_1, OUTPUT);


    // 设置LED灯默认关闭
    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(LED_1, LOW);
}


// 全局变量定义
int state;
// 全局变量定义
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000;  // 5秒发送一次数据


void loop() {

    // 发送传感器数据到 ESP模块
    if (millis() - lastSendTime >= sendInterval) {
        lastSendTime = millis();

        SensorData sensorData; // 传感器数据
        
        // 设置 test1 的数据在 0 - 20 之间，保留一位小数
        sensorData.test1 = random(0, 500) / 10.0;
        sensorData.test2 = random(0, 500) / 10.0;
        sensorData.test3 = random(0, 500) / 10.0;
        sensorData.test4 = random(0, 500) / 10.0;
        sensorData.test5 = random(0, 500) / 10.0;
        sensorData.test6 = random(0, 500) / 10.0;
        
        // 开始发送数据
        SerialPC.println("Send data to ESP8266");

        // 发送传感器数据
        sendSensorData(sensorData); 
    }

    // 接收 ESP模块 的数据
    if (SerialESPSTM32.available()) {
        String receivedData = SerialESPSTM32.readStringUntil('\n');  // 从ESP模块读取一行数据

        // 打印到 PC 端
        SerialPC.println("Received data from ESP8266: " + receivedData);

        // 解析 ESP 发送的
        int colonIndex = receivedData.indexOf(':');
        String key = receivedData.substring(0, colonIndex);
        String value = receivedData.substring(colonIndex + 1);

        // 使用 trim() 去除多余的空白字符或换行符
        value.trim();

        // 打印到 PC 端

        // 如果 key 是 PC13，则控制 LED 灯
        if (key == "PC13") {
            if (value == "1") {
                digitalWrite(LED_BUILTIN, LOW);
            } else {
                digitalWrite(LED_BUILTIN, HIGH);
            }
        }

        // 如果是 value1 根据 value 的值控制 LED 灯亮度
        if (key == "value1") {
            int value1 = value.toInt();
            analogWrite(LED_1, value1);
        }



        // 清空串口缓冲区
        receivedData = "";
    }

    delay(200);
}

