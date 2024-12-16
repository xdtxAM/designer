// DeviceController.h
#ifndef DEVICE_CONTROLLER_H
#define DEVICE_CONTROLLER_H

#include <Arduino.h>
#include "PinConfig.h"

class DeviceController {
public:
    DeviceController(uint8_t pc13Pin, uint8_t pb0) 
        : _pc13Pin(pc13Pin), _valuePB0(pb0) {}

    void begin() {
        pinMode(_pc13Pin, OUTPUT);
        pinMode(_valuePB0, OUTPUT);
        // 设置初始状态
        digitalWrite(_pc13Pin, HIGH);
        digitalWrite(_valuePB0, LOW);
    }

    void setPC13(bool state) {
        digitalWrite(_pc13Pin, !state);  // 反转逻辑，因为PC13是低电平有效
    }

    void setValue1(int value) {
        analogWrite(_valuePB0, value);
    }

private:
    uint8_t _pc13Pin;
    uint8_t _valuePB0;
};

#endif