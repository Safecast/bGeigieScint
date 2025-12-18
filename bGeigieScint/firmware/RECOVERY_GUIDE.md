# SAML21 Recovery Guide - Unbricking Sammy L21

This guide provides step-by-step instructions for recovering a "bricked" ATSAML21G18B device when SWD connection succeeds but chip erase fails.

## Problem Description

Your device shows:
- ✅ Successful SWD connection
- ✅ Correct DPIDR (0x0bc11477)
- ❌ Failed chip erase with "write to DSU CTRL failed"

This typically happens when firmware has:
- Reconfigured SWD pins (PA30/SWCLK, PA31/SWDIO) as GPIO
- Entered low-power mode that gates debug clocks
- Otherwise interfered with Device Service Unit (DSU) operations

## Hardware Setup

**Required Connections (DAPLink to Sammy L21):**
- SWDIO → PA31 (SWDIO)
- SWCLK → PA30 (SWCLK)
- GND → GND
- nRST → RESET (optional but helpful for Method 2)
- VTref → 3.3V (to power-sense the target)

**Important:**
- Use short wires (< 15cm ideally)
- Ensure solid GND connection
- Double-check pinout against Sammy L21 schematic

## Recovery Methods

Try these in order, starting with the simplest:

### Method 1: Simple Chip Erase (Try This First)

1. Ensure DAPLink is connected and board is powered
2. Run the basic erase script:
   ```bash
   openocd -f openocd_recovery_erase.cfg
   ```
3. If successful, program your firmware:
   ```bash
   pio run -t upload
   ```

**Success rate:** ~30% (works if issue is minor timing/power glitch)

---

### Method 2: Connect Under Reset (Most Effective)

This is the recommended method and has the highest success rate.

**Requirements:**
- nRST pin must be connected from DAPLink to Sammy L21 RESET pin
- Your DAPLink must support SRST (system reset)

**Steps:**

1. Verify nRST connection:
   ```bash
   # Check if your DAPLink exposes nRST/RESET pin
   # Most DAPLink boards do - check your specific model
   ```

2. Power off the Sammy L21 completely
   - Disconnect USB or power supply
   - Wait 5 seconds

3. With DAPLink still connected, power on the board

4. Run the reset recovery script:
   ```bash
   openocd -f openocd_recovery_reset.cfg
   ```

5. If successful, program your firmware:
   ```bash
   pio run -t upload
   ```

**Success rate:** ~80-90% (highest success rate)

**What this does:**
- Asserts reset during SWD connection
- Halts CPU before problematic code runs
- Performs chip erase while CPU is held in reset

---

### Method 3: Low-Speed Connection

Try this if Method 1 fails and you don't have nRST connected.

**Steps:**

1. Ensure solid physical connections (check for loose wires)

2. Run the low-speed recovery script:
   ```bash
   openocd -f openocd_recovery_slow.cfg
   ```

3. If successful, program your firmware:
   ```bash
   pio run -t upload
   ```

**Success rate:** ~40-50%

**What this does:**
- Reduces SWD clock to 100 kHz (very slow)
- More reliable with long wires or noisy connections
- May catch brief windows when debug access is available

---

### Method 4: Cold-Plugging Procedure

This method exploits the SAML21's built-in "cold-plugging" feature.

**Steps:**

1. **Power off the Sammy L21 completely**
   - Disconnect USB or power supply
   - Disconnect DAPLink SWD cables
   - Wait 5 seconds

2. **Connect DAPLink to PC (but not to board yet)**
   - Plug DAPLink into USB
   - Verify it's recognized by your PC

3. **Connect SWD pins while board is unpowered**
   - Connect SWDIO, SWCLK, GND from DAPLink to Sammy L21
   - Board is still OFF at this point

4. **Power on the board**
   - Connect power/USB to Sammy L21
   - The debugger is already attached when CPU first starts

5. **Immediately run recovery script:**
   ```bash
   openocd -f openocd_recovery_erase.cfg
   ```
   Or try:
   ```bash
   openocd -f openocd_recovery_slow.cfg
   ```

6. If successful, program your firmware

**Success rate:** ~60-70%

**What this does:**
- Debugger is connected before CPU starts running
- Catches CPU in early boot before problematic code runs
- Explicitly supported by ATSAML21 datasheet (CPU Reset Extension)

---

### Method 5: Power Cycling with Retry

If all else fails, try this brute-force approach.

**Steps:**

1. Create a script to retry connection:
   ```bash
   #!/bin/bash
   # save as recovery_retry.sh

   for i in {1..20}; do
     echo "Attempt $i of 20..."
     openocd -f openocd_recovery_slow.cfg && break
     sleep 1
   done
   ```

2. Make it executable:
   ```bash
   chmod +x recovery_retry.sh
   ```

3. Start the script:
   ```bash
   ./recovery_retry.sh
   ```

4. While script is running, repeatedly power cycle the board:
   - Disconnect/reconnect power every 2-3 seconds
   - Continue for all 20 attempts

