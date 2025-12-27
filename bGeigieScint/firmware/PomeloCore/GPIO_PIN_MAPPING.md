# PomeloCore GPIO Pin Mapping

## Overview
This document provides a comprehensive mapping of GPIO pins used by the PomeloCore firmware for both the original SAML21G18B microcontroller and the ESP32-C3 migration target.

---

## SAML21G18B GPIO Map

### Port A (PA) Pins

| SAML21 Pin | Function | Direction | Description | Special Function |
|------------|----------|-----------|-------------|------------------|
| **PA02** | DAC_VOUT0 | Output | HV control DAC output | DAC Channel 0 |
| **PA03** | RAMP_EN | Output | Ramp generator enable | Digital I/O |
| **PA04** | RAMP_INPUT | Input | Ramp generator input (ADC) | ADC Positive Input 4 |
| **PA07** | PEAK_DET_ADC | Input | Peak detector ADC input | ADC Positive Input 7 |
| **PA08** | RESET_CAP | Output | Reset peak detector capacitor | Digital I/O |
| **PA09** | ACK_DOWNSTREAM | Input | Downstream ACK for coincidence | Digital I/O |
| **PA10** | HV_PWM | Output | HV boost PWM output | TCC0_WO2 (PWM) |
| **PA11** | RAMP_TRIG | Output | Ramp generator trigger | Digital I/O |
| **PA12** | UART_TX | Output | Serial UART TX | SERCOM2_PAD0 |
| **PA13** | UART_RX | Input | Serial UART RX | SERCOM2_PAD1 |
| **PA14** | AFE_EN | Output | Analog Front End enable | Digital I/O |
| **PA15** | PEAK_DET_DISABLE | Output | Peak detector disable | Digital I/O |
| **PA16** | I2C_SDA | Bidirectional | I2C data | SERCOM1_PAD0 |
| **PA17** | I2C_SCL | Output | I2C clock | SERCOM1_PAD1 |
| **PA18** | TRIGGER | Input | Gamma trigger (falling edge) | EIC_EXTINT2 |
| **PA19** | LED | Output | Status LED indicator | Digital I/O |
| **PA20** | COINCIDENCE_IN | Input | Coincidence monitor input | CCL / Digital I/O |
| **PA21** | HV_CROWBAR | Output | HV crowbar (active LOW) | Digital I/O |
| **PA22** | REMOTE_TRIG_IN | Input | Remote trigger CCL input | CCL2_IN0 (I) |
| **PA23** | LOCAL_TRIG_IN | Input | Local trigger CCL input | CCL2_IN1 (I) |
| **PA24** | USB_DM | Bidirectional | USB D- | USB Data Minus |
| **PA25** | USB_DP | Bidirectional | USB D+ | USB Data Plus |
| **PA27** | USB_VBUS | Input | USB VBUS detection | EIC_EXTINT15 |
| **PA30** | SWCLK | N/A | Debug/Programming | SWD Clock |
| **PA31** | SWDIO | N/A | Debug/Programming | SWD Data |

### Port B (PB) Pins

| SAML21 Pin | Function | Direction | Description | Special Function |
|------------|----------|-----------|-------------|------------------|
| **PB02** | SYNC_OUTPUT | Output | Sync pulse output | Digital I/O |
| **PB03** | PEAKDET_EN | Input | Peak detector enable (2nd trigger) | Digital I/O |
| **PB08** | SYNC_INPUT | Input | Synchronizer input (rising edge) | EIC_EXTINT8 |
| **PB09** | COINCIDENCE_OUT | Output | Coincidence CCL output | CCL2_OUT (I) |
| **PB10** | HV_LOAD_MEAS | Input | HV load measurement | EIC_EXTINT10 |
| **PB11** | ACK_OUTPUT | Output | Coincidence ACK output | Digital I/O |
| **PB22** | ACK0_IN | Input | ACK0 CCL input | CCL0_IN0 (I) |
| **PB23** | COINCIDENCE_OUT2 | Output | CCL0 output | CCL0_OUT (I) |

### DAC Configuration

| Channel | Pin | Output Range | Function |
|---------|-----|--------------|----------|
| DAC0 | PA02 | 0-2.0V (Internal Ref) | HV bias control |
| DAC1 | PA05 | 0-2.0V (Internal Ref) | Trigger threshold |

### ADC Configuration

| Channel | Pin | Input Range | Function |
|---------|-----|-------------|----------|
| AIN4 | PA04 | 0-2.0V | Ramp generator input (calibration) |
| AIN7 | PA07 | 0-2.0V | Peak detector output (gamma energy) |

