# ESP32-C3 Migration - Quick Start

## Summary
The PomeloCore gamma spectroscopy firmware has been migrated from SAML21 to ESP32-C3 (RISC-V architecture) using the Arduino framework.

## What Has Been Done

### ✅ Completed Files
1. **[src/main.cpp](src/main.cpp)** - Main application code converted from ASF to Arduino
2. **[src/esp32c3_pinmap.h](src/esp32c3_pinmap.h)** - GPIO pin mapping configuration
3. **[src/nvm_params.h](src/nvm_params.h)** - Parameter structures (ASF-independent)
4. **[src/pMove.cpp](src/pMove.cpp)** - Spectral deconvolution filter array (1024×9)
5. **[platformio.ini](platformio.ini)** - Build configuration for ESP32-C3
6. **[ESP32C3_MIGRATION.md](ESP32C3_MIGRATION.md)** - Comprehensive migration documentation

### 🔧 What You Need to Do Next

#### 1. **CRITICAL: Add External DAC**
The ESP32-C3 has **NO built-in DAC**. You must add an external DAC chip:

**Recommended:** MCP4728 (4-channel, 12-bit I2C DAC)

```bash
# Install library
pio lib install "adafruit/Adafruit MCP4728"
```

Then implement in [main.cpp](src/main.cpp):
- `dac_init_gamma_hv()` at line ~220
- `dac_write_hv()` at line ~230

#### 2. **Verify Pin Assignments**
Open [esp32c3_pinmap.h](src/esp32c3_pinmap.h) and **verify all GPIO assignments match your hardware**:
- LED, AFE, Peak Detector, HV control, Triggers, etc.
- **Critical:** GPIO12-17 are reserved for SPI flash (DO NOT USE)
- GPIO18-19 are used for native USB

#### 3. **Port Command Parser**
The JSON command parser from the original code needs to be ported:
- Original location: `PomeloCore/src/main.c` lines 1896+
- Implement in: `usb_data_handler()` and `uart_data_handler()` functions

#### 4. **Test Incrementally**
Follow the testing checklist in [ESP32C3_MIGRATION.md](ESP32C3_MIGRATION.md#testing-checklist):
1. GPIO outputs (LED, AFE, etc.)
2. ADC (peak detector, HV load)
3. Interrupts (gamma trigger, sync)
4. External DAC (HV control)
5. USB CDC and UART communication
6. Full spectroscopy functions

## Build Instructions

```bash
# Build
pio run -e esp32-c3

# Upload (via USB)
pio run -e esp32-c3 --target upload

# Open serial monitor
pio device monitor
```

## Key Architecture Changes

| Component | SAML21 | ESP32-C3 |
|-----------|--------|----------|
| CPU | ARM Cortex-M0+ @ 48MHz | RISC-V @ 160MHz |
| GPIO API | `port_pin_set_output_level()` | `digitalWrite()` |
| DAC | Built-in 10-bit, 2ch | **External required** |
| ADC | 12-bit, 20 channels | 12-bit, 6 channels (ADC1) |
| Interrupts | EIC callbacks | `attachInterrupt()` + `IRAM_ATTR` |
| USB | ASF USB stack | Native USB CDC (`Serial`) |
| NVM/Flash | ASF NVM module | `Preferences` library (NVS) |
| Timers | TC/TCC modules | `hw_timer_t` |

## File Structure

```
PomeloCore/
├── platformio.ini          # Build config (ESP32-C3)
├── ESP32C3_MIGRATION.md    # Detailed migration guide
├── README_ESP32C3.md       # This file
└── src/
    ├── main.cpp            # Main application (Arduino)
    ├── esp32c3_pinmap.h    # GPIO pin assignments
    ├── nvm_params.h        # Parameter structures
    └── pMove.cpp           # Spectral deconvolution array
```

## Important Notes

### ⚠️ Hardware Differences
1. **No built-in DAC** - You **must** add external DAC (MCP4728 recommended)
2. **Fewer GPIOs** - 22 available vs 38 on SAML21
3. **GPIO restrictions:**
   - GPIO12-17: SPI flash (unavailable)
   - GPIO0, 2, 8, 9: Strapping pins (use carefully)
   - GPIO18-19: Native USB D+/D-

### USB Serial
The ESP32-C3 has **native USB**:
- `Serial` = USB CDC (configured via `platformio.ini`)
- `Serial1` = UART1 (external serial, 921600 baud)
- No need for external USB-Serial chips!

### Power Consumption
ESP32-C3 uses more power than SAML21:
- Active (WiFi off): ~20-25 mA
- Light sleep: ~130 µA  
- Deep sleep: ~5 µA

Sleep modes are commented out in `loop()` - implement if needed.

## Documentation

### Main References
- **[ESP32C3_MIGRATION.md](ESP32C3_MIGRATION.md)** - Complete migration guide with testing checklist
- **[FIRMWARE_ARCHITECTURE.md](FIRMWARE_ARCHITECTURE.md)** - Original system architecture
- **[SOFTWARE_FLOWS.md](SOFTWARE_FLOWS.md)** - Software flow diagrams

### External Documentation
- [ESP32-C3 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf)
- [ESP32-C3 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf)
- [Arduino-ESP32 Documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/)

## Support

For questions or issues with the migration, refer to:
1. [ESP32C3_MIGRATION.md](ESP32C3_MIGRATION.md) - Comprehensive technical details
2. Migration status table in documentation
3. Code comments in [main.cpp](src/main.cpp)

## Migration Status

| Task | Status |
|------|--------|
| Main code structure | ✅ Complete |
| GPIO configuration | ✅ Complete |
| ADC (ESP-IDF driver) | ✅ Complete |
| **External DAC** | ⚠️ **TODO** |
| Interrupts | ✅ Complete |
| Timers | ✅ Complete |
| USB CDC | ✅ Complete |
| UART | ✅ Complete |
| NVM/Preferences | ✅ Complete |
| I2C framework | ✅ Complete |
| **Command parser** | ❌ **TODO** |
| **Temperature comp** | ⚠️ Stub only |
| Power management | ⚠️ Optional |

**Next Priority:** Implement external DAC (MCP4728) and command parser.

---

**Last Updated:** 2025-12-26  
**Migration Author:** GitHub Copilot  
**Version:** 1.0
