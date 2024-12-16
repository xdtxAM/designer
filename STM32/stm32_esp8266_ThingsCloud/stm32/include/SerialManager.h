// SerialManager.h
#ifndef SERIAL_MANAGER_H
#define SERIAL_MANAGER_H

#include <HardwareSerial.h>
#include "SensorData.h"

class SerialManager {
public:
    SerialManager(HardwareSerial& espSerial, HardwareSerial& pcSerial) 
        : _espSerial(espSerial), _pcSerial(pcSerial) {}

    void begin() {
        _espSerial.begin(115200);
        _pcSerial.begin(115200);
    }

    void sendSensorData(const SensorData& data) {
        uint8_t byteData[sizeof(SensorData)];
        const uint8_t* ptr = reinterpret_cast<const uint8_t*>(&data);

        // 复制数据
        for (size_t i = 0; i < sizeof(SensorData); ++i) {
            byteData[i] = ptr[i];
        }

        // 计算校验和
        uint8_t checksum = 0;
        for (size_t i = 0; i < sizeof(SensorData); i++) {
            checksum ^= byteData[i];
        }

        // 发送数据和校验和
        _espSerial.write(byteData, sizeof(SensorData));
        _espSerial.write(checksum);
    }

    String receiveData() {
        if (_espSerial.available()) {
            return _espSerial.readStringUntil('\n');
        }
        return "";
    }

    void printToPC(const String& message) {
        _pcSerial.println(message);
    }

private:
    HardwareSerial& _espSerial;
    HardwareSerial& _pcSerial;
};

#endif