# Scintillator PCBs

In this architecture, there are two printed circuit boards. A small one, the readout, is nested inside the hood covering the scintillator. The second is the carrier on which the scintillator is mounted with headers protruding from the bottom of the hood.

 
## Updates

* 2026-05-06 Hood base for readout1_A booked to be 3D printed at library
* 2026-04-28 readout1_A sent to JLCPCB


## Readout PCB - Direct Connection to SiPM

The readout carries the SiPM itself as well as the anode resistor and the decoupling capacitor on the bias supply. The two 3-pos headers are meant to protrude from the bottom of the hood base, to be soldered into the carrier. The readout also carries a temperature sensor used by the firmware for calibration.


## Versions

### Version `readout1`: Two 3-pin headers

The PCB placement of the SiPM is at the 0,0 origin. The headers and mounting holes are symmetric along the Y-axis. With two headers, the scintillator hood must be vertical on the carrier.


### Version `readout2`: A single 6-pin header

(Not started yet). This version allows for more mounting flexibility for the scintillator hood -- laterally or vertically. However, it complicates the PCB layout and the base of the hood.


## Carrier PCB - Carries the scintillator and interprets the pulses 

The carrier PCB receives the readout PCB and hood through the headers protruding from the bottom, and conditions the scintillator output through amplifiers, comparators and integrators. The signals are digitized by either a standalone high speed ADC, or the ADC built into the microcontroller -- both approaches will be tried. Initially, the microcontroller  is the Adafruit Feather M0 Adalogger, mostly because it was already on hand though it seems to have the necessary capabilities. It can also be powered from a 3.7V Li-Ion battery.



### Version `carrier1_Adalogger_M0_2x3pin`: Two 3-pin headers

The hood has two 3-pos headers. The microcontroller is the Adafruit Feater M0 Adalogger. Analgog signal conditioning parts TBD -- need sufficiently high speed and low noise op-amps and ADC.