---

## ESP32-C3 GPIO Map

### GPIO Availability

| GPIO | Usable | Restriction | Notes |
|------|--------|-------------|-------|
| 0 | ⚠️ Caution | Strapping pin | Must be HIGH during boot |
| 1 | ✅ Yes | None | General purpose |
| 2 | ⚠️ Caution | Strapping pin | Boot mode selection |
| 3 | ✅ Yes | None | General purpose |
| 4 | ✅ Yes | None | ADC1_CH4 available |
| 5 | ✅ Yes | None | General purpose (NOT ADC!) |
| 6 | ✅ Yes | None | General purpose |
| 7 | ✅ Yes | None | General purpose |
| 8 | ⚠️ Caution | Strapping pin | Affected during boot |
| 9 | ⚠️ Caution | Strapping pin | Boot mode selection |
| 10 | ✅ Yes | None | General purpose |
| 11 | ✅ Yes | None | General purpose |
| 12-17 | ❌ No | SPI Flash | **DO NOT USE** |
| 18 | ❌ Reserved | USB D- | Native USB |
| 19 | ❌ Reserved | USB D+ | Native USB |
| 20 | ✅ Yes | None | Default UART1 RX |
| 21 | ✅ Yes | None | Default UART1 TX |

### Proposed ESP32-C3 Pin Assignments

| ESP32-C3 GPIO | SAML21 Pin | Function | Notes |
|---------------|------------|----------|-------|
| GPIO0 | PA14 | AFE_EN | ⚠️ Strapping - ensure HIGH during boot |
| GPIO1 | PA15 | PEAK_DET_DISABLE | Peak detector control |
| GPIO2 | PA08 | RESET_CAP | ⚠️ Strapping pin |
| GPIO3 | PA03 | RAMP_EN | Ramp generator enable |
| GPIO4 | PA11 | RAMP_TRIG | Ramp trigger + ADC1_CH4 |
| GPIO5 | N/A | (unused) | Note: NOT an ADC channel |
| GPIO6 | PA18 | TRIGGER | Main gamma trigger ISR |
| GPIO7 | PB08 | SYNC_INPUT | Synchronizer input |
| GPIO8 | PB03 | PEAKDET_EN | ⚠️ Strapping - I2C SDA alternate |
| GPIO9 | PA21 | HV_CROWBAR | ⚠️ Strapping - I2C SCL alternate |
| GPIO10 | PA19 | LED | Status LED indicator |
| GPIO11 | PA20 | COINCIDENCE_IN | Coincidence monitor |
| GPIO18 | USB D- | USB_DM | Native USB (fixed) |
| GPIO19 | USB D+ | USB_DP | Native USB (fixed) |
| GPIO20 | PA13 | UART_RX | UART1 RX |
| GPIO21 | PA12/PB02 | UART_TX / SYNC_OUT | UART1 TX (dual use) |

---

## ESP32-C3 Super Mini Specific Map

This mapping is optimized for the **ESP32-C3 Super Mini** module, which features an onboard USB-C connector.

### Super Mini Pinout Summary

| Pomelo Function | SAML21 Pin | **Super Mini GPIO** | Pin Type | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Gamma Trigger** | PA18 | **6** | Interrupt | **Critical:** Main detector ISR |
| **Peak Det ADC** | PA07 | **4** | ADC1_CH4 | **Critical:** Gamma energy reading |
| **HV PWM** | PA10 | **3** | PWM (LEDC) | High-speed PWM for HV Boost |
| **AFE Enable** | PA14 | **0** | Digital Out | Strapping pin (Must be HIGH at boot) |
| **Reset Cap** | PA08 | **2** | Digital Out | Strapping pin (Boot mode selection) |
| **Peak Disable** | PA15 | **1** | Digital Out | Peak detector control |
| **I2C SDA** | PA16 | **8** | I2C | **Bus:** Connect to MCP4728 & SSD1306 |
| **I2C SCL** | PA17 | **9** | I2C | **Bus:** Connect to MCP4728 & SSD1306 |
| **Sync Input** | PB08 | **7** | Digital In | Coincidence synchronization |
| **Sync Output** | PB02 | **5** | Digital Out | Coincidence synchronization |
| **HV Crowbar** | PA21 | **10** | Digital Out | Safety shutoff (Active LOW) |
| **System LED** | PA19 | **8** | Onboard | **Onboard Blue LED** (internal) |
| **UART TX** | PA12 | **21** | UART1 TX | Hardware UART (optional) |
| **UART RX** | PA13 | **20** | UART1 RX | Hardware UART (optional) |
| **USB D- / D+** | PA24/25 | **18/19** | **INTERNAL** | **Built-in to USB-C Connector** |

