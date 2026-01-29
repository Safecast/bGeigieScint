/**
 * PomeloCore ESP32-C3 Port - Main Application
 * 
 * Converted from SAML21 (ARM Cortex-M0+) to ESP32-C3 (RISC-V)
 * Original: Atmel Software Framework (ASF)
 * Target: Arduino Framework for ESP32
 * 
 * Key Changes:
 * - ASF peripherals → ESP32 Arduino APIs
 * - PORT/GPIO API → digitalWrite/pinMode
 * - ASF NVM → Preferences library
 * - ASF USB CDC → ESP32-C3 native USB CDC
 * - External interrupts (EIC) → attachInterrupt()
 * - Hardware ADC/DAC → ESP32 ADC + external DAC (ESP32-C3 has no DAC)
 */

#include <Arduino.h>
#include <Preferences.h>
#include <Wire.h>
#include <driver/adc.h>
#include <driver/ledc.h>
#include <esp_adc_cal.h>
#include "esp32c3_pinmap.h"
#include "nvm_params.h"

// USB CDC is auto-configured via platformio.ini
// Serial = USB CDC (native ESP32-C3 USB)
// Serial1 = UART1 (external serial)

#define SPECTRUM_LEN        1024
#define LIST_FIFO_LEN       128
#define UART_BUFFER_LEN     128

// List output mode bits
#define LIST_UART_PULSE         0
#define LIST_UART_FAST_PULSE    1
#define LIST_UART_ENERGY        2
#define LIST_UART_ENERGY_TS     3
#define LIST_USB_PULSE          4
#define LIST_USB_ENERGY         5
#define LIST_USB_ENERGY_TS      6

typedef enum _CmdState_t {
    STATE_CMD_IDLE,
    STATE_CMD_PARAM
} CmdState_t;

// Global parameters
static struct core_params coreParams;
static struct physics_params physicsParams;
static Preferences preferences;

static float hvSipmVolts;

#define FILTER_LEN 4
extern const uint16_t pMove[1024][9]; // Spectral deconvolution filter

// ADC calibration
static esp_adc_cal_characteristics_t adc_chars;

// Hardware instances (ESP32 doesn't use module instances like ASF)
static hw_timer_t *rtcTimer = NULL;
static hw_timer_t *hvLoadTimer = NULL;

// Volatile state variables
volatile static uint32_t hvloadTime;
volatile static uint32_t hvloadOn;
volatile static uint32_t hvloadOff;
static bool hvBoost;

volatile static uint32_t gammaTime;
volatile static uint32_t gammaCounts;
volatile static uint32_t gammaSum;
volatile static uint64_t gammaSumSquare;

volatile static uint32_t gammaPulseN, gammaPulseCoincidenceN;
volatile static uint32_t gammaPulseTstart, gammaPulseTstop;
volatile static bool gammaDaqRun, daq_enabled;
volatile static uint32_t gammaSpectrum[SPECTRUM_LEN];
volatile static uint32_t gammaSpectrumCoincidence[SPECTRUM_LEN];
volatile static uint16_t gammaFifo[LIST_FIFO_LEN];
volatile static uint32_t gammaFifoTs[LIST_FIFO_LEN];
volatile static uint16_t gammaFifoHead, gammaFifoTail;
volatile static bool gammaCoincidence;
volatile static bool gammaSyncTrig;
volatile static uint8_t gammaPulseChar;

volatile static uint8_t listOut;
volatile static bool temp_comp_run;

volatile bool usb_connected, can_sleep;

static CmdState_t cmdState;

// UART receive buffer
static volatile uint8_t rxBufHead, rxBufTail;
static volatile uint8_t rxBuf[UART_BUFFER_LEN];

// Forward declarations
void reset_to_bootloader(void);
void pomelo_printf(uint8_t iFace, const char* str);
int pomelo_sprintf(uint8_t iFace, const char* format, ...);
void load_parameters();
void apply_parameters();
void daq_stop(void);

// ============================================================================
// UART Functions (Serial1 = external UART)
// ============================================================================

void uart_init() {
    Serial1.begin(921600, SERIAL_8N1, PIN_UART_RX, PIN_UART_TX);
    rxBufHead = 1;
    rxBufTail = 0;
    
    // ESP32 handles UART interrupts internally via Serial1
    // No manual ISR setup needed
}

