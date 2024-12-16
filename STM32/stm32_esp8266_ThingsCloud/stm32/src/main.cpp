#include <Arduino.h>
#include <HardwareSerial.h>
#include "SensorData.h"
#include "SerialManager.h"
#include "DeviceController.h"
#include "DisplayManager.h"
#include "PinConfig.h"
#include <U8g2lib.h>
#include <DHT.h>
#include "DHT11Manager.h"

// 初始化 I2C SH1106 显示屏
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* SCL=*/ PB6, /* SDA=*/ PB7);

// 串口实例化
HardwareSerial SerialESPSTM32(PB11, PB10);
HardwareSerial SerialPC(PA10, PA9);

// 管理器实例化
SerialManager serialManager(SerialESPSTM32, SerialPC);
DeviceController deviceController(PIN_PC13, PIN_PC13_LED_2);
DisplayManager displayManager(u8g2);
DHT11Manager dht11Manager(PIN_DHT11);

// 全局变量
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000;

// 云平台发下来的数据 float
int cloudData = 0;

void setup() {
    serialManager.begin();
    deviceController.begin();
    displayManager.begin();
    dht11Manager.begin();
}

void loop() {
    SensorData sensorData;

    if (millis() - lastSendTime >= sendInterval) {
        lastSendTime = millis();

        float temperature = dht11Manager.getTemperature();
        float humidity = dht11Manager.getHumidity();

        int irValue = digitalRead(PIN_IR_RECEIVE);

        sensorData.temperature = temperature;
        sensorData.humidity = humidity;
        sensorData.irValue = irValue;
        
        sensorData.test5 = random(0, 500) / 10.0;
        sensorData.test6 = random(0, 500) / 10.0;



        serialManager.printToPC("Send data to ESP8266");
        serialManager.sendSensorData(sensorData);
    }

    String receivedData = serialManager.receiveData();
    if (receivedData.length() > 0) {
        serialManager.printToPC("Received data from ESP8266: " + receivedData);

        int colonIndex = receivedData.indexOf(':');
        String key = receivedData.substring(0, colonIndex);
        String value = receivedData.substring(colonIndex + 1);
        value.trim();

        cloudData = value.toFloat();

        if (key == "PC13") {
            deviceController.setPC13(value == "1");
        }
        else if (key == "value1") {
            deviceController.setValue1(value.toInt());
            // 更新亮度，按照 0 -255 的值，转换为 0 - 100 的值
            sensorData.test4 = value.toInt() * 100 / 255;
        }
    }

    delay(200);

    displayManager.updateValues(cloudData, sensorData.temperature, sensorData.humidity, sensorData.test4);
}
