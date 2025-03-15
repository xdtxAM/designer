#include <Arduino.h>
#include <HardwareSerial.h>


// UART 1，语音模块
HardwareSerial yuyinSerial(PA10, PA9);  // 调试串口

// 创建串口对象，使用USART3
HardwareSerial espSerial(PB11, PB10);  // RX, TX

// USART2，和串口调试-共用接口
HardwareSerial screenSerial(PA3, PA2);  // RX, TX

void setup() {
    //================串口初始化==================
    yuyinSerial.begin(115200);
    espSerial.begin(115200);
    screenSerial.begin(115200);
}

void loop() {
    //=================读取 esp8266 串口数据
    if (espSerial.available()) {
        delay(10);
        String data = espSerial.readStringUntil('\n');
        data.trim();
    }

    //=================读取语音串口数据==================
    if (yuyinSerial.available()) {
        String data = yuyinSerial.readStringUntil('\n');
        screenSerial.print("receive data yuyin");
    }

    //=================获取传感器数据==================
    SensorData data = getSensorData();



    //==================串口屏幕发送代码备份=======================
    screenSerial.print("SET_TXT(2,'");
    screenSerial.print('1');
    screenSerial.println("');");


    //=================发送数据到 esp8266==================
    espSerial.print(data.distance);
    espSerial.print(",");
    espSerial.print(data.ds18b20Temp);
    espSerial.print(",");
    espSerial.println(data.irValue);

    delay(1000);
}
