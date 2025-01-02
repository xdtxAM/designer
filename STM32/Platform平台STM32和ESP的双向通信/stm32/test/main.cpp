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
DeviceController deviceController(PIN_PC13, PIN_PC13_LED_2, PIN_IR_RECEIVE, PIN_MQ135);
DisplayManager displayManager(u8g2);
DHT11Manager dht11Manager(PIN_DHT11);

// 全局变量
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 2000;

// 云平台发下来的数据 float
int cloudData = 0;

// 模式
int mode = 0;

// 亮度
int luminosity = 0;

// 电压
float dianya = 0;

void setup() {
    serialManager.begin();
    deviceController.begin();
    displayManager.begin();
    dht11Manager.begin();
    
    // 设置ADC分辨率为12位
    analogReadResolution(12);
}

void loop() {
    SensorData sensorData;

    // 发送数据到云平台
    if (millis() - lastSendTime >= sendInterval) {
        lastSendTime = millis();

        float temperature = dht11Manager.getTemperature();
        float humidity = dht11Manager.getHumidity();

        sensorData.temperature = temperature;
        sensorData.humidity = humidity;

        // 获取光照传感器值
        float lightSensorValue = analogRead(PIN_LIGHT_SENSOR);
        // 映射 100 - 1500 为 100 - 0，然后反转为 0 - 100，光线越强，值越大
        sensorData.lightSensorValue = 100 - ((lightSensorValue - 100) * 100 / 1500);

        // 获取人体传感器高低电平
        sensorData.peopleSensorValue = digitalRead(PIN_IR_RECEIVE);

        // 获取mq135传感器值
        int mq135SensorValue = analogRead(PIN_MQ135);
        // 取值范围 0 - 4096，映射到 100 - 0，空气质量越好，值越大
        sensorData.mq135SensorValue = 100 - (mq135SensorValue * 100 / 4096);

        serialManager.printToPC("Send data to ESP8266");
        serialManager.sendSensorData(sensorData);

        float dianya = luminosity * 5 / 255;
        sensorData.dianya = dianya;
    }

    // 接收云平台数据
    String receivedData = serialManager.receiveData();
    if (receivedData.length() > 0) {
        serialManager.printToPC("Received data from ESP8266: " + receivedData);

        int colonIndex = receivedData.indexOf(':');
        String key = receivedData.substring(0, colonIndex);
        String value = receivedData.substring(colonIndex + 1);
        value.trim();

        cloudData = value.toFloat();

        if (key == "lightSwi") {
            deviceController.setLedSwitch(value == "1");  // 设置led开关状态，比较字符串是否为"1"，为1则打开，为0则关闭
        }
        else if (key == "luminosity") {
            deviceController.setValue1(value.toInt()); // 设置亮度，0 - 255
            luminosity = value.toInt();
        }
        else if (key == "state") {
            if (value == "1") {
                // 更新mode
                mode = 1;
            }
            else if (value == "0") {
                mode = 0;
            }
        }
    }

    // 如果是模式 1 进入自动模式
    if (mode == 1) {
        if (sensorData.peopleSensorValue == 0) {
            deviceController.setLedSwitch(true);
            // 根据光线强度调整LED亮度
            // lightSensorValue 范围是 0-100，数值越大表示光线越强
            // 我们希望光线越强，LED亮度越低
            int adjustedLuminosity = map(sensorData.lightSensorValue, 0, 100, 255, 0);
            deviceController.setValue1(adjustedLuminosity);
            luminosity = adjustedLuminosity;
        } else {
            deviceController.setLedSwitch(false);
            deviceController.setValue1(0);
        }
    }

    delay(100);

    //===============更新显示屏模块==================
    displayManager.updateValues(
        sensorData.lightSensorValue,
        sensorData.temperature,
        sensorData.humidity,
        sensorData.peopleSensorValue,
        sensorData.mq135SensorValue,
        mode,
        sensorData.dianya
    );
}
