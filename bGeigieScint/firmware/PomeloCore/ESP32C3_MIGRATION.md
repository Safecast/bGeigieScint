# PomeloCore SAML21 to ESP32-C3 Migration Guide

## Overview
This document describes the conversion of the PomeloCore gamma spectroscopy firmware from the Atmel SAML21G18B (ARM Cortex-M0+) to the Espressif ESP32-C3 (RISC-V) microcontroller.

---

## Hardware Differences

### Microcontroller Comparison

| Feature | SAML21G18B | ESP32-C3 | Notes |
|---------|------------|----------|-------|
| Architecture | ARM Cortex-M0+ | RISC-V | Different instruction set |
| Clock Speed | 48 MHz | 160 MHz | 3.3x faster |
| Flash | 256 KB | 4 MB | 16x more storage |
| RAM | 32 KB | 400 KB | 12.5x more memory |
| GPIO Pins | 38 | 22 | Fewer GPIOs available |
| ADC | 12-bit, 20 channels | 12-bit, 6 channels | Fewer ADC channels |
| **DAC** | **10-bit, 2 channels** | **NONE** | **⚠️ CRITICAL: Need external DAC** |
| USB | USB Device (via pins) | Native USB CDC | Built-in USB serial |
| Power Consumption | Ultra-low power | Moderate | Higher power draw |
| Operating Voltage | 1.62V - 3.63V | 3.0V - 3.6V | Similar range |

---

## Critical Hardware Changes

### ⚠️ NO Built-in DAC
**IMPACT:** HIGH - Requires hardware modification

The ESP32-C3 does **NOT** have a built-in DAC (unlike SAML21 which has 2x 10-bit DAC channels). The original firmware uses DAC for:
1. **HV (High Voltage) control** for SiPM bias
2. **Analog control signals** for AFE

**Solutions:**
- **Option 1:** External I2C DAC (e.g., MCP4725, MCP4728 dual)
- **Option 2:** External SPI DAC (e.g., MCP4921, DAC8551)
- **Option 3:** PWM + RC filter (lower precision, not recommended for HV)

**Recommended:** MCP4728 (4-channel I2C DAC, 12-bit) for better resolution than original 10-bit.

### Reduced GPIO Count
ESP32-C3 has only 22 GPIOs vs SAML21's 38. Some pins have restrictions:
- **GPIO12-17:** Reserved for SPI flash (DO NOT USE)
- **GPIO18-19:** Native USB D+/D- (already configured)
- **GPIO0, 2, 8, 9:** Strapping pins (boot mode) - use carefully

**Action Required:** Review pin assignments in `esp32c3_pinmap.h` and verify against your actual PCB layout.

### ADC Channels
- SAML21: 20 ADC channels
- ESP32-C3: 6 ADC1 channels (GPIO0-5), ADC2 shared with WiFi

**Impact:** Ensure critical analog signals (peak detector, HV monitor) are on ADC1 channels.

---

## Software Architecture Changes

### Framework Migration
| Component | SAML21 (ASF) | ESP32-C3 (Arduino) |
|-----------|--------------|-------------------|
| GPIO | `port_pin_set_output_level()` | `digitalWrite()` |
| Pin Mode | `port_pin_set_config()` | `pinMode()` |
| ADC | `adc_read()` module | `adc1_get_raw()` |
| DAC | `dac_chan_write()` module | External DAC via I2C/SPI |
| External Interrupts | EIC module callbacks | `attachInterrupt()` |
| Timers | TC/TCC modules | `hw_timer_t` / `timerBegin()` |
| USB CDC | ASF USB stack | Native USB via `Serial` |
| NVM/Flash | ASF NVM module | `Preferences` library (NVS) |
| UART | SERCOM modules | `Serial1` (HardwareSerial) |
| I2C | SERCOM I2C master | `Wire` library |
| SPI | SERCOM SPI | `SPI` library |
| PWM | TCC module | LEDC peripheral |
| RTC | RTC module | Hardware timers |
| Sleep Modes | `system_set_sleepmode()` | `esp_light_sleep_start()` |

