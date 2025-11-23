#!/usr/bin/env python3
"""
Reposition components on PomeloCore PCB based on reference board layout
Board dimensions: 40mm x 100mm
Updates existing footprints in place
"""

import re

# Component placement zones (in mm, absolute coordinates)
# Board outline will be from (50,50) to (90,150)
ZONES = {
    # Left side (0-30mm from left edge) - Power and USB
    'USB': {'x': 54, 'y': 100, 'desc': 'USB connector and protection'},
    'POWER_LDO': {'x': 62, 'y': 110, 'desc': 'Main power regulators'},
    'POWER_CAPS': {'x': 62, 'y': 95, 'desc': 'Power supply capacitors'},
    'POWER_INPUT': {'x': 55, 'y': 80, 'desc': 'Power input connectors'},

    # Center (30-60mm from left) - MCU and core
    'MCU': {'x': 70, 'y': 100, 'desc': 'Main microcontroller'},
    'MCU_CRYSTAL': {'x': 65, 'y': 92, 'desc': 'MCU crystal'},
    'MCU_CAPS': {'x': 75, 'y': 105, 'desc': 'MCU decoupling caps'},
    'DEBUG': {'x': 70, 'y': 55, 'desc': 'Debug header'},
    'BUTTON': {'x': 60, 'y': 92, 'desc': 'Reset button'},

    # Right side (60-100mm from left) - Analog and interfaces
    'ANALOG': {'x': 78, 'y': 100, 'desc': 'Analog frontend'},
    'LOGIC': {'x': 78, 'y': 115, 'desc': 'Logic circuits'},
    'EXPANSION': {'x': 85, 'y': 80, 'desc': 'Expansion headers'},
    'LED': {'x': 87, 'y': 58, 'desc': 'Status LED'},
}

# Component to zone mapping with rotation
COMPONENT_PLACEMENT = {
    # Power and USB section
    'USBC1': ('USB', 0),
    'D1': ('USB', 90),  # TVS diode near USB
    'R1': ('USB', 90),   # USB pullup
    'R3': ('USB', 90),   # USB pullup
    'R2': ('USB', 90),   # USB CC resistor
    'R7': ('USB', 90),   # USB CC resistor
    'U2': ('POWER_LDO', 0),  # 3.3V LDO
    'U5': ('POWER_LDO', 0),  # TPS7A2030 LDO
    'U11': ('POWER_LDO', 0),  # LT3014 LDO for analog
    'C6': ('POWER_CAPS', 0),  # 10uF bulk
    'C4': ('POWER_CAPS', 0),  # 10uF bulk
    'P1': ('POWER_INPUT', 90),   # Power header
    'P2': ('POWER_INPUT', 90),   # Power header
    'L1': ('POWER_CAPS', 0),  # Power inductor
    'L2': ('POWER_CAPS', 0),
    'L3': ('POWER_CAPS', 0),

    # MCU section
    'U1': ('MCU', 45),  # ATSAML21 - rotated 45° for optimal routing
    'X1': ('MCU_CRYSTAL', 0),  # Crystal next to MCU
    'C42': ('MCU_CRYSTAL', 90),  # Crystal cap
    'C43': ('MCU_CRYSTAL', 90),  # Crystal cap
    'J-LINK1': ('DEBUG', 0),   # Debug header
    'BUT1': ('BUTTON', 0),  # Reset button

    # Analog section (right side)
    'U7': ('ANALOG', 90),  # OPA357 opamp
    'U6': ('ANALOG', 90),  # TLV3201 comparator
    'U13': ('ANALOG', 90),  # TLV7031 comparator
    'U4': ('ANALOG', 90),  # LMV793 opamp

    # Logic section
    'U3': ('LOGIC', 0),  # MC14043 latch
    'U8': ('LOGIC', 90),  # TLR341G comparator
    'U14': ('LOGIC', 90),  # TLR341G comparator
    'U10': ('LOGIC', 90),  # 74LVC1G08 AND gate
    'U9': ('LOGIC', 0),  # MF-ASML020/6-2 PTC
    'U12': ('LOGIC', 0),  # TXU0202 level shifter

    # Interfaces (right edge)
    'H2': ('EXPANSION', 90),  # Expansion header
    'H3': ('EXPANSION', 90),  # Expansion header
    'H5': ('EXPANSION', 90),  # Expansion header
    'MEAS1': ('EXPANSION', 90),  # Measurement header
    'U15': ('EXPANSION', 90),  # Pin socket connector

    # LED and transistors
    'LED1': ('LED', 180),
    'R26': ('LED', 90),  # LED resistor
    'Q1': ('LOGIC', 0),
    'Q4': ('ANALOG', 90),
    'Q5': ('ANALOG', 90),

    # Diodes
    'D9': ('POWER_CAPS', 90),  # Schottky diode
}

