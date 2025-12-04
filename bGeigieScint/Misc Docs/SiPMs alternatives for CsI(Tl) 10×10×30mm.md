

## SiPM Options for CsI(Tl) (550nm emission peak)

### Best Spectral Match: RGB SiPMs (Peak PDE at 550nm)

| Model              | Manufacturer             | Size  | Peak λ | PDE at 550nm | Buy From                 |
| ------------------ | ------------------------ | ----- | ------ | ------------ | ------------------------ |
| **SiPM-RGB4S-SMD** | First Sensor (ams OSRAM) | 4×4mm | 550nm  | 32.5%        | Mouser                   |
| **ASD-RGB4S-P**    | AdvanSiD (FBK)           | 4×4mm | 550nm  | 32.5%        | Direct from advansid.com |
| **ASD-RGB3S-P**    | AdvanSiD (FBK)           | 3×3mm | 550nm  | 32.5%        | Direct from advansid.com |

AdvanSiD offers RGB-SiPM technology: N-on-P silicon photomultipliers for the detection of visible light with peak sensitivity wavelength at 550nm, spectral response range 350 to 900nm.

The RGB SiPM is developed for maximum PDE at 550nm, which is a good match for high-light-yield scintillators such as CsI:Tl.

**Note:** For CsI, the energy resolution is actually better with blue-sensitive SiPMs because of lower dark count rate. The RGB SiPMs have DCR < 200 kHz/mm² at 4V overvoltage which is higher than NUV types. So the trade-off is: better spectral match vs. higher noise.

---

### Excellent Alternative: Hamamatsu S14420 Series (Visible/NIR enhanced)

| Model             | Size  | Peak λ     | PDE at 550nm  | Price     | Buy From                |
| ----------------- | ----- | ---------- | ------------- | --------- | ----------------------- |
| **S14420-3050MG** | 3×3mm | ~550-600nm | 40% at 600nm  | ~$50-80   | Hamamatsu shop, DigiKey |
| **S14420-6050MG** | 6×6mm | ~550-600nm | ~40% at 600nm | ~$100-150 | Hamamatsu shop          |

The S14420 series is an MPPC for the visible to near infrared region. It provides higher photon detection efficiency than the previous product (S13360 series) in the visible to near infrared region.

**Advantages:** Lower dark count, better availability, excellent documentation

---

### Popular Choice: onsemi C-Series / J-Series (Blue-optimized but proven with CsI)

| Model                 | Size  | Peak λ | PDE at 550nm | Price | Buy From        |
| --------------------- | ----- | ------ | ------------ | ----- | --------------- |
| **MICROFC-60035-SMT** | 6×6mm | 420nm  | ~28%         | ~$23  | DigiKey, Mouser |
| **MICROFJ-60035-TSV** | 6×6mm | 420nm  | ~30%         | ~$27  | DigiKey, Mouser |

SensL J-series 60035 SiPM coupled to CsI(Tl) crystal detected distinct and well-resolved 5.9 keV X-ray peaks from Fe-55 — proven to work well with CsI(Tl) despite spectral mismatch.

J-Series sensors achieve PDE of 50% with sensitivity extending down into the UV, industry-leading low dark count rates of 50 kHz/mm².

---

### Standard Blue-Optimized: Hamamatsu S14160 Series

| Model             | Size  | Peak λ | Notes                                                 | Price |
| ----------------- | ----- | ------ | ----------------------------------------------------- | ----- |
| **S14160-6050HS** | 6×6mm | ~450nm | Higher PDE 50% at λp, lower operation voltage VBR=38V | ~$80  |

S14160 achieved best thresholds at +2.5V overvoltage. CsI(Tl) light yield was 6× higher than BGO — the high light output of CsI(Tl) compensates for spectral mismatch.

---

## My Recommendation

For your DIY CsI(Tl) project, I'd suggest one of these approaches:

**Option 1: Best spectral match**

- **First Sensor SiPM-RGB4S-SMD** from Mouser
- Or contact **AdvanSiD** directly for ASD-RGB4S-P
- Available sizes: 1×1mm², 3×3mm², 4×4mm²

**Option 2: Best overall value + proven performance**

- **onsemi MICROFC-60035-SMT** (6×6mm, ~$23 from DigiKey)
- Widely used, well-documented, proven with CsI(Tl)
- Lower noise than RGB types

**Option 3: Best NIR/visible sensitivity from major supplier**

- **Hamamatsu S14420-3050MG** or larger
- High PDE at 600nm, low crosstalk, low afterpulses
- Available directly from Hamamatsu shop, ships 4 days after order confirmation

Given your experience with Safecast hardware, the **onsemi MICROFC-60035-SMT** is probably the most practical choice — it's affordable, readily available, well-documented, and despite the spectral mismatch, CsI(Tl)'s exceptional light yield (54 photons/keV) means you'll still get excellent results. The 6×6mm size also gives better coverage of your 10×10mm crystal face.

Would you like me to look into specific readout circuits optimized for any of these SiPMs?