bool uart_available() {
    if ((rxBufTail + 1) % UART_BUFFER_LEN != rxBufHead) return true;
    else return false;
}

uint8_t uart_rx() {
    rxBufTail = (rxBufTail + 1) % UART_BUFFER_LEN;
    return rxBuf[rxBufTail];
}

uint8_t uart_tx(const uint8_t *data, uint8_t length) {
    Serial1.write(data, length);
    return length;
}

uint8_t uart_tx(volatile uint8_t *data, uint8_t length) {
    Serial1.write((const uint8_t*)data, length);
    return length;
}

// Task to read UART data into circular buffer
void uart_task() {
    while (Serial1.available()) {
        if (rxBufHead != rxBufTail) {
            rxBuf[rxBufHead] = (uint8_t)Serial1.read();
            rxBufHead = (rxBufHead + 1) % UART_BUFFER_LEN;
        } else {
            Serial1.read(); // Discard if buffer full
        }
    }
}

// ============================================================================
// GPIO and Pin Configuration
// ============================================================================

void gpio_init() {
    // LED
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, HIGH);
    
    // Reset capacitor
    pinMode(PIN_RESET_CAP, OUTPUT);
    digitalWrite(PIN_RESET_CAP, LOW);
    
    // AFE Enable
    pinMode(PIN_AFE_EN, OUTPUT);
    digitalWrite(PIN_AFE_EN, HIGH);
    
    // Peak detector disable
    pinMode(PIN_PEAK_DET_DISABLE, OUTPUT);
    digitalWrite(PIN_PEAK_DET_DISABLE, LOW);
    
    // Ramp generator
    pinMode(PIN_RAMP_EN, OUTPUT);
    digitalWrite(PIN_RAMP_EN, LOW);
    pinMode(PIN_RAMP_TRIG, OUTPUT);
    digitalWrite(PIN_RAMP_TRIG, LOW);
    pinMode(PIN_RAMP_INPUT, INPUT);
    
    // Trigger inputs
    pinMode(PIN_TRIGGER, INPUT);
    pinMode(PIN_SYNC_INPUT, INPUT);
    pinMode(PIN_PEAKDET_EN, INPUT);
    
    // Sync output
    pinMode(PIN_SYNC_OUTPUT, OUTPUT);
    digitalWrite(PIN_SYNC_OUTPUT, LOW);
    
    // HV crowbar (active low)
    pinMode(PIN_HV_CROWBAR, OUTPUT);
    digitalWrite(PIN_HV_CROWBAR, HIGH);
    
    // HV load measurement
    pinMode(PIN_HV_LOAD_MEASURE, INPUT);
    
    // Coincidence input
    pinMode(PIN_COINCIDENCE_IN, INPUT);
    
    // Clear peak detector capacitor (pulse high briefly)
    digitalWrite(PIN_RESET_CAP, HIGH);
    delayMicroseconds(30); // Replace nop() delays with actual microsecond delay
    digitalWrite(PIN_RESET_CAP, LOW);
}

// ============================================================================
// ADC Configuration (ESP32-C3)
// ============================================================================

void adc_init_gamma() {
    // Configure ADC for gamma detection
    adc1_config_width(ADC_WIDTH_BIT_12); // 12-bit ADC (0-4095)
    adc1_config_channel_atten(ADC_CHANNEL_GAMMA, ADC_ATTEN_DB_12); // Full range ~0-3.3V
    adc1_config_channel_atten((adc1_channel_t)ADC_CHANNEL_HV_LOAD, ADC_ATTEN_DB_12);
    
    // Calibrate ADC
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, 1100, &adc_chars);
}

uint16_t adc_read_gamma() {
    return adc1_get_raw(ADC_CHANNEL_GAMMA);
}

uint16_t adc_read_hv_load() {
    return adc1_get_raw((adc1_channel_t)ADC_CHANNEL_HV_LOAD);
}

// ============================================================================
// DAC Configuration (External - ESP32-C3 has NO built-in DAC)
// ============================================================================
// You need to implement external DAC control here (e.g., MCP4725 via I2C)
// This is a placeholder - replace with your actual DAC chip

void dac_init_gamma_hv() {
    // TODO: Initialize external DAC via I2C or SPI
    // Example for MCP4725 (I2C DAC):
    // Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    // Write initialization commands to DAC
    
    Serial.println("WARNING: External DAC initialization needed!");
}

