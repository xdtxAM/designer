#include <Arduino.h>
#include <SoftwareSerial.h>

#define BAUD_RATE 115200  // 波特率，需要与STM32发送端保持一致


// 软件串口
SoftwareSerial stm32Serial(4, 5); // (RX, TX)，4是D2，5是D1

void setup() {
  Serial.begin(BAUD_RATE);
  stm32Serial.begin(BAUD_RATE);
  Serial.println("ESP8266 UART接收程序启动");
}

void loop() {

    //====================STM32——给——ESP8266====================
    // 如果收到来自STM32的数据
    if (stm32Serial.available()) {
        // 读取接收到的数据
        String receivedData = stm32Serial.readStringUntil('\n');
        
        // 打印接收到的数据（用于调试）
        Serial.print("Received from STM32: ");
        Serial.println(receivedData);
        

        //===================ESP——给——STM32====================
        // 给STM32回复一个字符串
        stm32Serial.println("I received your data");
    }

    //====================STM32——给——计算机====================
    // STM32 调试，如果ESP的硬件串口有数据，则发送给我的计算机
    if (Serial.available()) {
        String receivedData = Serial.readStringUntil('\n');
        Serial.print("STM32 Debug: ");
        Serial.println(receivedData);
    }
    
  // 适当的延时，避免过于频繁的循环
  delay(100);
}
