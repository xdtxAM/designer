#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi配置
const char* ssid = "esp8266";
const char* password = "esp123456";

// 阿里云IoT配置
const char* mqtt_server = "a1sE2uDnUsF.iot-as-mqtt.cn-shanghai.aliyuncs.com";
const int mqtt_port = 1883;
const char* product_key = "a11kATWqNc2";
const char* device_name = "STM32";
const char* device_secret = "67a5b4b504349ee46eb63e46802fbf0827bc79ac0a0e11d2225a1ed2f8c20435";

// MQTT客户端
WiFiClient espClient;
PubSubClient client(espClient);

// MQTT回调函数 - 处理云平台下发的消息
void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    
    // 将接收到的数据转换为字符串
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    Serial.println(message);

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print("deserializeJson() failed: ");
        Serial.println(error.c_str());
        return;
    }

    // 解析 params 中的数据
    if (doc.containsKey("params")) {
        JsonObject params = doc["params"];
        
        // 遍历所有 params 中的键值对
        for (JsonPair kv : params) {
            const char* key = kv.key().c_str();      // 获取属性名
            JsonVariant value = kv.value();          // 获取属性值
            
            // 打印属性名和值
            Serial.print("Property: ");
            Serial.print(key);
            Serial.print(" = ");
            
            // 根据值的类型进行不同处理
            if (value.is<bool>()) {
                bool boolValue = value.as<bool>();
                Serial.println(boolValue ? "true" : "false");
                
                // 处理布尔类型的属性
                if (strcmp(key, "LEDSwitch") == 0) {
                    digitalWrite(LED_BUILTIN, boolValue ? HIGH : LOW);
                }
            }
            else if (value.is<int>()) {
                int intValue = value.as<int>();
                Serial.println(intValue);
                
                // 处理整数类型的属性
                if (strcmp(key, "temp") == 0) {
                    // TODO: 处理温度值
                }
                else if (strcmp(key, "Fan") == 0) {
                    // TODO: 处理风扇速度
                }
            }
            else if (value.is<float>()) {
                float floatValue = value.as<float>();
                Serial.println(floatValue);
            }
            else if (value.is<const char*>()) {
                const char* strValue = value.as<const char*>();
                Serial.println(strValue);
            }
        }
    }
}

// 连接MQTT服务器
void connectMQTT() {
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        String clientId = String(product_key) + "." + String(device_name) + 
                         "|securemode=2,signmethod=hmacsha256,timestamp=1735661355281|";
        String username = String(device_name) + "&" + String(product_key);
        
        if (client.connect(clientId.c_str(), username.c_str(), device_secret)) {
            Serial.println("connected");
            
            // 订阅属性设置主题
            String subscribe_topic = String("/sys/") + product_key + "/" + device_name + "/thing/service/property/set";
            client.subscribe(subscribe_topic.c_str());
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

// 发送属性数据到云平台
template<typename T>
void postProperty(const char* property, T value) {
    StaticJsonDocument<256> doc;
    doc["id"] = String(millis());
    doc["version"] = "1.0";
    doc["method"] = "thing.event.property.post";
    
    JsonObject params = doc.createNestedObject("params");
    params[property] = value;  // 现在可以接受任何类型的值
    
    String topic = String("/sys/") + product_key + "/" + device_name + "/thing/event/property/post";
    char jsonBuffer[256];
    serializeJson(doc, jsonBuffer);
    
    client.publish(topic.c_str(), jsonBuffer);
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    
    // 连接WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    
    // 配置MQTT服务器
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
    client.setKeepAlive(120);
}

void loop() {
    if (!client.connected()) {
        connectMQTT();
    }
    client.loop();
    
    // 处理串口命令
    if (Serial.available()) {
        char cmd = Serial.read();
        switch(cmd) {
            case '1':
                postProperty("LEDSwitch", true); // 将true作为布尔值发送
                break;
            case '0':
                postProperty("LEDSwitch", false); // 将false作为布尔值发送
                break;
        }
    }
    
    delay(100);
} 