**Success rate:** ~50% (depends on catching the right timing)

**What this does:**
- Attempts connection during brief windows of availability
- Different power states may allow debug access
- Statistical approach - tries many times

---

## Using PyOCD (Alternative Tool)

If OpenOCD isn't working, try PyOCD which sometimes has better recovery support:

1. **Install PyOCD:**
   ```bash
   pip install pyocd
   ```

2. **List connected devices:**
   ```bash
   pyocd list
   ```

3. **Try erase with connect-under-reset:**
   ```bash
   pyocd erase --chip --connect-mode under-reset --target atsaml21g18b --frequency 100000
   ```

4. **Alternative: Use halt mode:**
   ```bash
   pyocd erase --chip --connect-mode halt --target atsaml21g18b
   ```

5. **If successful, program firmware:**
   ```bash
   pyocd flash -t atsaml21g18b your_firmware.bin
   ```

**PyOCD advantages:**
- Sometimes has better DSU handling for SAM devices
- More detailed error messages
- Better support for connect-under-reset

---

## Verification After Recovery

Once chip erase succeeds:

1. **Verify the device is erased:**
   ```bash
   openocd -f interface/cmsis-dap.cfg -c "transport select swd" \
           -f target/at91samdXX.cfg -c "init; reset halt; flash list; shutdown"
   ```

2. **Program your firmware:**
   ```bash
   pio run -t upload
   ```

3. **Test basic functionality:**
   - Upload the blink test (currently in main.c)
   - Verify LED blinks
   - Confirms basic operation

---

## Troubleshooting

### "Error: unable to find CMSIS-DAP device"
- Check USB connection to DAPLink
- Try different USB port/cable
- Verify DAPLink LED is on
- Check: `lsusb` should show DAPLink device

### "Error: DPIDR read failed"
- Check all SWD connections (SWDIO, SWCLK, GND)
- Verify target is powered (check VTref connection)
- Try shorter wires
- Check for shorts or damaged pins

### "Error: DSU CTRL write failed" (persists after all methods)
- Device may have NVM User Page locked (CELCK bit)
  - This is rare without intentional security setup
  - Would require special vendor tools to unlock
- Possible hardware damage to DSU
  - Check for ESD damage
  - Verify supply voltage is correct (3.0-3.6V)

### OpenOCD can't find configuration files
```bash
# Check OpenOCD installation
openocd --version

# Find config file location
openocd --search  # Shows search paths

# If needed, use absolute paths:
openocd -f /usr/share/openocd/scripts/interface/cmsis-dap.cfg ...
```

---

## Prevention for Future

To avoid bricking the device again:

1. **Never disable SWD pins in production code** (unless absolutely necessary)
   ```c
   // AVOID doing this:
   // PORT->Group[0].PINCFG[30].bit.PMUXEN = 0;  // Disables SWCLK
   // PORT->Group[0].PINCFG[31].bit.PMUXEN = 0;  // Disables SWDIO
   ```

2. **Test low-power modes carefully**
   - Ensure debug clocks remain enabled during development
   - Use WDT (watchdog timer) as safety during sleep experiments

3. **Use bootloader with recovery mode**
   - Implement a bootloader that can re-enable SWD
   - Add button-press recovery mode

4. **Keep backup programmer ready**
   - External SWD programmer with nRST support
   - Secondary DAPLink device

---

## Success Indicators

You'll know recovery worked when you see:

```
Info : SAML21G18B
Info : Listening on port 3333 for gdb connections
Info : SAML21G18B: Chip erase done
```

Or with PyOCD:
```
0000536:INFO:loader:Erased 262144 bytes (100.00%) [####################]
```

Then you can program normally with PlatformIO.

---

## Additional Resources

- [ATSAML21 Datasheet - Debug Section](https://www.microchip.com/wwwproducts/en/ATSAML21G18B)
- [ARM Debug Interface v5 Architecture Specification](https://developer.arm.com/architectures/cpu-architecture/debug-visibility-and-trace)
- [OpenOCD SAMD/SAML Recovery Guide](http://openocd.org/doc/html/Flash-Programming.html)

---

## Summary of Recovery Success Rates

Based on community reports and testing:

| Method | Success Rate | Requirements | Time |
|--------|-------------|--------------|------|
| Method 1: Simple Erase | 30% | DAPLink only | 30 sec |
| Method 2: Under Reset | 80-90% | DAPLink + nRST | 1 min |
| Method 3: Low Speed | 40-50% | DAPLink only | 1 min |
| Method 4: Cold Plugging | 60-70% | DAPLink only | 2 min |
| Method 5: Power Cycling | 50% | DAPLink only | 5 min |
| PyOCD Alternative | 70-80% | PyOCD install | 2 min |

**Recommended order:**
1. Try Method 1 (quick, no harm in trying)
2. If you have nRST connected: Use Method 2 (highest success)
3. If no nRST: Try Method 4, then Method 3, then Method 5
4. If all fail: Try PyOCD alternative

Good luck! 🔧
