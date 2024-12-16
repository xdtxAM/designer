// config.h
#ifndef CONFIG_H
#define CONFIG_H

//============================ 网络配置 ============================
// Wi-Fi配置
#define WIFI_SSID "esp8266"
#define WIFI_PASSWORD "esp123456"
//============================ 网络配置 ============================



//============================ 云平台配置 ============================
// MQTT配置
#define MQTT_SERVER "bj-2-mqtt.iot-api.com"
#define MQTT_PORT 1883
#define MQTT_USER "o12vhomhsri0nlii"
#define MQTT_PASSWORD "cKqv7Z7Ypc"
//============================ 云平台配置 ============================


//============================ 串口配置 ============================
// 串口通信引脚配置
#define SERIAL_RX 4  // GPIO4 (D1)
#define SERIAL_TX 5  // GPIO5 (D2)
//============================ 串口配置 ============================



// 数据发送间隔配置
#define DATA_SEND_INTERVAL 5000  // 5秒

#endif