### Super Mini Hardware Strategy

1.  **USB Console**: Configure the ESP32-C3 to use **Native USB-OTG**. This allows `Serial` to communicate directly over the USB-C port (via GPIO 18/19), leaving the physical header pins 20/21 free for an external UART (e.g., GPS or Bluetooth).
2.  **No External USB Wiring**: Do **not** wire GPIO 18 or 19 to anything. They are hard-wired on the module to the USB-C connector.
3.  **External DAC Requirements**: Since the ESP32-C3 lacks an internal DAC, the **MCP4728** (or similar) MUST be connected to the I2C bus (Pins 8/9) to handle SiPM Bias and Trigger Thresholds.
4.  **Strapping Pins**:
    *   **GPIO 0 (AFE_EN)**: Must be HIGH during boot.
    *   **GPIO 2 (RESET_CAP)**: Strapping pin; ensure no static load pulling it LOW at boot.
    *   **GPIO 8 (SDA)**: Strapping pin; the standard I2C pull-up (4.7k - 10k) will keep this HIGH at boot as required.

### Super Mini Software Snippet

```cpp
// ESP32-C3 Super Mini HAL for PomeloCore
#define MCU_ESP32C3_SUPER_MINI

#define PIN_TRIGGER      6    // Gamma ISR
#define PIN_PEAK_ADC     4    // ADC1_CH4
#define PIN_HV_PWM       3    // HV Boost

#define PIN_AFE_EN       0    
#define PIN_PEAK_DIS     1    
#define PIN_RESET_CAP    2    

#define PIN_I2C_SDA      8    
#define PIN_I2C_SCL      9    

#define PIN_SYNC_IN      7    
#define PIN_SYNC_OUT     5    
#define PIN_HV_CROWBAR   10   
```


### Alternative: Internal Pseudo-DAC (PWM/PDM)

If an external I2C DAC chip (like MCP4728) is not available, the ESP32-C3 can generate analog voltages using **PWM** or **PDM** paired with an external **RC Low-Pass Filter**.

| Function | SAML21 Pin | **Super Mini GPIO** | Method |
| :--- | :--- | :--- | :--- |
| **HV Bias Control** | PA02 | **20** | LEDC PWM (High Res) |
| **Trigger Threshold**| PA05 | **21** | LEDC PWM (High Res) |

#### Hardware Filter Circuit
To minimize voltage ripple—which is critical for radiation spectroscopy—use a **Double RC Filter** on the output of GPIO 20/21:

```text
GPIO Pin ────┬───[ 10k Ω ]───┬───[ 10k Ω ]───┬─── ANALOG OUT
             │               │               │
           [ 1µF ]         [ 1µF ]         [ 0.1µF ]
             │               │               │
            GND             GND             GND
```

#### Pseudo-DAC Configuration Code
```cpp
// Initialize High-Resolution PWM for Pseudo-DAC
void setup_pseudo_dac() {
    // HV Bias (GPIO 20) - 13-bit resolution (0-8191)
    ledcSetup(0, 20000, 13); // 20kHz frequency
    ledcAttachPin(20, 0);

    // Trigger Threshold (GPIO 21)
    ledcSetup(1, 20000, 13); 
    ledcAttachPin(21, 1);
}

void set_hv_bias_voltage(uint16_t value) {
    ledcWrite(0, value); // Maps to 0.0V - 3.3V
}
```

#### Trade-offs
- **Pros**: Reduced BOM cost, simpler PCB routing.
- **Cons**: High output impedance and potential high-frequency ripple. Ripple on the threshold pin may cause false gamma triggers. A real DAC chip is always preferred for high-stability spectroscopy.

---

### Minimalist Software Integration

An ultra-minimalist Hardware Abstraction Layer (HAL) has been created specifically for this "Zero-Extra-Silicon" configuration. You can use it by including `hal_supermini_minimal.h` in your project.

It provides:
- **`hal_setup_dac()`**: Configures GPIO 20/21 as PWM outputs for HV/Threshold.
- **`hal_storage_begin()`**: Initializes internal NVS Flash storage.
- **`hal_save_params()` / `hal_load_params()`**: Saves calibration data to Flash (replaces the external I2C EEPROM).
- **`hal_init_pins()`**: Configures all primary GPIOs for the Super Mini headers.

