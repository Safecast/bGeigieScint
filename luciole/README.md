# Projet Luciole

A low cost radiation detection and measurement spectrometer for fixed location monitoring and reporting using a scintillator crystal and silicon photomultiplier. Une luciole serait un peu comme les petits éclairs de rayonnement dans le scintillateur.

## Functional requirements
* Scintillation detector (polymer or inorganic crystal)
* Sensitivity to gamma equal to or better than LND7317 G-M tube (beta optional)
* Temperature compensated measurements
* Communicate over WiFi in-house, optional cellular or satellite (Blues.io, brioconcept.com)
* Measurement uploads in Safecast format (existing LOG or new spectrum format)
* Low power with battery backup
* Easy to read display
* Simple UI for inexperienced users
* Touch OLED display, on-screen buttons
* Self calibrating or simple calibration procedure
* Not ruggedized, indoor use only
* Off-the-shelf case (Hammond, Takachi, etc.) or 3D printed
* USB-C charging and programming
* Build as a kit with minimal soldering

## Non-functional requirements
* Cost goal is sub CA$250.
* Parts reliably available from distribution


## Scintillators

Plastic (organic) scintillators are rugged and expected to be cheaper than inorganic crystals. They do not suffer from the limitations of some inorganic crystals, such as hygroscopic (absorb moisture) and cleavages.

### Possible sources

OST Photonics (China)
https://www.ostphotonics.com/products/sp101-plastic-scintillators.html
Do they offer off-the-shelf parts?

EPIC Crystal Co (China)
Online retail of organic and inorganic scintillators.

Luxium (USA)
Does not deal with less than minimum order USD3,000.

Eljen (USA)
Emailed Apr 14 asking about small quantities. No response. Abandon.


# Project structure

The prototype is more of a proof of concept than the precursor to a production device. It's a "throw it all at the wall to see what sticks" situation.

## Scintillator readout board
Readout is a small PCB holds a 6x6mm^2 silicon photomultiplier (SiPM). The device chosen for the first pass is OnSemi 60035 C-Series SiPM. The C-Series has an extra terminal, called Fast, that provides a voltage pulse proportional to the detection current. The other components on the board are a quench resistor, a power supply decoupling capacitor and an IC temperature sensor. Communication with the main board is through a pair of 3-pin headers.

Readout is packaged in a 3D printed enclosure consisting of a base and a hood. When assembled, the base and the hood block external light and hold the scintillator in place on the SiPM. The SiPM is coupled to the scintillator with optically clear grease to remove any air gaps.

## Main board
The main board, carrier, accepts the readout module and amplifies the pulses enough for the microcontroller's ADC to digitize for further processing. Several detection and amplification approaches are implemented on the carrier1 board.

### Fast output amplifiers
The Fast terminal provides a voltage pulse proportional to the detection current. The pin is capacitor coupled to the diode array and the signal is suitable for a high input impedance amplifier. Two amplifier architectures are tried. 

1 - Quick-and-dirty amplifier using an unbuffered CMOS digital inverter with a feedback resistor, sending its output to a Schmitt trigger inverter. This combination is expect to provide the minimum detection, outputting pulses without energy measurement, the same as a Geiger-Muller detector.

2 - Voltage amplifier for the Fast output, providing peak pulse voltage proportional to the detected energy.

### Avalanche photodiode current amplifiers
The avalance current can be converted to a voltage pulse across the 50 ohm quench resistor in series between the SiPM anode and ground and measured after a conventional voltage amplifier.

The avalanche current can be amplified and converted to a voltage signal using a transimpedance amplifier (TIA) receiving the diode avalanche current pulse. The output is expected to be a pulse with height proportional to the detected particle energy. The pulse is integrated by a RC low pass filter to meet the relatively slow ADC acqisition time. It requires a different configuration of the SiPM, where the anode is connected directly to the op-amp minus terminal and the quench resistor R1 is not populated on the readout board.

### Peak and hold detector
A peak and hold detector on the Fast output can hold the pulse height steady during the ADC acquisition cycle. This is something that seems to work on physicsopenlab.org. A voltage amplifier amplifies the Fast output and drives a diode peak detector. The peak is held until the microcontroller can digitize the voltage, then the microcontroller resets the peak by turning on a MOSFET across the hold capacitor. This scheme may need the CMOS inverter to detect the pulse and initiate the microcontroller conversion cycle.
https://physicsopenlab.org/2017/11/28/front-end-electronics-for-sipm/

## Microcontroller
The MCU is a Adafruit Feather M0 Adalogger with a 128x64 monochrome OLED. It was chosen because it was in a parts bin on my workbench. However, it's a reasonable choice for memory, speed and a 12-bit ADC. 


