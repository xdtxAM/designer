// SensorData.h
#ifndef SENSOR_DATA_H
#define SENSOR_DATA_H

struct __attribute__((packed)) SensorData {
    float temperature;
    float humidity;
    float irValue;
    float test4;
    float test5;
    float test6;
};

#endif