---

### ESP32-C3 ADC Channels

| ADC Channel | GPIO | SAML21 Equivalent | Function |
|-------------|------|-------------------|----------|
| ADC1_CH0 | GPIO0 | - | (Strapping - avoid for ADC) |
| ADC1_CH1 | GPIO1 | - | Available |
| ADC1_CH2 | GPIO2 | - | (Strapping - avoid for ADC) |
| ADC1_CH3 | GPIO3 | PA04 | Ramp generator input |
| ADC1_CH4 | GPIO4 | PA07 | **Peak detector ADC** |
| ADC2_* | - | - | Unavailable if WiFi used |

### Missing Pins - Require I2C GPIO Expander

The ESP32-C3 has fewer GPIOs than SAML21. These functions may need an I2C GPIO expander (e.g., MCP23008, PCF8574):

| Function | SAML21 Pin | Reason |
|----------|------------|--------|
| PB11 ACK_OUTPUT | PB11 | Coincidence acknowledgment |
| HV_LOAD_MEAS | PB10 | Can use ADC with polling instead |
| CCL Inputs/Outputs | PA22, PA23, PB09, PB22, PB23 | CCL hardware not available |

---

## Hardware Mapping Diagram

```
                    SAML21G18B                              ESP32-C3
                   ┌─────────────┐                       ┌─────────────┐
                   │             │                       │             │
  Gamma Pulse ────►│ PA18 (INT)  │ ─────────────────────►│ GPIO6 (INT) │◄──── Gamma Pulse
                   │             │                       │             │
  Peak Det ADC ───►│ PA07 (ADC7) │ ─────────────────────►│ GPIO4 (ADC4)│◄──── Peak Det ADC
                   │             │                       │             │
        LED ◄──────│ PA19 (OUT)  │ ─────────────────────►│ GPIO10 (OUT)│──────► LED
                   │             │                       │             │
     AFE_EN ◄──────│ PA14 (OUT)  │ ─────────────────────►│ GPIO0 (OUT) │──────► AFE_EN
                   │             │                       │             │
  RESET_CAP ◄──────│ PA08 (OUT)  │ ─────────────────────►│ GPIO2 (OUT) │──────► RESET_CAP
                   │             │                       │             │
  HV_CROWBAR ◄─────│ PA21 (OUT)  │ ─────────────────────►│ GPIO10 (OUT)│──────► HV_CROWBAR
                   │             │                       │             │
   UART TX ◄───────│ PA12 (SCOM) │ ─────────────────────►│ GPIO21 (TX) │──────► UART TX
   UART RX ───────►│ PA13 (SCOM) │ ─────────────────────►│ GPIO20 (RX) │◄────── UART RX
                   │             │                       │             │
    USB D- ◄──────►│ PA24 (USB)  │ ──── (ONBOARD USB) ──►│ GPIO18 (USB)│◄─────► (Built-in)
    USB D+ ◄──────►│ PA25 (USB)  │ ──── (ONBOARD USB) ──►│ GPIO19 (USB)│◄─────► (Built-in)
                   │             │                       │             │
   I2C SDA ◄──────►│ PA16 (SCOM) │ ─────────────────────►│ GPIO8 (SDA) │◄─────► I2C SDA
   I2C SCL ◄──────►│ PA17 (SCOM) │ ─────────────────────►│ GPIO9 (SCL) │◄─────► I2C SCL
                   │             │                       │             │
HV DAC (PA02) ◄────│ DAC Ch0     │      EXTERNAL DAC     │ I2C to DAC  │──────► HV Control
Thresh DAC(PA05)◄──│ DAC Ch1     │ ────(MCP4728 etc)────►│ (MCP4728)   │──────► Threshold
                   │             │                       │             │
  HV PWM ◄─────────│ PA10 (TCC)  │    PWM via LEDC      │ GPIO3 (PWM) │──────► HV PWM
                   │             │                       │             │
                   └─────────────┘                       └─────────────┘
```

---

## Software Mapping Guide

### GPIO Abstraction Layer

Create a hardware abstraction layer to simplify porting:

