#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Wi-Fi配置
const char* ssid = "test";
const char* password = "test123456";

// MQTT配置
const char* mqttServer = "bj-2-mqtt.iot-api.com";
const int mqttPort = 1883;
const char* mqttUser = "o12vhomhsri0nlii";
const char* mqttPassword = "cKqv7Z7Ypc";

// 创建客户端实例
WiFiClient espClient;
PubSubClient client(espClient);

// 串口通信配置
SoftwareSerial SerialESP(4, 5);  // RX = GPIO4 (D1), TX = GPIO5 (D2)

// 数据发送间隔
unsigned long previousMillis = 0;
const long interval = 5000;  // 5秒

// 全局控制变量
int state = 0;
bool PC13 = false;
bool switch1 = false;
bool switch2 = false;
int value1 = 0;
bool up = false;    // 上传数据开关

// 定义与STM32相同的数据结构
struct __attribute__((packed)) SensorData {
    float test1;
    float test2;
    float test3;
    float test4;
    float test5;
    float test6;
};

// 用于存储接收到的传感器数据
SensorData sensorData;

void setup() {
    Serial.begin(115200);  // 调试用串口
    SerialESP.begin(115200);  // STM32通信串口
    
    // 连接WiFi
    setupWiFi();
    
    // 设置MQTT服务器
    client.setServer(mqttServer, mqttPort);
    client.setCallback(callback);
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    // 检查是否有来自STM32的数据
    if (SerialESP.available() >= sizeof(SensorData) + 1) {  // +1 是校验和

        Serial.println("Data received from STM32");

        // 间隔发送数据，如果up为true则上传数据
        unsigned long currentMillis = millis();  // 获取当前时间
        if (currentMillis - previousMillis >= interval) {  // 如果 当前时间 - 上次发送时间 >= 间隔时间
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
        Serial.println("test1: " + String(sensorData.test1));
        
    }

}

void setupWiFi() {
    WiFi.begin(ssid, password);
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
    doc["test1"] = round(sensorData.test1 * 10.0) / 10.0;
    doc["test2"] = round(sensorData.test2 * 10.0) / 10.0;
    doc["test3"] = round(sensorData.test3 * 10.0) / 10.0;
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

// MQTT回调函数，处理接收到的数据
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
        if (client.connect("ESPClient", mqttUser, mqttPassword)) {
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