---

## Key Migration Steps Completed

### ✅ 1. Pin Mapping
Created `esp32c3_pinmap.h` with GPIO assignments. **VERIFY THESE MATCH YOUR HARDWARE!**

### ✅ 2. Main Code Structure
Converted `main.c` → `main.cpp`:
- ASF `main()` → Arduino `setup()` + `loop()`
- Removed ASF includes, added Arduino/ESP-IDF headers
- Converted peripheral initialization

### ✅ 3. GPIO Control
- `port_pin_set_output_level()` → `digitalWrite()`
- `port_pin_set_config()` → `pinMode()`
- Maintained same logic flow

### ✅ 4. Interrupt Handling
- ASF EIC callbacks → `attachInterrupt()` with `IRAM_ATTR` ISRs
- Gamma trigger ISR on `PIN_TRIGGER` (GPIO6)
- Sync trigger ISR on `PIN_SYNC_INPUT` (GPIO7)

### ✅ 5. Timers
- RTC 1Hz timer → `hw_timer_t` with 1-second alarm
- HV load timer → Separate hardware timer
- Used `timerBegin()`, `timerAttachInterrupt()`, `timerAlarmWrite()`

### ✅ 6. USB CDC
- ASF USB stack → ESP32-C3 native USB
- `udi_cdc_write()` → `Serial.print()` / `Serial.write()`
- Configured via platformio.ini: `ARDUINO_USB_CDC_ON_BOOT=1`

### ✅ 7. UART
- SERCOM2 → `Serial1` (UART1)
- Baud rate: 921600 (maintained)
- Manual ISR → Arduino's built-in UART interrupt handling

### ✅ 8. NVM/Flash Storage
- ASF NVM → `Preferences` library (NVS)
- `nvm_write_buffer()` → `preferences.putBytes()`
- `nvm_read_buffer()` → `preferences.getBytes()`

### ✅ 9. ADC
- ASF ADC module → ESP-IDF ADC driver
- 12-bit resolution maintained
- Calibration via `esp_adc_cal_characterize()`

---

## TODO: Remaining Implementation Tasks

### 🔧 1. External DAC Implementation
**Priority: CRITICAL**

The placeholder DAC functions need real implementation:

```cpp
// src/main.cpp lines ~200-220
void dac_init_gamma_hv() {
    // TODO: Initialize external DAC via I2C or SPI
}

void dac_write_hv(uint16_t value) {
    // TODO: Write to external DAC
}
```

**Action:** 
- Choose DAC chip (recommend MCP4728)
- Add I2C library code
- Test HV control loop

### 🔧 2. Command Parser
**Priority: HIGH**

The original JSON command parser needs to be ported:

```cpp
void usb_data_handler() {
    // TODO: Implement command parsing from Serial
}

void uart_data_handler() {
    // TODO: Implement command parsing from UART
}
```

**Original location:** `PomeloCore/src/main.c` lines 1896+ (function `cmd_parse()`)

**Action:**
- Extract command parsing logic
- Port to ESP32-C3 (should be straightforward)
- Test all commands

### 🔧 3. Spectral Deconvolution Filter
**Priority: MEDIUM**

The `pMove[1024][9]` filter array is referenced but not implemented:

```cpp
extern const uint16_t pMove[1024][9];
```

**Action:**
- Locate the pMove array definition in original project
- Copy to ESP32-C3 project
- Integrate into gamma trigger ISR

### 🔧 4. Temperature Compensation
**Priority: MEDIUM**

Temperature sensor I2C communication needs implementation:

```cpp
void update_hv_temp(bool force) {
    // TODO: Read temperature sensor via I2C
}
```

**Action:**
- Identify temp sensor chip (likely on original board)
- Add I2C read code
- Implement HV bias adjustment algorithm

### 🔧 5. Power Management
**Priority: LOW**