```c
// ===== SAML21 Implementation (ASF) =====
#ifdef TARGET_SAML21
  #include <asf.h>
  
  #define PIN_LED           PIN_PA19
  #define PIN_AFE_EN        PIN_PA14
  #define PIN_RESET_CAP     PIN_PA08
  #define PIN_TRIGGER       PIN_PA18
  #define PIN_HV_CROWBAR    PIN_PA21
  #define PIN_PEAK_DIS      PIN_PA15
  #define PIN_RAMP_EN       PIN_PA03
  #define PIN_RAMP_TRIG     PIN_PA11
  #define PIN_SYNC_IN       PIN_PB08
  #define PIN_SYNC_OUT      PIN_PB02
  #define PIN_COINC_IN      PIN_PA20
  #define PIN_ACK_OUT       PIN_PB11
  #define PIN_HV_LOAD       PIN_PB10
  
  #define gpio_set_output(pin)    do { struct port_config c; port_get_config_defaults(&c); c.direction = PORT_PIN_DIR_OUTPUT; port_pin_set_config(pin, &c); } while(0)
  #define gpio_set_input(pin)     do { struct port_config c; port_get_config_defaults(&c); c.direction = PORT_PIN_DIR_INPUT; port_pin_set_config(pin, &c); } while(0)
  #define gpio_write(pin, val)    port_pin_set_output_level(pin, val)
  #define gpio_read(pin)          port_pin_get_input_level(pin)
  
  // DAC
  #define dac_write_hv(val)       dac_chan_write(&dac_instance_app, DAC_CHANNEL_0, val)
  #define dac_write_thresh(val)   dac_chan_write(&dac_instance_app, DAC_CHANNEL_1, val)
  
  // ADC
  #define adc_read_gamma()        ({ uint16_t v; adc_start_conversion(&adc_instance_app); while(adc_read(&adc_instance_app, &v)==STATUS_BUSY); v; })

#endif
```

```cpp
// ===== ESP32-C3 Implementation (Arduino) =====
#ifdef TARGET_ESP32C3
  #include <Arduino.h>
  #include <driver/adc.h>
  #include <Wire.h>
  
  #define PIN_LED           10
  #define PIN_AFE_EN        0
  #define PIN_RESET_CAP     2
  #define PIN_TRIGGER       6
  #define PIN_HV_CROWBAR    9
  #define PIN_PEAK_DIS      1
  #define PIN_RAMP_EN       3
  #define PIN_RAMP_TRIG     4
  #define PIN_SYNC_IN       7
  #define PIN_SYNC_OUT      21    // Shared with UART TX (choose one)
  #define PIN_COINC_IN      11
  // PIN_ACK_OUT - requires I2C expander
  // PIN_HV_LOAD - use ADC polling instead of interrupt
  
  #define gpio_set_output(pin)    pinMode(pin, OUTPUT)
  #define gpio_set_input(pin)     pinMode(pin, INPUT)
  #define gpio_write(pin, val)    digitalWrite(pin, val)
  #define gpio_read(pin)          digitalRead(pin)
  
  // DAC - External I2C DAC (MCP4728 example)
  // Requires external library
  void dac_write_hv(uint16_t val);     // Implement via I2C
  void dac_write_thresh(uint16_t val); // Implement via I2C
  
  // ADC
  #define adc_read_gamma()        adc1_get_raw(ADC1_CHANNEL_4)

#endif
```

### Interrupt Setup

```cpp
// ===== SAML21 Interrupt Setup =====
#ifdef TARGET_SAML21
void setup_trigger_interrupt() {
    struct extint_chan_conf config;
    extint_chan_get_config_defaults(&config);
    config.gpio_pin           = PIN_PA18A_EIC_EXTINT2;
    config.gpio_pin_mux       = MUX_PA18A_EIC_EXTINT2;
    config.detection_criteria = EXTINT_DETECT_FALLING;
    extint_chan_set_config(2, &config);
    extint_register_callback(trigger_callback, 2, EXTINT_CALLBACK_TYPE_DETECT);
    extint_chan_enable_callback(2, EXTINT_CALLBACK_TYPE_DETECT);
}
#endif

// ===== ESP32-C3 Interrupt Setup =====
#ifdef TARGET_ESP32C3
void IRAM_ATTR trigger_callback_isr() {
    // ISR code - must be in IRAM
    trigger_callback();
}

void setup_trigger_interrupt() {
    pinMode(PIN_TRIGGER, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_TRIGGER), trigger_callback_isr, FALLING);
}
#endif
```

### DAC Implementation for ESP32-C3 (External MCP4728)

