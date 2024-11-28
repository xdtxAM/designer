#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>  // 如果使用ESP8266
#include <PubSubClient.h>
#include <ArduinoJson.h>


// Wi-Fi信息
const char* ssid = "test";             // Wi-Fi名称
const char* password = "test123456";      // Wi-Fi密码

// MQTT服务器信息
const char* mqttServer = "bj-2-mqtt.iot-api.com";
const int mqttPort = 1883;
// 账户和密码
const char* mqttUser = "o12vhomhsri0nlii";  // MQTT用户名
const char* mqttPassword = "cKqv7Z7Ypc";    // MQTT密码

WiFiClient espClient;                // 创建Wi-Fi客户端
PubSubClient client(espClient);      // 创建MQTT客户端

// 数据间隔
unsigned long previousMillis = 0;    // 上一次发送数据的时间
const long interval = 5000;          // 发送间隔：5秒

// 定义ESP8266的接收和发送引脚
SoftwareSerial SerialESP(4, 5);  // 接收使用ESP的D1-GPIO4


//  全局变量，一个是灯开关状态state，一个是亮度PWM，一个是工作模式Mode
int state;
int PWM;
int Mode;

void setup() {
  // 初始化串口
  Serial.begin(115200);  // 用于调试输出
  SerialESP.begin(115200);  // 用于和STM32通信

  // 连接到 Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to Wi-Fi");

  // 设置MQTT服务器及回调函数
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
}

void loop() {

  if (!client.connected()) {
    reconnect();  // 如果未连接，则重新连接MQTT服务器
  }
  client.loop();  // 保持MQTT连接活跃


  // 检查是否有来自STM32的数据
  if (SerialESP.available()) {
    String receivedData = SerialESP.readStringUntil('\n');  // 从STM32读取一行数据
    Serial.println("Received data: " + receivedData);       // 打印接收到的原始数据

    // 如果数据格式是 "lightValue,mq135Value,irValue,voltageValue"
    // 通过逗号分割数据
    parseData(receivedData);
  }
  delay(100);  // 避免过度循环消耗资源
}

// 解析数据并打印各个传感器的值
void parseData(String data) {
  int lightValue, mq135Value, irValue;
  float voltageValue;

  // 按逗号分割字符串
  int firstComma = data.indexOf(',');
  int secondComma = data.indexOf(',', firstComma + 1);
  int thirdComma = data.indexOf(',', secondComma + 1);

  // 解析字符串为不同的数据类型
  if (firstComma > 0 && secondComma > 0 && thirdComma > 0) {
    lightValue = data.substring(0, firstComma).toInt();
    mq135Value = data.substring(firstComma + 1, secondComma).toInt();
    irValue = data.substring(secondComma + 1, thirdComma).toInt();
    voltageValue = data.substring(thirdComma + 1).toFloat();
    // 打印解析后的数据
    // Serial.println("Parsed data:");
    // Serial.println("Light Value: " + String(lightValue));
    // Serial.println("MQ135 Value: " + String(mq135Value));
    // Serial.println("IR Value: " + String(irValue));
    // Serial.println("Voltage Value: " + String(voltageValue));
  } else {
    Serial.println("Error: Invalid data format");
  }

  // 获取当前时间
  unsigned long currentMillis = millis();
  // 每5秒发送一次数据
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    // 4 个数据打包成一个 JSON 格式的字符串
    String message = "{\"lightValue\": " + String(lightValue) + ", \"mq135Value\": " + String(mq135Value) + ", \"irValue\": " + String(irValue) + ", \"voltageValue\": " + String(voltageValue) + "}";
    // 发送消息到指定主题
    if (client.publish("attributes", message.c_str())) {
      Serial.println("Message sent: " + message);
    } else {
      Serial.println("Failed to send message");
    }
  }
}

// 当接收到订阅消息时的回调函数
// 回调函数，当接收到订阅的消息时调用
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);

  // 创建一个动态JSON文档，用于存储解析后的数据
  DynamicJsonDocument doc(256);

  // 将payload转换为字符串
  char message[length + 1];
  strncpy(message, (char*)payload, length);
  message[length] = '\0';

  // 解析收到的JSON消息
  DeserializationError error = deserializeJson(doc, message);

  if (error) {
    Serial.print("Failed to parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // 根据JSON消息的键值，更新全局变量 state, pwm, mode
  if (doc.containsKey("state")) {
    state = doc["state"];
    Serial.println("Received state: " + String(state));
    // 发送状态到STM32
    SerialESP.println("state:" + String(state));
  }

  if (doc.containsKey("PWM")) {
    PWM = doc["PWM"];
    Serial.println("Received PWM: " + String(PWM));
    // 发送PWM到STM32
    SerialESP.println("PWM:" + String(PWM));
  }

  if (doc.containsKey("Mode")) {
    Mode = doc["Mode"];
    Serial.println("Received mode: " + String(Mode));
    // 发送Mode到STM32
    SerialESP.println("Mode:" + String(Mode));
  }

}



// 尝试连接到MQTT服务器
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("ESPClient", mqttUser, mqttPassword)) {
      Serial.println("connected");
      // 订阅一个主题（可根据需要更改）
      client.subscribe("attributes/push");
    } else {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);  // 等待2秒后重试
    }
  }
}