ESP32 sleep modes differ from SAML21:

```cpp
// Commented out in loop():
// if (can_sleep && !usb_connected) {
//     esp_light_sleep_start();
// }
```

**Action:**
- Configure wake sources (GPIO, timer)
- Test light sleep mode
- Measure power consumption

### 🔧 6. Coincidence Logic
**Priority: MEDIUM**

Coincidence acknowledgment output (original PB11) may need I2C GPIO expander if no GPIO available.

**Action:**
- Review coincidence requirements
- Allocate GPIO or add expander

---

## Testing Checklist

- [ ] **GPIO Output Tests**
  - [ ] LED toggle
  - [ ] Peak detector reset pulse
  - [ ] AFE enable/disable
  - [ ] HV crowbar control
  - [ ] Sync output pulse

- [ ] **GPIO Input Tests**
  - [ ] Trigger input detection
  - [ ] Sync input detection
  - [ ] Coincidence input detection
  - [ ] USB VBUS detection (if available)

- [ ] **ADC Tests**
  - [ ] Gamma peak detector read (ADC_CHANNEL_GAMMA)
  - [ ] HV load measurement (ADC_CHANNEL_HV_LOAD)
  - [ ] Calibration verification

- [ ] **DAC Tests** (requires external DAC)
  - [ ] HV control voltage output
  - [ ] DAC I2C communication
  - [ ] HV ramp test

- [ ] **Communication Tests**
  - [ ] USB CDC (Serial) data transfer
  - [ ] UART (Serial1) at 921600 baud
  - [ ] Command parsing (USB and UART)
  - [ ] List mode data output

- [ ] **Interrupt Tests**
  - [ ] Gamma trigger ISR latency
  - [ ] Sync trigger ISR
  - [ ] RTC 1Hz timer ISR
  - [ ] HV load timer ISR

- [ ] **Storage Tests**
  - [ ] Save parameters to NVS
  - [ ] Load parameters from NVS
  - [ ] Parameter persistence after reset

- [ ] **Spectroscopy Tests**
  - [ ] Histogram accumulation
  - [ ] Coincidence detection
  - [ ] List mode FIFO
  - [ ] Spectral deconvolution filter
  - [ ] Statistics calculation

- [ ] **System Tests**
  - [ ] Temperature compensation
  - [ ] HV boost mode switching
  - [ ] USB plug/unplug handling
  - [ ] Bootloader reset
  - [ ] Low power sleep (if implemented)

---

## Performance Considerations

### ✅ Advantages of ESP32-C3
1. **3.3x faster clock:** Allows more complex ISR processing
2. **12.5x more RAM:** Can buffer more data, larger histograms
3. **Native USB:** Simpler USB implementation, no external components
4. **WiFi/BLE (optional):** Can add wireless data streaming

### ⚠️ Potential Issues
1. **ISR Timing:** ESP32 has more overhead in ISR entry/exit
   - **Mitigation:** Use `IRAM_ATTR` for critical ISRs (already done)
2. **ADC Speed:** ESP32-C3 ADC may be slower than SAML21
   - **Test:** Measure ADC conversion time in ISR
3. **Pin Count:** Limited GPIOs may require I2C expanders
4. **Power Consumption:** ESP32-C3 draws more current
   - Deep sleep: ~5 µA
   - Light sleep: ~130 µA
   - Active (WiFi off): ~20-25 mA

---

## External Hardware Requirements

### Required External Components

1. **DAC Module** (CRITICAL)
   - Recommended: MCP4728 (4-channel, 12-bit, I2C, $2-3)
   - Alternative: MCP4725 (1-channel) + second channel if needed
   - Connection: I2C (GPIO8=SDA, GPIO9=SCL)

2. **Temperature Sensor** (if not on board)
   - Original likely uses I2C sensor
   - Common options: TMP102, LM75, SHT31

3. **Level Shifters** (if needed)
   - ESP32-C3 I/O is 3.3V tolerant
   - Check if AFE or HV control circuits need 5V signals

