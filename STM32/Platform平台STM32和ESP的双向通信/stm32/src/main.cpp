#include <Arduino.h>
#include <HardwareSerial.h>

// 创建串口对象，使用USART3
HardwareSerial espSerial(PB11, PB10);  // RX, TX

// 再创建一个串口对象，用于调试
HardwareSerial debugSerial(PA3, PA2);

void setup() {
  espSerial.begin(115200);  // ESP8266通信波特率
  debugSerial.begin(115200);
  delay(1000);  // 等待ESP8266启动
  
  espSerial.println("STM32 Ready!"); // 通过ESP8266发送启动信息
}

void loop() {
    //=========================STM32——给——ESP==========================
    // 发送测试数据到ESP8266
    espSerial.println("Temp:25");

    //=========================STM32——给——调试串口==========================
    // 调试数据发送
    debugSerial.println("Hello Mac Or PC");
    

    //=========================ESP——给——STM32==========================
    // 如果需要接收ESP8266返回的数据
    if (espSerial.available()) {
        String response = espSerial.readStringUntil('\n');
        debugSerial.println(response);
    }
    
    delay(1000);  // 每秒发送一次
}
