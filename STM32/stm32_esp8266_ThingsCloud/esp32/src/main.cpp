#include "config.h"
#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// 创建客户端实例
WiFiClient espClient;
PubSubClient client(espClient);

// 串口通信配置
SoftwareSerial SerialESP(SERIAL_RX, SERIAL_TX);

// 时间控制
unsigned long previousMillis = 0;

// 全局控制变量
int state = 0;
bool PC13 = false;
bool switch1 = false;
bool switch2 = false;
int value1 = 0;
bool up = false;  // 上传数据开关，true则上传数据，调用上传数据时候

// 数据结构定义
struct __attribute__((packed)) SensorData {
    float temperature;
    float humidity;
    float irValue;
    float test4;
    float test5;
    float test6;
} sensorData;

// 函数前向声明
void setupWiFi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void readSensorData();
void publishSensorData();

void setup() {
    Serial.begin(115200);
    SerialESP.begin(115200);
    
    setupWiFi();
    
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(callback);
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    // 检查是否有来自STM32的数据
    if (SerialESP.available() >= static_cast<int>(sizeof(SensorData) + 1)) {  // +1 是校验和

        Serial.println("Data received from STM32");

        // 间隔发送数据，如果up为true则上传数据
        unsigned long currentMillis = millis();  // 获取当前时间
        if (currentMillis - previousMillis >= DATA_SEND_INTERVAL) {  // 如果 当前时间 - 上次发送时间 >= 间隔时间
            if (up) {
                readSensorData();
                publishSensorData();
            }
            previousMillis = currentMillis;  //  更新上次发送时间
        }

        // 清空多余的数据
        while (SerialESP.available() > 0) {
            SerialESP.read();
        }

        // 打印一下所有的数据
        Serial.println("temperature: " + String(sensorData.temperature));
        
    }

}

void setupWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");
}


// 读取传感器数据，之后把数据存储到sensorData结构体
void readSensorData() {
    uint8_t receivedChecksum;
    uint8_t calculatedChecksum = 0;
    uint8_t buffer[sizeof(SensorData)];
    
    // 读取数据
    SerialESP.readBytes((uint8_t*)&buffer, sizeof(SensorData));
    // 读取校验和
    receivedChecksum = SerialESP.read();
    
    // 计算校验和
    for (size_t i = 0; i < sizeof(SensorData); i++) {
        calculatedChecksum ^= buffer[i];
    }
    
    // 验证校验和
    if (receivedChecksum == calculatedChecksum) {
        // 数据有效，复制到sensorData结构体
        memcpy(&sensorData, buffer, sizeof(SensorData));
        Serial.println("Data received successfully");
    } else {
        Serial.println("Checksum error");
    }
}

// 发布传感器数据到MQTT
void publishSensorData() {
    // 创建JSON文档
    StaticJsonDocument<200> doc;
    
    // 添加传感器数据
    // 添加传感器数据并限制小数位数为1位
    doc["temperature"] = round(sensorData.temperature * 10.0) / 10.0;
    doc["humidity"] = round(sensorData.humidity * 10.0) / 10.0;
    // "Attribute irValue value type should be boolean"
    doc["irValue"] = sensorData.irValue > 0;
    doc["test4"] = round(sensorData.test4 * 10.0) / 10.0;
    doc["test5"] = round(sensorData.test5 * 10.0) / 10.0;
    doc["test6"] = round(sensorData.test6 * 10.0) / 10.0;

    // 序列化JSON
    char jsonBuffer[200];
    serializeJson(doc, jsonBuffer);
    
    // 发布到MQTT
    if (client.publish("attributes", jsonBuffer)) {
        Serial.println("Published: " + String(jsonBuffer));
    } else {
        Serial.println("Failed to publish");
    }
}

// MQTT回调函数处理接收到的数据
void callback(char* topic, byte* payload, unsigned int length) {
    StaticJsonDocument<200> doc;
    
    // 将payload转换为字符串并解析JSON
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
        Serial.println("JSON parsing failed");
        return;
    }

    // 打印接收到的键和值
    for (JsonPair kv : doc.as<JsonObject>()) {
      Serial.print(kv.key().c_str());
      Serial.print(": ");
      Serial.println(kv.value().as<String>());
    }
    
    // 处理接收到的控制命令
    if (doc.containsKey("state")) {
        state = doc["state"].as<int>();
        SerialESP.print("state: " + String(state));
    }

    if (doc.containsKey("PC13")) {
        PC13 = doc["PC13"].as<int>();
        SerialESP.print("PC13: " + String(PC13));
    }

    if (doc.containsKey("switch1")) {
        switch1 = doc["switch1"].as<int>();
        SerialESP.print("switch1: " + String(switch1));
    }

    if (doc.containsKey("switch2")) {
        switch2 = doc["switch2"].as<int>();
        SerialESP.print("switch2: " + String(switch2));
    }

    if (doc.containsKey("value1")) {
        value1 = doc["value1"].as<int>();
        SerialESP.print("value1: " + String(value1));
    }

    if (doc.containsKey("up")) {
        // 设置 rece 为接收到的值
        up = doc["up"].as<bool>();
    }
}


void reconnect() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT...");
        if (client.connect("ESPClient", MQTT_USER, MQTT_PASSWORD)) {
            Serial.println("connected");
            client.subscribe("attributes/push");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 2 seconds");
            delay(2000);
        }
    }
}