4. **Pull-up/Pull-down Resistors**
   - ESP32-C3 has internal pull-ups/downs
   - Verify trigger inputs have appropriate external conditioning

---

## Build Configuration

The `platformio.ini` is already configured for ESP32-C3:

```ini
[env:esp32-c3]
platform = espressif32
board = esp32-c3-devkitm-1
framework = arduino
```

Key settings:
- USB CDC enabled: `ARDUINO_USB_CDC_ON_BOOT=1`
- Optimization: `-Os` (size)
- Flash: 4MB
- Upload speed: 921600 baud

---

## Next Steps

1. **Review Pin Mapping**
   - Open `src/esp32c3_pinmap.h`
   - **Verify all GPIO assignments match your hardware schematic**
   - Update as needed

2. **Add External DAC**
   - Select DAC chip (MCP4728 recommended)
   - Install library: `pio lib install "adafruit/Adafruit MCP4728"`
   - Implement `dac_init_gamma_hv()` and `dac_write_hv()`

3. **Port Command Parser**
   - Extract from `PomeloCore/src/main.c` lines 1896+
   - Integrate into `usb_data_handler()` and `uart_data_handler()`

4. **Add pMove Filter**
   - Locate array definition in original project
   - Add to ESP32-C3 project (create `pMove.cpp`)

5. **Test Incrementally**
   - Start with GPIO tests
   - Add ADC, then DAC
   - Test interrupts
   - Finally, full spectroscopy

6. **Calibration**
   - Re-calibrate ADC for ESP32-C3
   - Adjust timing constants if needed
   - Verify spectrum quality matches original

---

## Support and References

### ESP32-C3 Documentation
- [ESP32-C3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)
- [ESP32-C3 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf)
- [Arduino-ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/)

### Original PomeloCore
- `FIRMWARE_ARCHITECTURE.md` - System architecture
- `SOFTWARE_FLOWS.md` - Software flow diagrams
- `PomeloCore/src/main.c` - Original source code

### Library References
- **Preferences:** ESP32 NVS abstraction
- **Wire:** I2C library for Arduino
- **MCP4728:** Adafruit library for DAC

---

## Known Limitations

1. **No hardware DAC** - Requires external chip
2. **Fewer GPIOs** - May need I/O expander for full functionality
3. **Different sleep modes** - Power consumption profile differs
4. **ADC2 unavailable** - If using WiFi (not needed for this app)
5. **No direct replacement for TCC** - PWM via LEDC (different config)

---

## Migration Status

| Component | Status | Priority | Notes |
|-----------|--------|----------|-------|
| Main structure | ✅ Complete | Critical | setup()/loop() implemented |
| GPIO | ✅ Complete | Critical | All pins mapped |
| ADC | ✅ Complete | Critical | ESP-IDF driver used |
| DAC | ⚠️ Stub only | Critical | **Needs external DAC implementation** |
| Interrupts | ✅ Complete | Critical | attachInterrupt() used |
| Timers | ✅ Complete | High | hw_timer_t implemented |
| USB CDC | ✅ Complete | High | Native USB configured |
| UART | ✅ Complete | High | Serial1 configured |
| NVM | ✅ Complete | High | Preferences library |
| I2C | ⚠️ Partial | High | Wire initialized, no devices |
| Command Parser | ❌ TODO | High | Needs porting |
| pMove Filter | ❌ TODO | Medium | Array missing |
| Temp Comp | ⚠️ Stub only | Medium | Sensor I2C needed |
| Power Mgmt | ❌ TODO | Low | Sleep modes optional |
| Coincidence Ack | ⚠️ TODO | Medium | May need I/O expander |

---

**Legend:**
- ✅ Complete: Fully implemented and tested
- ⚠️ Partial: Framework in place, needs device-specific code
- ❌ TODO: Not yet implemented

---

**Last Updated:** 2025-12-26  
**Author:** GitHub Copilot  
**Version:** 1.0
