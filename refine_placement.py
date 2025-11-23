#!/usr/bin/env python3
"""
Refine component placement based on detailed top-side reference image
Board dimensions: 40mm x 100mm from (50,50) to (90,150)
"""

import re

# Updated component placement zones based on top-side photo
REFINED_ZONES = {
    # Right side - USB and power input
    'USB': {'x': 87, 'y': 100, 'desc': 'USB-C connector on right edge'},
    'USB_PROTECTION': {'x': 84, 'y': 95, 'desc': 'USB ESD protection'},

    # Left side - Pin headers and connectors
    'LEFT_HEADERS': {'x': 53, 'y': 80, 'desc': 'Left side pin headers'},
    'POWER_INPUT': {'x': 53, 'y': 120, 'desc': 'Power input connectors'},

    # Center-left - Power management
    'POWER_LDO': {'x': 60, 'y': 100, 'desc': 'Power regulators'},
    'POWER_CAPS': {'x': 58, 'y': 110, 'desc': 'Power bulk caps'},
    'POWER_INDUCTORS': {'x': 58, 'y': 95, 'desc': 'Power inductors'},

    # Center - MCU section
    'MCU': {'x': 72, 'y': 100, 'desc': 'Main microcontroller'},
    'MCU_CRYSTAL': {'x': 67, 'y': 93, 'desc': 'MCU crystal'},
    'MCU_PASSIVES': {'x': 75, 'y': 95, 'desc': 'MCU passives'},
    'BUTTON_RST': {'x': 60, 'y': 92, 'desc': 'Reset button'},

    # Top center - Debug header
    'DEBUG': {'x': 70, 'y': 54, 'desc': 'J-LINK debug header'},

    # Right-center - Analog section
    'ANALOG_FRONTEND': {'x': 80, 'y': 100, 'desc': 'Analog signal chain'},
    'ANALOG_PASSIVES': {'x': 82, 'y': 95, 'desc': 'Analog passives'},

    # Right side - Expansion and GPIO
    'EXPANSION_TOP': {'x': 85, 'y': 70, 'desc': 'Top expansion headers'},
    'EXPANSION_MID': {'x': 85, 'y': 100, 'desc': 'Mid expansion headers'},
    'EXPANSION_BOT': {'x': 85, 'y': 130, 'desc': 'Bottom expansion headers'},

    # Bottom-right - Logic and support
    'LOGIC_ICS': {'x': 78, 'y': 120, 'desc': 'Logic ICs'},
    'SUPPORT_CIRCUITS': {'x': 70, 'y': 130, 'desc': 'Support circuits'},

    # Status indicators
    'LED_PWR': {'x': 87, 'y': 56, 'desc': 'Power LED'},
}

# Refined component placement based on photo
REFINED_PLACEMENT = {
    # USB section (right edge)
    'USBC1': ('USB', 0),
    'D1': ('USB_PROTECTION', 90),  # TVS diode
    'R1': ('USB_PROTECTION', 90),
    'R2': ('USB_PROTECTION', 90),
    'R3': ('USB_PROTECTION', 90),
    'R7': ('USB_PROTECTION', 90),

    # Power management (center-left)
    'U2': ('POWER_LDO', 0),   # 3.3V LDO
    'U5': ('POWER_LDO', 0),   # Power LDO
    'U11': ('POWER_LDO', 0),  # Analog LDO
    'C6': ('POWER_CAPS', 0),
    'C4': ('POWER_CAPS', 0),
    'L1': ('POWER_INDUCTORS', 0),
    'L2': ('POWER_INDUCTORS', 0),
    'L3': ('POWER_INDUCTORS', 0),

    # Left side headers
    'P1': ('POWER_INPUT', 90),
    'P2': ('POWER_INPUT', 90),
    'H2': ('LEFT_HEADERS', 90),
    'H3': ('LEFT_HEADERS', 90),

    # MCU section (center)
    'U1': ('MCU', 45),  # Main MCU
    'X1': ('MCU_CRYSTAL', 0),
    'C42': ('MCU_CRYSTAL', 90),
    'C43': ('MCU_CRYSTAL', 90),
    'BUT1': ('BUTTON_RST', 0),

    # Debug (top center)
    'J-LINK1': ('DEBUG', 0),

    # Analog section (right-center)
    'U4': ('ANALOG_FRONTEND', 90),  # LMV793 opamp
    'U6': ('ANALOG_FRONTEND', 90),  # TLV3201 comparator
    'U7': ('ANALOG_FRONTEND', 90),  # OPA357 opamp
    'U13': ('ANALOG_FRONTEND', 90), # TLV7031 comparator
    'Q4': ('ANALOG_FRONTEND', 90),
    'Q5': ('ANALOG_FRONTEND', 90),

    # Logic section (bottom-right)
    'U3': ('LOGIC_ICS', 0),   # MC14043 latch
    'U8': ('LOGIC_ICS', 90),  # Comparator
    'U9': ('LOGIC_ICS', 0),   # PTC
    'U10': ('LOGIC_ICS', 90), # AND gate
    'U12': ('SUPPORT_CIRCUITS', 0), # Level shifter
    'U14': ('LOGIC_ICS', 90),
    'Q1': ('LOGIC_ICS', 90),

    # Expansion headers (right side)
    'H5': ('EXPANSION_TOP', 90),
    'MEAS1': ('EXPANSION_BOT', 90),
    'U15': ('EXPANSION_MID', 90),

    # Status LED
    'LED1': ('LED_PWR', 180),
    'R26': ('LED_PWR', 90),

    # Diodes
    'D9': ('POWER_INDUCTORS', 90),
}

