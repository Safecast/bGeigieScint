#ifndef ESP32C3_PINMAP_H
#define ESP32C3_PINMAP_H

/**
 * PomeloCore ESP32-C3 Pin Mapping
 * 
 * This file maps the original SAML21 pins to ESP32-C3 GPIO pins.
 * ESP32-C3 has 22 GPIO pins (GPIO0-GPIO21), some with special functions.
 * 
 * CRITICAL NOTES:
 * - GPIO0: Strapping pin, must be HIGH during boot (avoid using for critical functions)
 * - GPIO2: Strapping pin (Boot mode selection)
 * - GPIO8: Strapping pin (can be used but affected during boot)
 * - GPIO9: Strapping pin (Boot mode selection)
 * - GPIO18-19: Native USB D-/D+ (used for USB CDC, don't reassign)
 * - GPIO12-17: SPI Flash (DO NOT USE - connected to internal flash)
 * 
 * Available GPIOs: 0-11, 18-21 (excluding 12-17 for flash)
 */

// LED indicator
#define PIN_LED                 GPIO_NUM_10   // Original: PA19

// Analog Front End (AFE) Control
#define PIN_AFE_EN              GPIO_NUM_0    // Original: PA14 - AFE Enable
#define PIN_PEAK_DET_DISABLE    GPIO_NUM_1    // Original: PA15 - Peak detector disable
#define PIN_RESET_CAP           GPIO_NUM_2    // Original: PA08 - Reset capacitor

// Ramp Generator
#define PIN_RAMP_EN             GPIO_NUM_3    // Original: PA03 - Ramp generator enable
#define PIN_RAMP_TRIG           GPIO_NUM_4    // Original: PA11 - Ramp generator trigger
#define PIN_RAMP_INPUT          GPIO_NUM_5    // Original: PA04 - Ramp generator input (ADC)

// Gamma Detection Triggers
#define PIN_TRIGGER             GPIO_NUM_6    // Original: PA18 - Main trigger input (CRITICAL ISR)
#define PIN_SYNC_INPUT          GPIO_NUM_7    // Original: PB08 - Synchronizer input
#define PIN_PEAKDET_EN          GPIO_NUM_8    // Original: PB03 - Peak detector enable (2nd trigger)
#define PIN_SYNC_OUTPUT         GPIO_NUM_21   // Original: PB02 - Sync pulse output

// High Voltage (HV) Control
#define PIN_HV_CROWBAR          GPIO_NUM_9    // Original: PA21 - HV crowbar (active low)
#define PIN_HV_LOAD_MEASURE     GPIO_NUM_20   // Original: PB10 - HV load measurement (ADC input)

// Coincidence Logic
#define PIN_COINCIDENCE_IN      GPIO_NUM_11   // Original: PA20 - Coincidence input
// Note: Coincidence acknowledgment on original PB11 - may need implementation via I2C expander

// ADC/DAC Channels
// ESP32-C3 has 5 ADC1 channels (GPIO0-4) - Note: GPIO5 is NOT an ADC channel on ESP32-C3!
// ESP32-C3 does NOT have a built-in DAC - you'll need external DAC via I2C or SPI
#define ADC_CHANNEL_GAMMA       ADC1_CHANNEL_4  // GPIO4 for peak detector ADC (was GPIO5 on SAML21)
#define ADC_CHANNEL_HV_LOAD     ADC1_CHANNEL_0  // GPIO0 for HV load measurement (reconsider if boot issues)

// Communication (Hardware UART0 is used for USB CDC on ESP32-C3)
// Use UART1 for external serial communication
#define UART_NUM                UART_NUM_1
#define PIN_UART_TX             GPIO_NUM_21    // Default UART1 TX
#define PIN_UART_RX             GPIO_NUM_20    // Default UART1 RX
// Note: These may conflict with HV pins - adjust based on your board layout

// I2C for external sensors (temperature, DAC, etc.)
#define PIN_I2C_SDA             GPIO_NUM_8     // Default I2C SDA
#define PIN_I2C_SCL             GPIO_NUM_9     // Default I2C SCL

// SPI for external peripherals if needed
#define PIN_SPI_MOSI            GPIO_NUM_7
#define PIN_SPI_MISO            GPIO_NUM_2
#define PIN_SPI_SCK             GPIO_NUM_6
#define PIN_SPI_CS              GPIO_NUM_10

// USB Detection (ESP32-C3 has native USB)
// VBUS detection might be available via GPIO or power management
#define PIN_USB_VBUS            GPIO_NUM_19    // May need hardware modification

// PWM for HV boost converter
// ESP32-C3 has LEDC peripheral for PWM
#define PWM_CHANNEL_HV          0
#define PWM_TIMER_HV            0
#define PWM_FREQ_HV             50000          // 50 kHz PWM for HV boost

// Important: Verify these pin assignments match your actual hardware!
// This is a template - adjust based on your ESP32-C3 board layout

#endif // ESP32C3_PINMAP_H