def get_component_position(ref, zone_name, rotation, base_offset=(0, 0)):
    """Calculate component position based on zone"""
    if zone_name not in ZONES:
        zone_name = 'MCU'  # default

    zone = ZONES[zone_name]
    x = zone['x'] + base_offset[0]
    y = zone['y'] + base_offset[1]

    return (x, y, rotation)

def reposition_components(pcb_file):
    """Update footprint positions in PCB file"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    updates = 0

    # Track offsets for grouped components to avoid overlaps
    resistor_offset = [0, 0]
    cap_offset = [0, 0]
    tp_offset = [0, 0]
    diode_offset = [0, 0]

    # Find all footprints and update their positions
    # Pattern: (footprint "..." ... (at x y rotation) ... (property "Reference" "REF")

    def replace_position(match):
        nonlocal updates, resistor_offset, cap_offset, tp_offset, diode_offset

        full_block = match.group(0)

        # Extract reference designator
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', full_block)
        if not ref_match:
            return full_block

        ref = ref_match.group(1)

        # Skip power symbols
        if ref.startswith('#PWR'):
            return full_block

        # Determine new position
        zone = None
        rotation = 0
        offset = [0, 0]

        # Check for specific placement
        if ref in COMPONENT_PLACEMENT:
            zone, rotation = COMPONENT_PLACEMENT[ref]
        # Group similar components
        elif ref.startswith('R'):
            zone = 'MCU_CAPS'
            rotation = 90
            offset = resistor_offset.copy()
            resistor_offset[0] += 1.5
            if resistor_offset[0] > 15:
                resistor_offset[0] = 0
                resistor_offset[1] += 2
        elif ref.startswith('C'):
            zone = 'MCU_CAPS'
            rotation = 0
            offset = cap_offset.copy()
            cap_offset[0] += 1.5
            if cap_offset[0] > 15:
                cap_offset[0] = 0
                cap_offset[1] += 2
        elif ref.startswith('TP'):
            zone = 'MCU'
            rotation = 0
            offset = tp_offset.copy()
            tp_offset[0] += 3
            if tp_offset[0] > 18:
                tp_offset[0] = 0
                tp_offset[1] += 3
        elif ref.startswith('L'):
            zone = 'POWER_CAPS'
            rotation = 0
        elif ref.startswith('D') and ref not in COMPONENT_PLACEMENT:
            zone = 'MCU_CAPS'
            rotation = 90
            offset = diode_offset.copy()
            diode_offset[0] += 2
            if diode_offset[0] > 10:
                diode_offset[0] = 0
                diode_offset[1] += 2
        elif ref.startswith('Q'):
            zone = 'LOGIC'
            rotation = 90

        if zone:
            new_x, new_y, new_rot = get_component_position(ref, zone, rotation, offset)

            # Replace the (at x y rotation) line
            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {new_x} {new_y} {new_rot})',
                full_block,
                count=1
            )

            if new_block != full_block:
                updates += 1
                print(f"Repositioned {ref} to ({new_x:.1f}, {new_y:.1f}, {new_rot}°)")

            return new_block

        return full_block

    # Match entire footprint blocks
    pattern = r'\(footprint\s+[^\n]+\n(?:.*?\n)*?\t\)'
    new_content = re.sub(pattern, replace_position, content, flags=re.MULTILINE)

    # Write updated PCB
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\nRepositioned {updates} components")
    return updates

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("Repositioning components on PomeloCore PCB...")
    print("Layout based on reference board image\n")

    count = reposition_components(pcb_file)

    print(f"\nDone! Repositioned {count} components.")
    print("\nNext steps:")
    print("1. Open PCB in KiCad")
    print("2. Fine-tune component positions")
    print("3. Add board outline if needed")
    print("4. Route the board")
