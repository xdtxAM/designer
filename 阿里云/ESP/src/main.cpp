#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// WiFi配置
const char* ssid = "test";
const char* password = "test123456";

// 阿里云 IoT 配置
const char* mqtt_server = "a1nLOR1Vk0z.iot-as-mqtt.cn-shanghai.aliyuncs.com";
const int mqtt_port = 1883;
const char* product_key = "a1nLOR1Vk0z";
const char* device_name = "stm32";
const char* device_secret = "e49eacd3e8eff86fe611064d1be18478ab28cfcc728701406808befe17b12b02";
// MQTT客户端
WiFiClient espClient;
PubSubClient client(espClient);

// 定义通信引脚
// 软件串口
SoftwareSerial stm32Serial(4, 5); // (RX, TX)，4是D2，5是D1

// 串口接收缓冲区
String inputString = "";         // 完整的输入字符串
boolean stringComplete = false;  // 是否接收完成

// 函数声明
void callback(char* topic, byte* payload, unsigned int length);
void connectMQTT();
void postProperty(const String& jsonString);
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
      //把doc["params"]转换为字符串
      String params = doc["params"].as<String>();
      //通过stm32Serial发送params
      Serial.println(params);
      stm32Serial.println(params);
    }
  }
}

// 连接MQTT服务器
void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // 构建MQTT连接参数
    String clientId = String(product_key) + "." + String(device_name) + 
                     "|securemode=2,signmethod=hmacsha256,timestamp=1747206491077|";
    String username = String(device_name) + "&" + String(product_key);
    
    Serial.println("ClientId: " + clientId);
    Serial.println("Username: " + username);
    
    if (client.connect(clientId.c_str(), username.c_str(), device_secret)) {
      Serial.println("connected");
      
      // 订阅主题
      String subscribe_topic = String("/sys/") + product_key + "/" + device_name + "/thing/service/property/set";
      client.subscribe(subscribe_topic.c_str());
      
      // 发布测试消息
      // mode  hw1 hw2 hw3 lig led1 led2 led3 ly
      StaticJsonDocument<200> doc;
      doc["id"] = "1";
      doc["version"] = "1.0";
      doc["params"]["mode"] = 0;
      doc["params"]["hw1"] = 0;
      doc["params"]["hw2"] = 0;
      doc["params"]["hw3"] = 0;
      doc["params"]["lig"] = 0;
      doc["params"]["led1"] = 0;
      doc["params"]["led2"] = 0;
      doc["params"]["led3"] = 0;
      doc["params"]["ly"] = 50;

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

// 修改postProperty函数，接收字符串参数而不是bool
void postProperty(const String& jsonString) {
  // 增加文档大小
  StaticJsonDocument<512> receivedDoc;
  StaticJsonDocument<512> sendDoc;
  
  // 添加详细的错误处理
  DeserializationError error = deserializeJson(receivedDoc, jsonString);
  if (error) {
    Serial.print("JSON解析失败: ");
    Serial.println(error.c_str());
    Serial.println("接收到的数据: ");
    Serial.println(jsonString);
    return;
  }

  // 打印成功解析的数据以便调试
  Serial.println("Have received data:");
  serializeJsonPretty(receivedDoc, Serial);
  Serial.println();

  // 构建发送给云平台的消息
  sendDoc["id"] = "1";
  sendDoc["version"] = "1.0";
  sendDoc["method"] = "thing.event.property.post";
  
  JsonObject params = sendDoc.createNestedObject("params");
  params["mode"] = receivedDoc["mode"];
  params["hw1"] = receivedDoc["hw1"];
  params["hw2"] = receivedDoc["hw2"];
  params["hw3"] = receivedDoc["hw3"];
  params["lig"] = receivedDoc["lig"];


  String topic = String("/sys/") + product_key + "/" + device_name + "/thing/event/property/post";
  
  char jsonBuffer[512];
  serializeJson(sendDoc, jsonBuffer);
  
  Serial.print("Publishing message: ");
  Serial.println(jsonBuffer);

  // 发布消息并报告结果
  if(client.publish(topic.c_str(), jsonBuffer)) {
    Serial.println("Property published successfully");
  } else {
    Serial.println("Property publish failed");
  }
}

void setup() {
  Serial.begin(115200);
  stm32Serial.begin(9600);  // 匹配STM32的波特率
  pinMode(LED_BUILTIN, OUTPUT);
  
  // 初始化接收字符串
  inputString.reserve(256);
  
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

  // 采用缓冲读取方式接收串口数据
  while (stm32Serial.available()) {
    char inChar = (char)stm32Serial.read();
    inputString += inChar;
    
    // 判断是否接收到完整的JSON (以换行符结束)
    if (inChar == '\n') {
      stringComplete = true;
      break;
    }
  }
  
  // 处理完整的JSON字符串
  if (stringComplete) {
    inputString.trim();  // 移除首尾空白字符
    
    if (inputString.length() > 0) {
      Serial.println("received data from stm32: " + inputString);
      postProperty(inputString);  // 发送数据到阿里云
    }
    
    // 清空字符串，准备接收下一条数据
    inputString = "";
    stringComplete = false;
  }
  
  // 增加调试信息
  static unsigned long lastMsgMQTT = 0;
  unsigned long nowMQTT = millis();
  if (nowMQTT - lastMsgMQTT > 10000) {  // 增加到10秒一次
    lastMsgMQTT = nowMQTT;
    Serial.print("MQTT State: ");
    Serial.println(client.state());  // 打印 MQTT 连接状态
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));  // 闪烁LED表示程序在运行
  }
  
  delay(10);  // 更小的延迟，提高响应性
}