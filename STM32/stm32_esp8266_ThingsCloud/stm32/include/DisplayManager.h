// DisplayManager.h
#ifndef DISPLAY_MANAGER_H
#define DISPLAY_MANAGER_H

#include <U8g2lib.h>

class DisplayManager {
public:
    DisplayManager(U8G2_SH1106_128X64_NONAME_F_HW_I2C& display) : _display(display) {
        // 光
        static const unsigned char guang[] = {
            0x04,0x00,0x44,0x40,0x24,0x80,0x15,0x00,0x04,0x00,0xFF,0xE0,0x11,0x00,0x11,0x00,0x11,0x00,0x21,0x20,0x41,0x20,0x80,0xE0,/*"光",0*/
            
        };

        // 线
        static const unsigned char xian[] = {
            0x21,0x40,0x21,0x20,0x41,0xE0,0x97,0x00,0xE1,0x00,0x21,0xE0,0x47,0x00,0xF1,0x40,0x01,0x80,0x31,0x20,0xC2,0xA0,0x0C,0x60
        };

        // 温
        static const unsigned char wen[] = {
            0x0F,0x80,0x88,0x80,0x4F,0x80,0x08,0x80,0x0F,0x80,0x80,0x00,0x5F,0xC0,0x15,0x40,0x35,0x40,0x55,0x40,0x95,0x40,0x3F,0xE0
        };

        // 湿
        static const unsigned char shi[] = {
            0x80,0x00,0x5F,0xC0,0x10,0x40,0x1F,0xC0,0x90,0x40,0x5F,0xC0,0x05,0x00,0x25,0x20,0x15,0x40,0x45,0x00,0x85,0x00,0x3F,0xE0
        };

        // 度
        static const unsigned char du[] = {
            0x02,0x00,0x7F,0xE0,0x48,0x80,0x7F,0xE0,0x48,0x80,0x4F,0x80,0x40,0x00,0x5F,0xC0,0x48,0x40,0x44,0x80,0x43,0x00,0x9C,0xE0
        };

        // 模
        static const unsigned char mo[] = {
            /*"模"*/
            0x22,0x80,0x2F,0xE0,0x22,0x80,0xF7,0xC0,0x24,0x40,0x67,0xC0,0x74,0x40,0xA7,0xC0,0x21,0x00,0x2F,0xE0,0x22,0x80,0x2C,0x60
        };

        // 式
        static const unsigned char shi_style[] = {
            /*"式"*/
            0x01,0x40,0x01,0x20,0x01,0x00,0xFF,0xE0,0x01,0x00,0x01,0x00,0x7D,0x00,0x11,0x00,0x10,0x80,0x10,0xA0,0x1E,0x60,0xE0,0x20
        };

        //亮
        static const unsigned char liang[] = {
            /*"亮"*/
            0x04,0x00,0xFF,0xE0,0x00,0x00,0x3F,0x80,0x20,0x80,0x3F,0x80,0x00,0x00,0xFF,0xE0,0x80,0x20,0x3F,0x00,0x21,0x20,0xC0,0xE0
        };

        memcpy(_guang, guang, sizeof(guang));
        memcpy(_xian, xian, sizeof(xian));
        memcpy(_wen, wen, sizeof(wen));
        memcpy(_shidu, shi, sizeof(shi));
        memcpy(_du, du, sizeof(du));
        memcpy(_mo, mo, sizeof(mo));
        memcpy(_shi, shi_style, sizeof(shi_style));
        memcpy(_liang, liang, sizeof(liang));
    }

    void begin() {
        _display.begin();
        _display.enableUTF8Print();
        initializeDisplay();
    }

    void updateValues(int value, float temp, float humi, int brightness) {
        _display.clearBuffer();
        
        // 先画固定的图标
        drawAllIcons();  // 绘制所有固定的图标
        
        // 然后更新变化的数值
        _display.setFont(u8g2_font_7x13_tf);
        
        // 第一行：光照值
        _display.setCursor(30, 10);  // 2 个参数意思：x 轴，y 轴
        _display.print(value, 1);
        _display.print("lux");

        // 第二行：温度
        _display.setCursor(30, 27);
        _display.print(temp, 1);
        _display.print("C");

        // 第三行：湿度
        _display.setCursor(30, 42);
        _display.print(humi, 1);
        _display.print("%");

        // 第 1 行，2 列，显示亮度
        _display.setCursor(90, 10);
        _display.print(brightness);
        _display.print("%");

        _display.sendBuffer();
    }


private:
    void initializeDisplay() {
        _display.clearBuffer();
        _display.setFont(u8g2_font_7x13_tf);
    }

    void drawAllIcons() {
        // 光线
        _display.drawBitmap(1, 1, 2, 16, _guang);
        _display.drawBitmap(15, 1, 2, 16, _xian);

        // 温度
        _display.drawBitmap(1, 15, 2, 16, _wen);
        _display.drawBitmap(15, 15, 2, 16, _du);

        // 湿度
        _display.drawBitmap(1, 31, 2, 16, _shidu);
        _display.drawBitmap(15, 31, 2, 16, _du);

        // 模式
        _display.drawBitmap(1, 47, 2, 16, _mo);
        _display.drawBitmap(15, 47, 2, 16, _shi);

        // 亮度
        _display.drawBitmap(60, 1, 2, 16, _liang);;
        _display.drawBitmap(75, 1, 2, 16, _du);
    }

    U8G2_SH1106_128X64_NONAME_F_HW_I2C& _display;
    unsigned char _guang[32];
    unsigned char _xian[32];
    unsigned char _wen[32];
    unsigned char _shidu[32];
    unsigned char _du[32];
    unsigned char _mo[32];
    unsigned char _shi[32];
    unsigned char _liang[32];
};

#endif