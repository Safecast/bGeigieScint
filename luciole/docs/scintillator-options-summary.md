# Luciole — Low-Cost Scintillator Path Summary

*Repo review summary, 2026-07-06. Based on README.md, electronics/readme.md, carrier1/readout1 designs, BOMs, and docs/.*

## Recommended path

**Plastic scintillator (EJ-200/BC-408 class, 10×10×20 mm) + MicroFC-60035 SiPM + existing readout1/carrier1 boards**, then move to CsI(Tl) for spectroscopy once the signal chain is proven. Fits well under the CA$250 goal.

## Scintillator options

| Option | Source | ~Price (small block) | Spectroscopy? | Notes |
|---|---|---|---|---|
| **Plastic (PVT, BC-408/EJ-200 type)** ✅ | EPIC Crystal, OST Photonics (China) | **CA$15–50** | No (counting only, like G-M) | Rugged, non-hygroscopic, machinable. Matches the 10×10×20 mm hood. Best first step. |
| **CsI(Tl) crystal** | EPIC Crystal (datasheet in `docs/scintillators/epic-crystal/`) | **CA$40–100** (10×10×20 mm) | **Yes** — 540 nm matches SiPM well | Slightly hygroscopic but manageable; slow decay (~1 µs) suits the slow-ADC + peak-hold approach. Best value for a real spectrometer. |
| GAGG(Ce) | EPIC, AliExpress vendors | CA$80–150 | Yes, excellent | Non-hygroscopic, bright, but pricier. Upgrade path. |
| NaI(Tl) packaged | Surplus/eBay, EPIC | CA$100–250 | Yes | Hygroscopic, needs hermetic can; blows the budget with new stock. |
| Luxium / Eljen (USA) | — | US$3,000 MOQ / no reply | — | Already ruled out in README. Correct call. |

## Rest of the signal chain (already in repo)

| Block | Part (in repo) | ~Price |
|---|---|---|
| SiPM | OnSemi MicroFC-60035-SMT | CA$35–45 (3 mm 30035 ~CA$20 with smaller crystal) |
| Bias supply ~29 V | **Not yet on carrier1 rev A** — `+BIAS` comes from a bench supply via J7/J8. MAX5026 boost planned (`architecture/MAX5026_boost_converter.txt`) | CA$5–8 |
| Front-end | OPA2354 ×2, 74HCU04/74HC14, passives | CA$10–15 |
| MCU + display | Feather M0 Adalogger + 128×64 OLED FeatherWing | CA$45–55 |
| PCBs | readout1 + carrier1 at JLCPCB | CA$10–20 /set (qty 5) |
| Hood/case | 3D-printed (in `mech/`) | CA$5 |
| Optical grease, wrap (Teflon/ESR film) | Saint-Gobain BC-630 or generic | CA$10–15 |

**Total: ~CA$135–200 with CsI(Tl); ~CA$120–160 with plastic** — under budget either way.

## Suggested sequence

1. **Order both** a plastic block and a CsI(Tl) 10×10×20 mm from EPIC Crystal (sells small quantities online — the gap Eljen/Luxium left). Combined ~CA$60–120 shipped.
2. Validate counting mode first with plastic + the CMOS-inverter "quick-and-dirty" chain — proves SiPM, bias, hood light-tightness.
3. Move to Fast-output amplifier + peak-and-hold (physicsopenlab-style) with CsI(Tl) for actual spectroscopy — its ~1 µs pulses are much friendlier to the SAMD21 12-bit ADC than plastic's ~2 ns pulses.
4. Compare against the LND7317 sensitivity requirement; CsI(Tl) at this volume should comfortably beat it for gamma.

## Caveats (from schematic review)

- The OPA2354/TPH2502 TIA path is fine for CsI(Tl), but for plastic's nanosecond pulses only the counting path is viable with the MCU ADC — don't attempt plastic spectroscopy with this chain.
- Carrier1 rev A has **no onboard SiPM bias generator** — designing in the MAX5026 boost (or MAX1932) is a required step before this is a standalone instrument.
- Readout boards use a TMP36 analog temp sensor (not the TMP126 in docs/) for gain compensation.
- Carrier1 implements three parallel readout sites: (1) peak-and-hold with MOSFET reset, (2)–(3) transistor/op-amp voltage-amp variants — bench comparison will pick the winner.
