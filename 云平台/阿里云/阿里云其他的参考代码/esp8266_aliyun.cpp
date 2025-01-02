#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi配置
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 阿里云IoT配置
const char* mqtt_server = "a1sE2uDnUsF.iot-as-mqtt.cn-shanghai.aliyuncs.com";
const int mqtt_port = 1883;
const char* product_key = "a11kATWqNc2";
const char* device_name = "STM32";
const char* device_secret = "67a5b4b504349ee46eb63e46802fbf0827bc79ac0a0e11d2225a1ed2f8c20435";

// MQTT客户端
WiFiClient espClient;
PubSubClient client(espClient);

// 函数声明
void callback(char* topic, byte* payload, unsigned int length);
void connectMQTT();
void postProperty(bool state);
void reconnect();

// 消息回调
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';
  Serial.println(message);

  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  
  if (!error) {
    if(doc.containsKey("params")) {
      JsonObject params = doc["params"];
      if(params.containsKey("LEDSwitch")) {
        bool ledState = params["LEDSwitch"];
        digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
      }
    }
  }
}

// 连接MQTT服务器
void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // 构建MQTT连接参数
    String clientId = String(product_key) + "." + String(device_name) + 
                     "|securemode=2,signmethod=hmacsha256,timestamp=1735661355281|";
    String username = String(device_name) + "&" + String(product_key);
    
    Serial.println("ClientId: " + clientId);
    Serial.println("Username: " + username);
    
    if (client.connect(clientId.c_str(), username.c_str(), device_secret)) {
      Serial.println("connected");
      
      // 订阅主题
      String subscribe_topic = String("/sys/") + product_key + "/" + device_name + "/thing/service/property/set";
      client.subscribe(subscribe_topic.c_str());
      
      // 发布测试消息
      StaticJsonDocument<200> doc;
      doc["id"] = "1";
      doc["version"] = "1.0";
      doc["params"]["temp"] = 1;
      doc["params"]["humi"] = 1;
      doc["params"]["Fan"] = 1;
      doc["params"]["Mode"] = 0;
      doc["params"]["Meiju"] = 1;

      String publish_topic = String("/sys/") + product_key + "/" + device_name + "/thing/event/property/post";
      char buffer[256];
      serializeJson(doc, buffer);
      client.publish(publish_topic.c_str(), buffer);
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// 发送属性数据
void postProperty(bool state) {
  StaticJsonDocument<200> doc;
  doc["id"] = String(millis());  // 使用时间戳作为消息ID
  doc["version"] = "1.0";
  doc["method"] = "thing.event.property.post";  // 添加method字段
  JsonObject params = doc.createNestedObject("params");
  params["LEDSwitch"] = state ? 1 : 0;
  
  String topic = String("/sys/") + product_key + "/" + device_name + "/thing/event/property/post";
  
  char jsonBuffer[256];
  serializeJson(doc, jsonBuffer);
  
  Serial.print("Publishing message: ");
  Serial.println(jsonBuffer);
  
  if(client.publish(topic.c_str(), jsonBuffer)) {
    Serial.println("Property published successfully");
  } else {
    Serial.println("Property publish failed");
  }
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
  
  // 设置MQTT保持连接时间
  client.setKeepAlive(120);  // 设置为120秒
}

void loop() {
  if (!client.connected()) {
    connectMQTT();
  }
  client.loop();
  
  if (Serial.available()) {
    char cmd = Serial.read();
    switch(cmd) {
      case '1':
        postProperty(true);
        break;
      case '0':
        postProperty(false);
        break;
    }
  }
  
  // 增加调试信息
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    Serial.print("MQTT State: ");
    Serial.println(client.state());  // 打印MQTT连接状态
  }
  
  delay(100);
} 