void dac_write_hv(uint16_t value) {
    // TODO: Write to external DAC
    // Example for MCP4725:
    // Wire.beginTransmission(DAC_I2C_ADDRESS);
    // Wire.write((value >> 8) & 0x0F);
    // Wire.write(value & 0xFF);
    // Wire.endTransmission();
}

// ============================================================================
// PWM for HV Boost Converter (Using LEDC)
// ============================================================================

void hv_pwm_init() {
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = LEDC_LOW_SPEED_MODE,
        .duty_resolution  = LEDC_TIMER_10_BIT,
        .timer_num        = (ledc_timer_t)PWM_TIMER_HV,
        .freq_hz          = PWM_FREQ_HV,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&ledc_timer);
    
    ledc_channel_config_t ledc_channel = {
        .gpio_num       = PIN_RAMP_TRIG, // Or dedicated HV PWM pin
        .speed_mode     = LEDC_LOW_SPEED_MODE,
        .channel        = (ledc_channel_t)PWM_CHANNEL_HV,
        .timer_sel      = (ledc_timer_t)PWM_TIMER_HV,
        .duty           = 0,
        .hpoint         = 0
    };
    ledc_channel_config(&ledc_channel);
}

void hv_set_duty(uint16_t duty) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)PWM_CHANNEL_HV, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)PWM_CHANNEL_HV);
}

void hv_disable() {
    hv_set_duty(0);
}

void hv_enable() {
    // Set appropriate duty cycle
    hv_set_duty(512); // Example: 50% duty cycle
}

// ============================================================================
// Interrupt Handlers
// ============================================================================

// Gamma trigger ISR (main detection event)
void IRAM_ATTR gamma_trigger_isr() {
    static uint16_t adcValue;
    static uint16_t channel;
    
    // Read ADC peak detector value
    adcValue = adc1_get_raw(ADC_CHANNEL_GAMMA);
    
    // Clear peak detector capacitor
    digitalWrite(PIN_RESET_CAP, HIGH);
    // Minimal delay in ISR - consider using hardware timer
    digitalWrite(PIN_RESET_CAP, LOW);
    
    // Apply spectral deconvolution filter (pMove)
    // TODO: Implement pMove filter logic here
    
    // Update spectrum histogram
    if (adcValue < SPECTRUM_LEN) {
        gammaSpectrum[adcValue]++;
    }
    
    // Check coincidence input
    if (digitalRead(PIN_COINCIDENCE_IN) == HIGH) {
        gammaCoincidence = true;
        if (adcValue < SPECTRUM_LEN) {
            gammaSpectrumCoincidence[adcValue]++;
        }
        gammaPulseChar = 'C'; // Coincidence marker
    } else {
        gammaPulseChar = 'P'; // Regular pulse
    }
    
    // Update FIFO for list mode
    if (listOut != 0) {
        gammaFifo[gammaFifoHead] = adcValue;
        gammaFifoTs[gammaFifoHead] = micros();
        gammaFifoHead = (gammaFifoHead + 1) % LIST_FIFO_LEN;
    }
    
    // Statistics
    gammaCounts++;
    gammaSum += adcValue;
    gammaSumSquare += (uint64_t)adcValue * adcValue;
}

// Sync trigger ISR
void IRAM_ATTR sync_trigger_isr() {
    // Insert sync marker in FIFO
    if (listOut != 0) {
        gammaFifo[gammaFifoHead] = 9999; // Sync marker
        gammaFifoTs[gammaFifoHead] = micros();
        gammaFifoHead = (gammaFifoHead + 1) % LIST_FIFO_LEN;
    }
}

// RTC timer ISR (1Hz for temperature compensation)
void IRAM_ATTR rtc_timer_isr() {
    temp_comp_run = true;
}

// HV load timer ISR
void IRAM_ATTR hv_load_timer_isr() {
    // HV load monitoring logic
    // TODO: Implement HV boost mode switching
}

// ============================================================================
// Timer Initialization
// ============================================================================

