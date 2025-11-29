# bGeigieScint

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![KiCad](https://img.shields.io/badge/KiCad-9.0-blue.svg)](https://www.kicad.org/)
[![Version](https://img.shields.io/badge/version-1.3-green.svg)](CHANGELOG.md)

**bGeigieScint** is a compact radiation detection board featuring a Silicon Photomultiplier (SiPM) based sensor system with integrated high-voltage generation, analog signal processing, and USB connectivity.

## 📋 Features

- **Microcontroller**: ATSAML21G18B (ARM Cortex-M0+, 256KB Flash, 32KB RAM)
- **SiPM Interface**: Complete analog frontend with adjustable HV bias (30-70V)
- **Power Management**: Multi-rail power supply (3.3V, 3.0V, Vload, Vbias)
- **Connectivity**: USB-C interface with ESD protection
- **Debug**: 10-pin J-LINK SWD interface + 18 test points
- **Expansion**: Multiple GPIO headers for external interfaces
- **Compact**: 40mm × 100mm 4-layer PCB

## 🔧 Hardware Specifications

### Main Components

| Component | Part Number | Function |
|-----------|-------------|----------|
| MCU | ATSAML21G18B-AUT | Main microcontroller (48-pin QFN) |
| USB | USB3.1C16PFSMT | USB-C connector (USB 2.0) |
| LDO 3.3V | XC6209F332MR-G | Main 3.3V regulator |
| LDO 3.0V | TPS7A2030PDBVR | 3.0V rail for analog |
| LDO Vload | LT3014BHVES5 | Low-noise LDO for HV control |
| OpAmp | OPA357AIDBVR | Shaper amplifier |
| Comparator | TLV3201AIDBVT | Fast comparator |
| Latch | MC14043BDR2G | Digital latch for triggering |

### SiPM Sensor

- **Part Number**: AFBR-S4N44P014M (Broadcom)
- **Type**: NUV-HD Silicon Photomultiplier
- **Active Area**: 4×4 mm²
- **Spectral Range**: 350-900 nm (peak sensitivity ~420 nm)
- **Datasheet**: [AFBR-S4N44P014M Documentation](https://docs.broadcom.com/doc/AFBR-S4N44P014M-NUV-MT-Silicon-Photomultiplier)

### Scintillator Crystal

- **Material**: CsI(Tl) - Cesium Iodide doped with Thallium
- **Dimensions**: 10 mm × 10 mm × 20 mm
- **Emission Peak**: ~550 nm (matches SiPM sensitivity)
- **Application**: Gamma ray detection coupled to SiPM

### Power Supply

- **Input**: 4.5-6V via USB-C or external connector
- **Output Rails**:
  - 3.3V @ up to 200mA (digital)
  - 3.0V @ up to 100mA (analog)
  - Vload (adjustable)
  - Vbias: 30-70V @ low current (SiPM bias)

### HV Generation

The board features an integrated **boost converter + linear regulator** topology for SiPM bias generation:

- **Boost Stage**: PWM-controlled (L1 10mH inductor, Q3 P-FET, D9 Schottky)
- **Regulation**: LT3014 ultra-low-noise LDO
- **Control**: MCU DAC output (PA02_DAC_HV) sets target voltage
- **Monitoring**: Comparator feedback (PB10_HV_COMP_OUT)
- **Output**: Adjustable 30-70V Vbias for SiPM

## 📁 Project Structure

```
bGeigieScint/
├── bGeigieScint/
│   ├── bGeigieScint.kicad_pro       # KiCad project file
│   ├── bGeigieScint.kicad_sch       # Schematic (organized in functional blocks)
│   ├── bGeigieScint.kicad_pcb       # PCB layout (4-layer, 40×100mm)
│   ├── bGeigieScint-backups/        # Automatic backups
│   ├── firmware/                    # Firmware source code
│   │   └── PomeloCore/              # Main firmware project
│   ├── bootloader/                  # Bootloader files
│   │   └── uf2-samd21/              # UF2 bootloader for SAMD21
│   ├── v1_2/                        # Version 1.2 reference files
│   │   ├── schematic/               # V1.2 schematic PDF
│   │   ├── firmware/                # V1.2 firmware
│   │   └── bootloader/              # V1.2 bootloader
│   ├── Images/                      # Project images and photos
│   └── Misc Docs/                   # Additional documentation
├── BOM.csv                          # Bill of Materials
├── Python scripts (*.py)            # KiCad automation scripts
└── README.md                        # This file
```

## 🎨 Schematic Organization

The schematic is organized into **7 functional blocks**:

1. **USB & POWER INPUT**: USB-C interface, power connectors, reset button
2. **POWER MANAGEMENT**: LDOs, inductors, power distribution
3. **MCU CORE**: Microcontroller, crystal, decoupling
4. **ANALOG FRONTEND**: SiPM signal chain, opamps, comparators
5. **LOGIC & CONTROL**: Digital logic, latches, level shifters
6. **EXPANSION I/O**: Pin headers for external connections
7. **DEBUG & TEST**: J-LINK interface, test points

## 🔌 Pinout & Interfaces

### J-LINK Debug Header (10-pin)
```
1: VCC        2: SWDIO
3: GND        4: SWCLK
5: GND        6: SWO
7: NC         8: NC
9: GND       10: RESET
```

### Expansion Headers

- **H2, H3**: 7-pin GPIO expansion
- **H5**: 7-pin expansion with labeled signals
- **MEAS1**: 2-pin measurement header
- **P1, P2**: 2×2 power connectors (mirrored on Pomelo Physics board)

### Key Signals

| Signal | Description |
|--------|-------------|
| SiPM_A | SiPM analog input |
| Vbias | SiPM bias voltage output |
| SHAPER_OUT | Shaped pulse output |
| PA02_DAC_HV | HV control DAC output |
| PA10_PWM | Boost converter PWM |
| PB03_PEAKDET_EN | Peak detector enable |
| PA23_TRG_OUT | Trigger output |

## 📊 Version History

### V1.3 (Current)
**Major improvements over V1.2:**

✅ **Added (47 components)**:
- USB-C connector (USBC1)
- Reset button (BUT1)
- J-LINK debug header
- 18 test points (TP1-TP18)
- Additional transistors (Q4, Q5) and diodes (D6, D8, D10)
- 15 new resistors for better signal conditioning

✅ **Changed**:
- C44: 1uF → 4.7uF
- C45: 4.7uF → 1uF
- H2, H3: 6-pin → 7-pin headers (expanded)

✅ **Enhanced**:
- Better debugging capability
- Improved power filtering
- More flexible I/O expansion

### V1.2 (Legacy)
- Initial production version
- PDF schematic available in `v1_2/schematic/`

## 🚀 Getting Started

### Prerequisites

- **KiCad 9.0** or later
- Basic understanding of radiation detection and SiPM operation
- JTAG/SWD programmer (e.g., J-Link, ST-Link)

### Opening the Project

1. Clone this repository
2. Open `bGeigieScint/bGeigieScint.kicad_pro` in KiCad
3. The schematic shows functional blocks with dashed rectangles
4. The PCB has components organized by function

### Manufacturing

**PCB Specifications:**
- **Layers**: 4 (signal/GND/VCC/signal)
- **Dimensions**: 40mm × 100mm
- **Thickness**: 1.6mm
- **Copper**: 35μm (1oz) on all layers
- **Min Track/Space**: 0.15mm / 0.15mm (for 0805 components)
- **Finish**: HASL or ENIG recommended
- **Solder Mask**: Green (top and bottom)

**Assembly Notes:**
- Minimum component size: 0805 for passives
- QFN-48 MCU requires reflow soldering
- LDOs are SOT-23-5 packages
- Test points for easy debugging

## 📝 Design Notes

### Power Planes
- **Layer 1 (In1.Cu)**: GND plane - solid pour for low noise
- **Layer 2 (In2.Cu)**: VCC plane - split for 3.3V/3.0V rails

### Critical Traces
- Keep SiPM analog traces short and shielded
- HV traces (Vbias) should be isolated from digital signals
- Crystal traces should be short with GND guard ring

### Component Placement
Components are organized into functional blocks:
- Power supply on left side
- MCU in center
- Analog section on right
- Digital logic bottom-right

## 🔬 Applications

- Radiation detection and measurement
- Scintillation counting
- Environmental monitoring
- Educational radiation physics
- DIY Geiger counter replacement with better sensitivity

## 👥 Credits

**Original Designer**: Mihai Cuciuc (M. Cuciuc)
**Original Repository**: [github.com/mihaicuciuc/pomelo](https://github.com/mihaicuciuc/pomelo)
**Organization**: Safecast
**Date**: 2024-2025

Safecast appreciates the great work that Mihai has done and made publicly available. This project builds upon the original Pomelo design.

## 📄 License

![CC0](https://bgeigiezen.safecast.jp/wp-content/uploads/2023/07/CC_BY-SA_Andere_Wikis-300x100-1.png)

- **Hardware Design** (schematics, PCB layouts, design files): [CC0 1.0 Universal](https://creativecommons.org/publicdomain/cc0/1.0/)
- **Firmware and Software**: [MIT License](https://opensource.org/licenses/MIT)

This project is completely open source and free to use, modify, and distribute.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

- **Project Page**: [Pomelo on Crowd Supply](https://www.crowdsupply.com/pomelo-instrumentation/pomelo)
- **Safecast**: [https://safecast.org](https://safecast.org)
- Report issues through the repository's issue tracker

## ⚠️ Safety Warning

This board generates **high voltage** (up to 70V) for SiPM biasing. Handle with care:
- Do not touch HV traces while powered
- Use proper ESD protection
- Follow safe electronics handling practices
- Designed for educational and research purposes

---

**Made with ❤️ for the radiation detection community**