```cpp
#include <Adafruit_MCP4728.h>

Adafruit_MCP4728 mcp;

void dac_init_gamma_hv() {
    if (!mcp.begin(0x60)) {  // Default I2C address
        // Handle error
    }
    // Set initial values
    mcp.setChannelValue(MCP4728_CHANNEL_A, 4095);  // HV control (min HV)
    mcp.setChannelValue(MCP4728_CHANNEL_B, 4095);  // Threshold (max = disabled)
}

void dac_write_hv(uint16_t value) {
    mcp.setChannelValue(MCP4728_CHANNEL_A, value);
}

void dac_write_thresh(uint16_t value) {
    mcp.setChannelValue(MCP4728_CHANNEL_B, value);
}
```

---

## Pin Function Summary Table

| Function | SAML21 | ESP32-C3 | Type | Critical? | Notes |
|----------|--------|----------|------|-----------|-------|
| **Gamma Trigger** | PA18 | GPIO6 | Input/INT | ⚠️ YES | ISR timing critical |
| **Peak Det ADC** | PA07 | GPIO4 | ADC | ⚠️ YES | 12-bit ADC reading |
| **LED** | PA19 | GPIO10 | Output | No | Status indicator |
| **AFE Enable** | PA14 | GPIO0 | Output | Yes | Powers AFE circuit |
| **Reset Cap** | PA08 | GPIO2 | Output | Yes | Peak det reset pulse |
| **Peak Disable** | PA15 | GPIO1 | Output | Yes | Peak det control |
| **HV Crowbar** | PA21 | GPIO10 | Output | Yes | Safety shutoff |
| **HV DAC** | PA02 | I2C DAC | DAC | ⚠️ YES | SiPM bias control |
| **Threshold DAC** | PA05 | I2C DAC | DAC | Yes | Trigger level |
| **HV PWM** | PA10 | GPIO3 | PWM | Yes | Boost converter |
| **UART TX** | PA12 | GPIO21 | Output | No | Serial comm |
| **UART RX** | PA13 | GPIO20 | Input | No | Serial comm |
| **USB D-** | PA24 | INTERNAL | USB | Yes | Built-in to USB-C |
| **USB D+** | PA25 | INTERNAL | USB | Yes | Built-in to USB-C |
| **I2C SDA** | PA16 | GPIO8 | Bidir | Yes | Sensor/DAC bus |
| **I2C SCL** | PA17 | GPIO9 | Output | Yes | I2C clock |
| **Sync Input** | PB08 | GPIO7 | Input/INT | Medium | Coincidence sync |
| **Sync Output** | PB02 | GPIO5 | Output | Medium | Sync pulse output |
| **Coincidence In** | PA20 | GPIO11 | Input | Medium | Monitor signal |
| **ACK Output** | PB11 | Expander | Output | Medium | Needs I2C expander |
| **HV Load** | PB10 | Polling | Input | Low | Can poll instead of INT |
| **Ramp Enable** | PA03 | GPIO3 | Output | Low | Calibration only |
| **Ramp Trigger** | PA11 | GPIO4 | Output | Low | Calibration only |
| **Ramp Input** | PA04 | GPIO3 | ADC | Low | Calibration only |

---

## Critical Timing Considerations

### Gamma Trigger ISR Timing

The gamma pulse trigger ISR is the most timing-critical part:

| Step | SAML21 Time | ESP32-C3 Time | Notes |
|------|-------------|---------------|-------|
| ISR Entry | ~1 µs | ~3-5 µs | ESP32 has more overhead |
| ADC Start | ~0.1 µs | ~0.5 µs | Function call |
| ADC Read | ~3-5 µs | ~10-15 µs | ADC conversion |
| Peak Reset | ~0.5 µs | ~0.3 µs | GPIO toggle |
| Total ISR | ~10-15 µs | ~20-30 µs | Acceptable |

**Recommendation:** Use `IRAM_ATTR` for all ISR code on ESP32-C3.

---

## Migration Checklist

- [x] Map all GPIO pins
- [x] Identify ADC channels
- [x] Document DAC requirements (external)
- [x] Plan interrupt assignments
- [x] Document I2C bus usage
- [x] Identify missing features requiring expander
- [ ] Verify PCB routing matches pin assignment
- [ ] Test each GPIO individually
- [ ] Calibrate ADC readings
- [ ] Test ISR timing

---

## References

- [SAML21 Datasheet](https://www.microchip.com/wwwproducts/en/ATSAML21G18B)
- [ESP32-C3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)
- [MCP4728 I2C DAC](https://www.microchip.com/wwwproducts/en/MCP4728)

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-27  
**Author:** Cline AI Assistant