void timer_init_gamma() {
    // RTC Timer: 1Hz for temperature compensation
    rtcTimer = timerBegin(0, 80, true); // Timer 0, prescaler 80 (1MHz), count up
    timerAttachInterrupt(rtcTimer, &rtc_timer_isr, true);
    timerAlarmWrite(rtcTimer, 1000000, true); // 1 second, auto-reload
    timerAlarmEnable(rtcTimer);
    
    // HV Load Timer
    hvLoadTimer = timerBegin(1, 80, true); // Timer 1
    timerAttachInterrupt(hvLoadTimer, &hv_load_timer_isr, true);
    timerAlarmWrite(hvLoadTimer, 10000, true); // 10ms, adjust as needed
    timerAlarmEnable(hvLoadTimer);
}

// ============================================================================
// External Interrupts
// ============================================================================

void eic_init() {
    // Attach interrupt for gamma trigger (rising edge)
    attachInterrupt(digitalPinToInterrupt(PIN_TRIGGER), gamma_trigger_isr, RISING);
    
    // Attach interrupt for sync trigger
    attachInterrupt(digitalPinToInterrupt(PIN_SYNC_INPUT), sync_trigger_isr, RISING);
}

// ============================================================================
// NVM Parameter Storage (Using Preferences)
// ============================================================================

void configure_nvm() {
    preferences.begin("pomelo", false); // Namespace "pomelo", read-write
}

void load_parameters() {
    // Load parameters from NVS (Non-Volatile Storage)
    // Example - adapt to your actual parameter structure
    size_t len = sizeof(core_params);
    preferences.getBytes("core_params", &coreParams, len);
    len = sizeof(physics_params);
    preferences.getBytes("physics_params", &physicsParams, len);
    
    Serial.println("Parameters loaded from NVS");
}

void save_parameters() {
    preferences.putBytes("core_params", &coreParams, sizeof(core_params));
    preferences.putBytes("physics_params", &physicsParams, sizeof(physics_params));
    Serial.println("Parameters saved to NVS");
}

// ============================================================================
// USB and UART Data Handlers
// ============================================================================

void usb_data_handler() {
    // USB CDC is on Serial (native USB)
    // TODO: Implement command parsing from Serial
    while (Serial.available()) {
        char c = Serial.read();
        // Process commands (JSON protocol from original code)
        // This needs to be ported from the original uart_data_handler
    }
}

void uart_data_handler() {
    // Process UART data (Serial1)
    uart_task(); // Read into buffer
    
    // TODO: Implement command parsing from UART
    // Port the original command parser here
}

// ============================================================================
// Temperature Compensation and HV Control
// ============================================================================

void update_hv_temp(bool force) {
    // TODO: Read temperature sensor via I2C
    // Adjust HV bias based on temperature
    // Use external DAC to set HV control voltage
    
    // Placeholder implementation
    Serial.println("Temperature compensation update");
}

void temp_init() {
    // TODO: Initialize temperature sensor (I2C)
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
}

void i2c_init() {
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    Serial.println("I2C initialized");
}

// ============================================================================
// DAQ Control
// ============================================================================

void daq_stop() {
    gammaDaqRun = false;
    // Disable interrupts or stop acquisition
}

void daq_start() {
    // Clear histograms and statistics
    memset((void*)gammaSpectrum, 0, sizeof(gammaSpectrum));
    memset((void*)gammaSpectrumCoincidence, 0, sizeof(gammaSpectrumCoincidence));
    gammaCounts = 0;
    gammaSum = 0;
    gammaSumSquare = 0;
    gammaFifoHead = 0;
    gammaFifoTail = 0;
    
    gammaDaqRun = true;
    Serial.println("DAQ started");
}

void coincidences_reset() {
    gammaCoincidence = false;
    gammaPulseCoincidenceN = 0;
}

// ============================================================================
// System Power Control
// ============================================================================

void pomelo_on() {
    // Enable all subsystems
    digitalWrite(PIN_AFE_EN, HIGH);
    daq_enabled = true;
    Serial.println("Pomelo ON");
}

void pomelo_off() {
    // Disable subsystems for low power
    digitalWrite(PIN_AFE_EN, LOW);
    daq_enabled = false;
    hv_disable();
    Serial.println("Pomelo OFF");
}

// ============================================================================
// Utility Functions
// ============================================================================

void pomelo_printf(uint8_t iFace, const char* str) {
    if (iFace == 0) { // USB
        if (usb_connected) {
            Serial.print(str);
        }
    } else if (iFace == 1) { // UART
        Serial1.print(str);
    }
}

