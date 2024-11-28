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


// 初始化
void setup() {
    // 初始化串口与ESP通信
    SerialESPSTM32.begin(115200);
    // 初始化串口与PC通信
    SerialPC.begin(115200);

    // 初始化LED灯
    pinMode(LED_BUILTIN, OUTPUT);

    // 设置LED灯默认关闭
    digitalWrite(LED_BUILTIN, HIGH);
}


// 定义接收到的数据，全局变量
String receivedData;
// 全局变量定义
int state;


void loop() {
    // 接收 ESP模块 的数据
    if (SerialESPSTM32.available()) {
        String receivedData = SerialESPSTM32.readStringUntil('\n');  // 从ESP模块读取一行数据

        // 解析数据键和值
        int colonIndex = receivedData.indexOf(':');
        String key = receivedData.substring(0, colonIndex);
        String value = receivedData.substring(colonIndex + 1);

        // 使用 trim() 去除多余的空白字符或换行符
        value.trim();
        // 打印到 PC 端
        SerialPC.println("Key: " + key + " Value: " + value);

        if (value == "1") {
            SerialPC.println("value is exactly '1'");
            // 打开 LED 灯
            digitalWrite(LED_BUILTIN, LOW);
        } else {
            SerialPC.println("value is NOT '1'");
            // 关闭 LED 灯
            digitalWrite(LED_BUILTIN, HIGH);
        }

    }
}



