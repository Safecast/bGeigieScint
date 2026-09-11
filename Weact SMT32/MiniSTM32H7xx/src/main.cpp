#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

// WeAct STM32H7xx 0.96" ST7735 LCD (from omv_boardconfig.h)
#define TFT_CS   PE11
#define TFT_DC   PE13
#define TFT_RST  PF_0
#define TFT_MOSI PE14
#define TFT_SCLK PE12
#define TFT_BL   PE10

Adafruit_ST7735 tft(TFT_CS, TFT_DC, TFT_MOSI, TFT_SCLK, TFT_RST);

void setup() {
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, LOW); // backlight gate is active-low (P-FET high-side switch)

  tft.initR(INITR_MINI160x80);
  tft.setRotation(1);
  tft.fillScreen(ST77XX_BLACK);

  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);
  tft.setCursor(10, 30);
  tft.print("Hello World!");
}

void loop() {
}