int pomelo_sprintf(uint8_t iFace, const char* format, ...) {
    static char str[80];
    static va_list args;
    
    va_start(args, format);
    vsnprintf(str, sizeof(str), format, args);
    va_end(args);
    
    if (iFace == 0) { // USB
        if (usb_connected) {
            Serial.print(str);
        }
    } else if (iFace == 1) { // UART
        Serial1.print(str);
    }
    
    return 0;
}

void reset_to_bootloader() {
    Serial.println("Resetting to bootloader...");
    ESP.restart(); // ESP32 restart
}

// ============================================================================
// Arduino Setup Function
// ============================================================================

void setup() {
    // Initialize USB CDC Serial
    Serial.begin(115200);
    delay(1000); // Wait for USB serial to be ready
    Serial.println("\n\nPomeloCore ESP32-C3 Starting...");
    
    // Initialize GPIO
    gpio_init();
    
    // Initialize peripherals
    configure_nvm();
    uart_init();
    i2c_init();
    adc_init_gamma();
    dac_init_gamma_hv();
    hv_pwm_init();
    timer_init_gamma();
    eic_init();
    temp_init();
    
    // Load and apply parameters
    load_parameters();
    apply_parameters();
    
    // Initial state
    usb_connected = true;
    can_sleep = true;
    daq_enabled = false;
    temp_comp_run = false;
    gammaDaqRun = false;
    gammaCoincidence = false;
    gammaSyncTrig = false;
    listOut = 0;
    hvloadTime = 0;
    cmdState = STATE_CMD_IDLE;
    
    // Start in OFF state
    pomelo_off();
    
    Serial.println("Initialization complete!");
}

// ============================================================================
// Arduino Loop Function
// ============================================================================

void loop() {
    // USB data handler
    if (usb_connected) {
        usb_data_handler();
    }
    
    // UART data handler
    uart_data_handler();
    
    // List mode FIFO output
    if (listOut != 0) {
        if (((gammaFifoTail + 1) % LIST_FIFO_LEN) != gammaFifoHead) {
            gammaFifoTail++;
            if (gammaFifoTail >= LIST_FIFO_LEN) {
                gammaFifoTail = 0;
            }
            
            // Output data based on enabled modes
            if ((listOut & (1 << LIST_UART_PULSE)) != 0) 
                uart_tx(&gammaPulseChar, 1);
            if ((listOut & (1 << LIST_UART_ENERGY)) != 0) 
                pomelo_sprintf(1, "%d\n", gammaFifo[gammaFifoTail]);
            if ((listOut & (1 << LIST_UART_ENERGY_TS)) != 0) 
                pomelo_sprintf(1, "%lu,%d\n", gammaFifoTs[gammaFifoTail], gammaFifo[gammaFifoTail]);
            if ((listOut & (1 << LIST_USB_PULSE)) != 0) 
                pomelo_sprintf(0, "%c", gammaPulseChar);
            if ((listOut & (1 << LIST_USB_ENERGY)) != 0) 
                pomelo_sprintf(0, "%d\n", gammaFifo[gammaFifoTail]);
            if ((listOut & (1 << LIST_USB_ENERGY_TS)) != 0) 
                pomelo_sprintf(0, "%lu,%d\n", gammaFifoTs[gammaFifoTail], gammaFifo[gammaFifoTail]);
            
            can_sleep = false;
        } else {
            can_sleep = true;
        }
    }
    
    // Temperature compensation
    if (temp_comp_run) {
        if (daq_enabled) update_hv_temp(false);
        temp_comp_run = false;
    }
    
    // Sync trigger output pulse
    if (gammaSyncTrig) {
        digitalWrite(PIN_SYNC_OUTPUT, HIGH);
        delayMicroseconds(5);
        digitalWrite(PIN_SYNC_OUTPUT, LOW);
        gammaSyncTrig = false;
    }
    
    // Low power sleep (ESP32 has different sleep modes than SAML21)
    // For now, use light sleep if needed
    // if (can_sleep && !usb_connected) {
    //     esp_light_sleep_start();
    // }
    
    // Small delay to prevent tight loop
    delay(1);
}

// ============================================================================
// Parameter Application (Stub - needs full implementation)
// ============================================================================

void apply_parameters() {
    // Apply loaded parameters to hardware
    // Set HV, thresholds, etc.
    Serial.println("Parameters applied");
}
