

## DIY CsI(Tl) Scintillator Build Guide

### Important: Spectral Matching Consideration

There's a **key consideration** with your component selection: CsI(Tl) has its emission peak at 550nm, but the Broadcom AFBR-S4N44P014M is a NUV-MT SiPM with high sensitivity towards the blue and near-UV region with peak PDE at 420nm.

This isn't a dealbreaker—the SiPM still has usable PDE (~25-30%) at 550nm—but you'll get reduced light collection efficiency compared to an RGB SiPM optimized for 550nm. RGB SiPMs developed for maximum PDE at 550nm are a good match for high-light-yield scintillators like CsI(Tl).

For your 10×10×30mm crystal with the 4×4mm SiPM, this should still work acceptably due to the exceptionally high light yield of CsI(Tl) (54 photons/keV, one of the brightest scintillators).

---

### 1. Crystal Preparation

**Wrapping the crystal:**
Wrap the CsI(Tl) crystal in Teflon tape on all faces except the one coupling to the SiPM. Teflon (PTFE tape) acts as an excellent diffuse reflector to maximize light collection toward the SiPM.

Alternatively, you can paint all but one side white to reflect scintillation light internally.

**Light-tight enclosure:**
A black 3D printed housing for the crystal acts both as mechanical protection and as a light shield. You can also use black electrical insulation tape or similar non-transparent material to wrap the whole assembly—use multiple layers just to be sure.

---

### 2. Optical Coupling

**Critical step:** Center the SiPM on the scintillator crystal and put some silicon grease or other special coupling material between the two parts to optimize optical coupling and minimize reflections. This step is important!

Recommended coupling materials include:
- BC-630 optical grease (Saint-Gobain)
- OC431A-LVP (SmartGel)  
- BLUESIL V-788
- Clear 3M VHB tape is another option

Optical grease applied between the crystal and SiPM minimizes photon loss at the interface and improves optical coupling.

For your 10×10mm crystal face with a 4×4mm SiPM, you're only covering ~16% of the crystal face. Consider whether you want to tile multiple SiPMs or use a larger SiPM (the AFBR-S4N66P014M is 6×6mm).

---

### 3. SiPM Biasing

**Bias voltage:** The Broadcom NUV-MT SiPMs operate around 50V total bias (breakdown voltage ~47-48V + overvoltage of 2-5V). Start conservatively at 2-3V overvoltage.

**Basic bias circuit:**
The SiPM consists of an array of microcells connected in parallel. For Broadcom SiPMs with AFBR-S4N serial numbers (p-on-n substrate), prefer the anode for signal extraction with positive bias via the cathode.

Recommended bias filter:
```
HV → 100Ω resistor → 100nF capacitor to GND → SiPM cathode
SiPM anode → signal output
```

---

### 4. Readout Circuit Options

**Option A: Simple resistor readout (easiest)**
Standard readout using a sense resistor: typically RS = 50Ω for 4mm SiPMs.

```
SiPM anode → 50Ω to GND
Signal taken from SiPM anode via coupling capacitor
```

**Option B: Transimpedance amplifier (better performance)**
A transimpedance amplifier circuit (TIA) based on a high-speed operational amplifier provides better signal-to-noise ratio.

Key TIA design considerations:
- Use a high-bandwidth op-amp (OPA656, AD8000, LMH6624)
- Feedback resistor: 1kΩ–10kΩ (determines gain)
- Add feedback capacitor (1-10pF) to prevent oscillation from SiPM capacitance
- A capacitance is placed in parallel with the feedback resistor to mitigate oscillations when coupled with the large input capacitance from a SiPM.

---

### 5. Signal Processing for Spectroscopy

**Integration time:** For CsI, an integration duration of 9µs was required due to its slow decay time (~1µs average).

**Pulse shaping:** CsI(Tl) requires longer shaping times than faster scintillators. Use 2-6µs shaping constants for good energy resolution.

**Temperature compensation:** 
The SiPM gain depends on temperature and can be compensated by adjusting the bias voltage. Adding a temperature sensor (like TMP126) near the SiPM allows for compensation.

---

### 6. Data Acquisition Options

**DIY MCA approach:**
Using a small custom PCB with a Raspberry Pi Pico microcontroller, a scintillator and SiPM, you can build your own gamma spectrometer with processing and multi-channel analyzer all on-board.

Projects like the Open Gamma Detector on Hackaday.io provide open-source firmware and PCB designs you could adapt.

**Simple oscilloscope/digitizer approach:**
Waveforms can be sampled by a digitizer (12 bit/250 MSPS) for pulse height analysis. A PicoScope or similar USB oscilloscope works well for prototyping.

---

### 7. Expected Performance

With your setup you can reasonably expect:
- Energy resolution: ~10-15% FWHM at 662 keV (Cs-137)
- Clear photopeaks for common isotopes
- Good low-energy sensitivity down to ~10-20 keV

SiPM coupled to CsI(Tl) can detect distinct and well-resolved peaks even at 5.9 keV from Fe-55 sources.

---

### Parts Summary

| Component | Notes |
|-----------|-------|
| CsI(Tl) 10×10×30mm | Your specified crystal |
| AFBR-S4N44P014M | 4×4mm SiPM (consider 6×6mm for better coverage) |
| Optical coupling | BC-630 or similar silicone grease |
| PTFE tape | For crystal wrapping |
| HV supply | 50-55V adjustable, low noise |
| Readout PCB | TIA or resistor-based |
| MCU/ADC | Pico, STM32, or external digitizer |

---

Would you like me to go deeper into any specific aspect? I can also sketch out a basic schematic for the readout circuit, or discuss integrating this with a Notecard for remote data logging if that's relevant to your Safecast work.