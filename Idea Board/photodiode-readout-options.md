# Photodiode Readout Options — Idea Board

## Option 1: PIC18-Q41 (internal op-amp/comparator/ADC)

Reverse-biased photodiode into internal OPA1, routed internally to CMP1 (counts) and ADC (spectrum). Minimal external parts.

**Netlist**
- D1: Anode → PD_ANODE, Cathode → VCC_DIODE (+12V to +30V clean DC reverse bias)
- Feedback: R1 10MΩ ‖ C1 1.0pF between PD_ANODE and OPA1_OUT

**Pin map**

| PIC18-Q41 Pin | Peripheral | Connection |
|---|---|---|
| RA2 | OPA1IN+ | GND (or 0.5V virtual ground) |
| RA1 | OPA1IN- | Net: PD_ANODE |
| RA3 | OPA1OUT | Net: OPA1_OUT |
| internal | OPA1OUT→CMP1+/ADC_IN | no external wire, software-routed |

```
 +30V Bias ──[ 10kΩ ]──┬──(Cathode) Photodiode (Anode)
                       │
                     [100nF]
                       │
                      GND
                                ┌───────────────────────────────────┐
                                │            PIC18-Q41              │
                      ┌─────────┤ RA1 (OPA1IN-)                     │
                      │         │                                   │
                      ├─[ 10M ]─┤ RA3 (OPA1OUT) ──┐                 │
                      │         │                 │                 │
                      └─┤├──────┤                 │ (Internal)      │
                         1pF    │                 ├──► CMP1 (Counts)│
                                │                 │                 │
             GND ───────────────┤ RA2 (OPA1IN+)   └──► ADC (Spectrum│
                                └───────────────────────────────────┘
```

Drafting tips: keep C1/R1 as close to MCU pins as possible (parasitic capacitance kills energy resolution). Solid ground plane under analog front-end; no digital traces under it.

## Option 2: Dedicated readout ASIC (IDEAS IDE8411 / CITIROC-style)

Differential/specialized single-ended front end for femtocoulomb pulses, isolated from digital switching noise.

**Netlist**
- Power: dual clean analog rail (+3.3V analog, +3.3V digital, analog GND), separated by ferrite beads (L1, L2)
- Input: photodiode-to-ASIC track < 5mm (stray capacitance sensitive)

**Pin map**

| Pin group | Pin | Connection |
|---|---|---|
| Front-end | IN_A | Photodiode anode, AC-coupled via 10nF 100V NP0 cap if bias voltage high |
| Bias | VBIAS_IN | 100nF bypass to analog GND |
| Digital out | TRIG_OUT/DiscOut | MCU external interrupt (pulse counting) |
| Analog out | SHAPER_OUT/PeakHold | MCU analog input (spectral peak) |
| Control | MISO/MOSI/SCK/CS | MCU SPI bus (gain/threshold config) |

```
                     10nF 100V
   Photodiode ───────┤├────────► [ Pin: IN_A ]───────┐
   (w/ High Bias)                                    │
                                               ┌─────┴────────┐
                                               │  IDEAS ASIC  │
                                               │              ├─► TRIG_OUT ──► (To MCU Count Input)
   +3.3V_ANA ──[ Ferrite ]──┬──► [ Pin: VDD_A ]│              │
                            │                  │              ├─► PEAK_OUT ──► (To MCU ADC Input)
                          [100nF]              │              │
                            │                  │              │
                           GND                 └─────┬────────┘
                                                     │
   SPI Control Bus ──────────────────────────────────┘
```

## KiCad draft

`PhotodiodeReadout_Option1.kicad_sch` / `.kicad_pro` in this folder — Option 1 wired up.

- Sensor: project BOM (`bGeigieScint/Misc Docs/BOM.md`) uses a **SiPM, Broadcom AFBR-S4N44P014M 4x4mm** (matches `AFBR-S4N44P014M.stp` already in the repo root), not a generic photodiode — D1 is labeled accordingly, replacing the earlier BPW34 placeholder text.
- MCU: no PIC18-Q41 symbol exists in the local KiCad libraries (too new), so U1 uses **PIC18F26K22** as a stand-in — same RA1/RA2/RA3 pin names, correct for wiring intent, but not the real device. Swap the symbol once a Q41 library/symbol is available.
- Connectivity done via net labels (PD_ANODE, OPA1_OUT, GND, VCC_DIODE, VCC_30V, VDD) snapped to exact pin endpoints rather than drawn wires.
- ERC run: only "unused pin" warnings on unrouted GPIO and power-pin-source warnings from using local (not global/power) labels — expected for a conceptual sketch, not fab-ready.

## Open questions
- Generate C code for Option 1 internal op-amp/comparator/ADC config?
- Confirm SiPM bias voltage/network against AFBR-S4N44P014M datasheet (this sketch assumes the generic +12–30V reverse-bias scheme from the original photodiode netlist — SiPMs typically need a specific, tightly regulated bias, e.g. ~24-29V trimmed per-device).
