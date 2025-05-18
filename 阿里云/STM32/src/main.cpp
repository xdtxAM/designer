#include <Arduino.h>
#include <ArduinoJson.h>


// 创建全局串口对象
HardwareSerial UartSerial(PA10, PA9);
// 创建 ESP 串口对象，使用USART3
HardwareSerial espSerial(PB11, PB10);  // RX ESP:D1, TX ESP:D2


// 缓冲区大小
#define BUFFER_SIZE 256  // 增加缓冲区大小
// 缓冲区
char jsonBuffer[BUFFER_SIZE];

// 引脚定义，红外-1，红外-2，红外-3
#define RED_PIN1 PA0
#define RED_PIN2 PA1
#define RED_PIN3 PA2

// 引脚定义，led-1，led-2，led-3
#define LED_PIN1 PA3
#define LED_PIN2 PA5
#define LED_PIN3 PA4
// 引脚定义，光线传感器
#define LIG_PIN PA6


// 全局变量
int ly = 50;   // 光照阈值
// 模式
int mode = 0;


void setup() {
  // 初始化串口
  UartSerial.begin(115200);
  espSerial.begin(9600);  // 增加波特率

  UartSerial.println("have started");
  delay(1000);  // 启动延迟

  // 初始化引脚
  pinMode(RED_PIN1, INPUT);
  pinMode(RED_PIN2, INPUT);
  pinMode(RED_PIN3, INPUT);
  pinMode(LED_PIN1, OUTPUT);
  pinMode(LED_PIN2, OUTPUT);
  pinMode(LED_PIN3, OUTPUT);

  

  // 刚开始的时候，LED 全部关闭
  analogWrite(LED_PIN1, 0);
  analogWrite(LED_PIN2, 0);
  analogWrite(LED_PIN3, 0);
}

void loop() {
  // 读取DHT传感器数据，非阻塞，间隔1秒
  // static unsigned long previousMillis_chuanganqi = 0;  // 上次执行的时间
  // const unsigned long interval_chuanganqi = 1000;  // 增加延时时间
  // if (millis() - previousMillis_chuanganqi >= interval_chuanganqi) {
  //   // 读取火焰
  //   int fir = digitalRead(FIR_PIN);
  //   UartSerial.print("fire: ");
  //   UartSerial.println(fir);
  //   previousMillis_chuanganqi = millis();
  // }

  
  // 间隔时间
  static unsigned long previousMillis = 0;  // 上次执行的时间
  const unsigned long interval = 1000;  // 增加延时时间

  // 读取红外传感器数据
  int red1 = !digitalRead(RED_PIN1);
  int red2 = !digitalRead(RED_PIN2);
  int red3 = !digitalRead(RED_PIN3);

  // 读取光线传感器数据
  int lig = analogRead(LIG_PIN);
  int lig_map = map(lig, 50, 1023, 100, 0);

  // 非阻塞延时
  if (millis() - previousMillis >= interval) {
    // 使用ArduinoJson库创建和序列化JSON数据
    StaticJsonDocument<200> doc;
    doc["hw1"] = red1;
    doc["hw2"] = red2;
    doc["hw3"] = red3;
    doc["lig"] = lig_map;

    // 序列化为JSON字符串
    serializeJson(doc, jsonBuffer, sizeof(jsonBuffer));
    
    // 添加换行符
    int len = strlen(jsonBuffer);
    if (len + 1 < BUFFER_SIZE) {
      jsonBuffer[len] = '\n';
      jsonBuffer[len + 1] = '\0';
    }
    
    // 使用 write 发送完整的数据
    UartSerial.print("start send data to esp: ");
    UartSerial.println(jsonBuffer);
    
    espSerial.write(jsonBuffer, strlen(jsonBuffer));
    espSerial.flush();  // 等待所有数据发送完成
    
    previousMillis = millis();
  }

  // 接收和解析 ESP 串口数据————————————————云平台控制逻辑————————————————
  if (espSerial.available()) {
    String data = espSerial.readStringUntil('\n');
    data.trim();  // 移除首尾空白字符
    
    if (data.length() > 0) {
      // 创建JSON文档
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, data);
      
      if (!error) {
        // 打印数据
        UartSerial.println("receive data from esp: " + data);
        // 解析JSON数据，{"led":0}  {"fan":1}  {"jsq":1}
        // 检查并控制 LED
        if (doc.containsKey("led1")) {
          int led1State = doc["led1"];
          if (led1State == 1) {
            analogWrite(LED_PIN1, 255);
          } else {
            analogWrite(LED_PIN1, 0);
          }
        }

        if (doc.containsKey("led2")) {
          int led2State = doc["led2"];
          if (led2State == 1) {
            analogWrite(LED_PIN2, 255);
          } else {
            analogWrite(LED_PIN2, 0);
          }
        }

        if (doc.containsKey("led3")) {
          int led3State = doc["led3"];
          if (led3State == 1) {
            analogWrite(LED_PIN3, 255);
          } else {
            analogWrite(LED_PIN3, 0);
          }
        }

        // 如果是阈值控制，则修改阈值
        if (doc.containsKey("ly")) {
          int lyState = doc["ly"];
          ly = lyState;
          UartSerial.print("Light threshold changed to: ");
          UartSerial.println(lyState);
        }

        // 模式控制
        if (doc.containsKey("mode")) {
          int modeState = doc["mode"];
          mode = modeState;
          // 如果 mode = 0 则关闭所有设备
          if (modeState == 0) {
            // 关闭所有设备
            digitalWrite(LED_PIN1, 0);
            digitalWrite(LED_PIN2, 0);
            digitalWrite(LED_PIN3, 0);
          }
          UartSerial.print("Mode state changed to: ");
          UartSerial.println(modeState);
        }
      } else {
        UartSerial.print("ESP data parse failed: ");
        UartSerial.println(error.c_str());
        UartSerial.println("original data: " + data);
      }

    }
  }

  // 自动模式工作逻辑
  if (mode == 1) {
    // 光敏电阻先测得当前光强，若低于阈值，哪个区域有人，哪个区域灯光打开，其余区域灯光状态呈关闭状态
    if (lig_map < ly) {
      // 哪个区域有人，哪个区域灯光打开，其余区域灯光状态呈关闭状态
      if (red1 == 1) {
        analogWrite(LED_PIN1, 255);
      } else {
        analogWrite(LED_PIN1, 0);
      }
      if (red2 == 1) {
        analogWrite(LED_PIN2, 255);
      } else {
        analogWrite(LED_PIN2, 0);
      }
      if (red3 == 1) {
        analogWrite(LED_PIN3, 255);
      } else {
        analogWrite(LED_PIN3, 0);
      }
    }
    else {
      analogWrite(LED_PIN1, 0);
      analogWrite(LED_PIN2, 0);
      analogWrite(LED_PIN3, 0);
    }
  }
  delay(100);
}