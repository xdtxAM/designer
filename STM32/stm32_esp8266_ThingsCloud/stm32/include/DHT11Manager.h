// DHT11Manager.h
#ifndef DHT11_MANAGER_H
#define DHT11_MANAGER_H

#include <DHT.h>
#include "PinConfig.h"

class DHT11Manager {
public:
    DHT11Manager(uint8_t pin) : _dht(pin, DHT11) {}

    void begin() {
        _dht.begin();
    }

    float getTemperature() {
        return _dht.readTemperature();
    }

    float getHumidity() {
        return _dht.readHumidity();
    }

private:
    DHT _dht;
};

#endif