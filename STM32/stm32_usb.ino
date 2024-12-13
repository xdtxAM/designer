#include <HardwareSerial.h>

/********************************************************************************
* 使用STM32的串口与计算机通信
* 功能是：每隔1秒向计算机发送 "Hello, World!"
* 使用 usb 转 ttl 模块与计算机和STM32
********************************************************************************/

// 使用PB10作为TX引脚，与ESP模块通信
HardwareSerial SerialESPSTM32(PB11, PB10);  // 11是RX，10是TX
/* 接线说明
STM32 PB11 接收 -> ESP-Mini D1 发送
STM32 PB10 发送 -> ESP-Mini D1 接收
*/

// 和 本地计算机，通过 USB 转 TTL 串口通信
HardwareSerial SerialPC(PA10, PA9);  // 10是RX，9是TX。PA10和USB转TTL的TX连接
/* 接线说明
STM32 PA10 -> USB 转 TTL 模块的 TX
STM32 PA9 -> USB 转 TTL 模块的 RX
*/


void setup()
{
    // 初始化串口与ESP通信
    SerialESPSTM32.begin(115200);
    // 初始化串口与PC通信
    SerialPC.begin(115200);
}

void loop()
{
    // 发送 "Hello, World!" 到 计算机
    SerialPC.println("Hello, World!");   
    // 延时 1 秒
    delay(1000);
}