#!/usr/bin/env python3
"""
Place components on PomeloCore PCB based on reference board layout
Board dimensions: 40mm x 100mm
Origin offset: (50, 50) so board is from (50,50) to (90,150)
"""

import re
import uuid

# Component placement zones (in mm, relative to board origin at 50,50)
ZONES = {
    # Left side (0-30mm) - Power and USB
    'USB': {'x': 52, 'y': 100, 'desc': 'USB connector and protection'},
    'POWER_LDO': {'x': 62, 'y': 85, 'desc': 'Main power regulators'},
    'POWER_CAPS': {'x': 62, 'y': 95, 'desc': 'Power supply capacitors'},

    # Center (30-60mm) - MCU and core
    'MCU': {'x': 70, 'y': 100, 'desc': 'Main microcontroller'},
    'MCU_CRYSTAL': {'x': 70, 'y': 90, 'desc': 'MCU crystal'},
    'MCU_CAPS': {'x': 70, 'y': 105, 'desc': 'MCU decoupling caps'},
    'DEBUG': {'x': 65, 'y': 55, 'desc': 'Debug header'},

    # Right side (60-100mm) - Analog and interfaces
    'ANALOG': {'x': 78, 'y': 100, 'desc': 'Analog frontend'},
    'LOGIC': {'x': 78, 'y': 85, 'desc': 'Logic circuits'},
    'EXPANSION': {'x': 85, 'y': 100, 'desc': 'Expansion headers'},
    'LED': {'x': 87, 'y': 55, 'desc': 'Status LED'},
}

# Component to zone mapping based on reference and function
COMPONENT_PLACEMENT = {
    # Power section
    'USBC1': ('USB', 0),
    'D1': ('USB', 90),  # TVS diode near USB
    'R1': ('USB', 0),   # USB pullup
    'R3': ('USB', 0),   # USB pullup
    'U2': ('POWER_LDO', 90),  # 3.3V LDO
    'C6': ('POWER_CAPS', 0),  # 10uF bulk
    'P1': ('POWER_LDO', 0),   # Power headers
    'P2': ('POWER_LDO', 0),

    # MCU section
    'U1': ('MCU', 45),  # ATSAML21 - rotated 45° for optimal routing
    'X1': ('MCU_CRYSTAL', 0),  # Crystal next to MCU
    'J-LINK1': ('DEBUG', 0),   # Debug header
    'BUT1': ('MCU', 0),  # Reset button

    # Analog section
    'U7': ('ANALOG', 90),  # OPA357 opamp
    'U6': ('ANALOG', 90),  # TLV3201 comparator
    'U11': ('POWER_LDO', 90),  # LT3014 LDO for analog

    # Logic section
    'U3': ('LOGIC', 90),  # MC14043 latch
    'U8': ('LOGIC', 90),
    'U9': ('ANALOG', 90),
    'U10': ('LOGIC', 0),
    'U13': ('ANALOG', 90),
    'U14': ('LOGIC', 90),
    'U4': ('ANALOG', 90),  # LMV793 opamp
    'U5': ('POWER_LDO', 90),

    # Interfaces
    'H2': ('EXPANSION', 90),  # Expansion headers
    'H3': ('EXPANSION', 90),
    'H5': ('EXPANSION', 90),
    'MEAS1': ('EXPANSION', 90),
    'U15': ('EXPANSION', 90),

    # LED
    'LED1': ('LED', 180),
}

def read_schematic_components(sch_file):
    """Extract components with their footprints from schematic"""
    with open(sch_file, 'r', encoding='utf-8') as f:
        content = f.read()

    components = {}

    # Find all symbol instances
    pattern = r'\(symbol[^)]*?\(lib_id[^)]*?\).*?\(property "Reference" "([^"]+)".*?\(property "Value" "([^"]+)".*?\(property "Footprint" "([^"]+)"'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        ref = match.group(1)
        value = match.group(2)
        footprint = match.group(3)

        if not ref.startswith('#PWR') and footprint:
            components[ref] = {
                'value': value,
                'footprint': footprint
            }

    print(f"Found {len(components)} components with footprints")
    return components

def get_component_position(ref, zone_name, rotation, offset=(0, 0)):
    """Calculate component position based on zone and offset"""
    if zone_name not in ZONES:
        # Default to center if zone not found
        zone_name = 'MCU'

    zone = ZONES[zone_name]
    x = zone['x'] + offset[0]
    y = zone['y'] + offset[1]

    return (x, y, rotation)