def refine_component_positions(pcb_file):
    """Update component positions based on refined placement map"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    updates = 0

    # Track offsets for grouped components
    resistor_offset = [0, 0]
    cap_offset = [0, 0]
    tp_offset = [0, 0]
    diode_offset = [0, 0]

    def get_position(ref, zone_name, rotation, offset=(0, 0)):
        """Get component position from zone"""
        if zone_name not in REFINED_ZONES:
            zone_name = 'MCU'

        zone = REFINED_ZONES[zone_name]
        x = zone['x'] + offset[0]
        y = zone['y'] + offset[1]
        return (x, y, rotation)

    def replace_position(match):
        nonlocal updates, resistor_offset, cap_offset, tp_offset, diode_offset

        full_block = match.group(0)

        # Extract reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', full_block)
        if not ref_match:
            return full_block

        ref = ref_match.group(1)

        if ref.startswith('#PWR'):
            return full_block

        # Determine position
        zone = None
        rotation = 0
        offset = [0, 0]

        if ref in REFINED_PLACEMENT:
            zone, rotation = REFINED_PLACEMENT[ref]
        elif ref.startswith('R'):
            zone = 'MCU_PASSIVES'
            rotation = 90
            offset = resistor_offset.copy()
            resistor_offset[0] += 1.5
            if resistor_offset[0] > 12:
                resistor_offset[0] = 0
                resistor_offset[1] += 2
        elif ref.startswith('C'):
            zone = 'MCU_PASSIVES'
            rotation = 0
            offset = cap_offset.copy()
            cap_offset[0] += 1.5
            if cap_offset[0] > 12:
                cap_offset[0] = 0
                cap_offset[1] += 2
        elif ref.startswith('TP'):
            zone = 'MCU'
            rotation = 0
            offset = tp_offset.copy()
            tp_offset[0] += 3
            if tp_offset[0] > 15:
                tp_offset[0] = 0
                tp_offset[1] += 3
        elif ref.startswith('L'):
            zone = 'POWER_INDUCTORS'
            rotation = 0
        elif ref.startswith('D'):
            zone = 'MCU_PASSIVES'
            rotation = 90
            offset = diode_offset.copy()
            diode_offset[0] += 2
            if diode_offset[0] > 8:
                diode_offset[0] = 0
                diode_offset[1] += 2
        elif ref.startswith('Q'):
            zone = 'LOGIC_ICS'
            rotation = 90

        if zone:
            new_x, new_y, new_rot = get_position(ref, zone, rotation, offset)

            # Replace position
            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {new_x} {new_y} {new_rot})',
                full_block,
                count=1
            )

            if new_block != full_block:
                updates += 1
                if ref in REFINED_PLACEMENT:
                    print(f"Refined {ref:8s} -> ({new_x:5.1f}, {new_y:5.1f}, {new_rot:3.0f}°)")

            return new_block

        return full_block

    # Process all footprints
    pattern = r'\(footprint\s+[^\n]+\n(?:.*?\n)*?\t\)'
    new_content = re.sub(pattern, replace_position, content, flags=re.MULTILINE)

    # Write updated file
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\nRefined {updates} component positions")
    return updates

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("Refining component placement based on top-side reference...\n")

    count = refine_component_positions(pcb_file)

    print(f"\nDone! Refined placement for {count} components.")
    print("\nKey improvements:")
    print("- USB-C moved to right edge")
    print("- Pin headers aligned on left side")
    print("- Power section organized center-left")
    print("- Analog chain positioned right-center")
    print("- Debug header at top center")
    print("\nOpen in KiCad to review and fine-tune!")
