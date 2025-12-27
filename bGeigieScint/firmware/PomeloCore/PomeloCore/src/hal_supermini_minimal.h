/**
 * PomeloCore Ultra-Minimalist HAL for ESP32-C3 Super Mini
 * 
 * This file replaces:
 * 1. External I2C DAC with Internal PWM (Pseudo-DAC)
 * 2. External I2C EEPROM with Internal NVS Flash
 * 3. External GPIO Expander with direct Pin Mapping
 */

#ifndef HAL_SUPERMINI_MINIMAL_H
#define HAL_SUPERMINI_MINIMAL_H

#include <Arduino.h>
#include <Preferences.h> // For internal Flash storage

// ===== PIN DEFINITIONS =====
#define PIN_TRIGGER      6    // Gamma Pulse (Interrupt)
#define PIN_PEAK_ADC     4    // Peak Detector (ADC1_CH4)
#define PIN_HV_PWM       3    // HV Boost PWM
#define PIN_AFE_EN       0    // Analog Front End Power
#define PIN_PEAK_DIS     1    // Peak Detector Disable
#define PIN_RESET_CAP    2    // Peak Det Capacitor Reset
#define PIN_LED          10   // Status LED
#define PIN_DAC_HV       20   // HV Bias (PWM + RC Filter)
#define PIN_DAC_THRESH   21   // Trigger Level (PWM + RC Filter)

// ===== PSEUDO-DAC (PWM) CONFIG =====
const int dac_frequency = 20000; // 20kHz
const int dac_resolution = 12;   // 0-4095 (Matches original SAML21 resolution)

void hal_setup_dac() {
    // Setup PWM channels
    ledcSetup(0, dac_frequency, dac_resolution); // Channel 0 -> HV
    ledcAttachPin(PIN_DAC_HV, 0);

    ledcSetup(1, dac_frequency, dac_resolution); // Channel 1 -> Threshold
    ledcAttachPin(PIN_DAC_THRESH, 1);
}

void hal_set_hv_bias(uint16_t value) {
    ledcWrite(0, value);
}

void hal_set_threshold(uint16_t value) {
    ledcWrite(1, value);
}

// ===== INTERNAL FLASH STORAGE (Preferences) =====
Preferences preferences;

void hal_storage_begin() {
    preferences.begin("pomelo", false); // Namespace "pomelo"
}

void hal_save_params(const void* data, size_t size) {
    preferences.putBytes("params", data, size);
}

void hal_load_params(void* data, size_t size) {
    if (preferences.isKey("params")) {
        preferences.getBytes("params", data, size);
    } else {
        Serial.println("No saved params found, using defaults.");
    }
}

// ===== ANALOG FRONT END INITIALIZATION =====
void hal_init_pins() {
    pinMode(PIN_TRIGGER, INPUT);
    pinMode(PIN_AFE_EN, OUTPUT);
    pinMode(PIN_PEAK_DIS, OUTPUT);
    pinMode(PIN_RESET_CAP, OUTPUT);
    pinMode(PIN_LED, OUTPUT);

    digitalWrite(PIN_AFE_EN, LOW);    // Default OFF
    digitalWrite(PIN_PEAK_DIS, LOW);
    digitalWrite(PIN_RESET_CAP, LOW);
    digitalWrite(PIN_LED, LOW);
}

// ===== ANALOG READ (Internal ADC) =====
uint16_t hal_read_energy() {
    return analogRead(PIN_PEAK_ADC);
}

#endif // HAL_SUPERMINI_MINIMAL_H