def generate_footprint_element(ref, value, footprint, position):
    """Generate KiCad footprint element"""
    x, y, rotation = position
    uid = str(uuid.uuid4())

    fp = f'''	(footprint "{footprint}"
		(layer "F.Cu")
		(uuid "{uid}")
		(at {x} {y} {rotation})
		(property "Reference" "{ref}"
			(at 0 -2.5 {rotation})
			(layer "F.SilkS")
			(uuid "{uuid.uuid4()}")
			(effects
				(font
					(size 0.8 0.8)
					(thickness 0.15)
				)
			)
		)
		(property "Value" "{value}"
			(at 0 2.5 {rotation})
			(layer "F.Fab")
			(uuid "{uuid.uuid4()}")
			(effects
				(font
					(size 0.8 0.8)
					(thickness 0.15)
				)
			)
		)
		(property "Footprint" "{footprint}"
			(at 0 0 {rotation})
			(layer "F.Fab")
			(hide yes)
			(uuid "{uuid.uuid4()}")
			(effects
				(font
					(size 1.27 1.27)
					(thickness 0.15)
				)
			)
		)
		(path "/00000000-0000-0000-0000-000000000000")
	)
'''
    return fp

def place_components_on_pcb(sch_file, pcb_file):
    """Main function to place components"""

    # Read components from schematic
    components = read_schematic_components(sch_file)

    # Read current PCB file
    with open(pcb_file, 'r', encoding='utf-8') as f:
        pcb_content = f.read()

    # Generate footprint placements
    footprints = []
    placed_count = 0

    # Track offset for similar components to avoid overlaps
    resistor_offset = [0, 0]
    cap_offset = [0, 0]
    tp_offset = [0, 0]

    for ref, data in sorted(components.items()):
        value = data['value']
        footprint = data['footprint']

        # Determine placement
        zone = 'MCU'  # default
        rotation = 0
        offset = [0, 0]

        # Check if component has specific placement
        if ref in COMPONENT_PLACEMENT:
            zone, rotation = COMPONENT_PLACEMENT[ref]
        # Group similar components
        elif ref.startswith('R'):
            zone = 'MCU_CAPS'
            rotation = 90
            offset = resistor_offset.copy()
            resistor_offset[0] += 2
            if resistor_offset[0] > 10:
                resistor_offset[0] = 0
                resistor_offset[1] += 2
        elif ref.startswith('C'):
            zone = 'MCU_CAPS'
            offset = cap_offset.copy()
            cap_offset[0] += 2
            if cap_offset[0] > 10:
                cap_offset[0] = 0
                cap_offset[1] += 2
        elif ref.startswith('TP'):
            zone = 'MCU'
            offset = tp_offset.copy()
            tp_offset[0] += 3
            if tp_offset[0] > 15:
                tp_offset[0] = 0
                tp_offset[1] += 3
        elif ref.startswith('L'):
            zone = 'POWER_CAPS'
            rotation = 90
        elif ref.startswith('D'):
            zone = 'MCU_CAPS'
        elif ref.startswith('Q'):
            zone = 'LOGIC'
            rotation = 90

        position = get_component_position(ref, zone, rotation, offset)
        footprint_element = generate_footprint_element(ref, value, footprint, position)
        footprints.append(footprint_element)
        placed_count += 1

        print(f"Placed {ref} ({value}) at zone {zone}: {position}")

    # Insert footprints before the closing parenthesis
    # Find the board outline element and insert after it
    insertion_point = pcb_content.rfind(')')

    new_pcb = pcb_content[:insertion_point] + '\n'.join(footprints) + pcb_content[insertion_point:]

    # Write updated PCB
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_pcb)

    print(f"\nPlaced {placed_count} components on PCB")
    return placed_count

if __name__ == '__main__':
    sch_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_sch"
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("Placing components on PomeloCore PCB...")
    print("Board: 40mm x 100mm")
    print("Layout based on reference board\n")

    count = place_components_on_pcb(sch_file, pcb_file)

    print(f"\nDone! Placed {count} components.")
    print("\nNext steps:")
    print("1. Open PCB in KiCad")
    print("2. Adjust component positions as needed")
    print("3. Route the board")
