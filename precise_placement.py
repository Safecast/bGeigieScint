#!/usr/bin/env python3
"""
Precise component placement based on high-quality reference photos
Focus on exact resistor/capacitor placement matching the reference board
Components that can't be placed accurately go off-board (100-120mm area)
"""

import re
import uuid

# Board area: (50, 50) to (90, 150) = 40mm x 100mm
# Off-board staging area: (100, 50) to (120, 150)

# Detailed placement based on reference photos
# All positions in mm, rotations in degrees

PRECISE_PLACEMENT = {
    # ========== RIGHT EDGE - USB SECTION ==========
    # USB-C connector at right edge, bottom area
    'USBC1': {'x': 88.5, 'y': 135, 'rot': 0, 'layer': 'F'},

    # Components near USB (visible in photo)
    'D1': {'x': 85, 'y': 132, 'rot': 90, 'layer': 'F'},  # TVS diode near USB
    'R2': {'x': 83, 'y': 137, 'rot': 90, 'layer': 'F'},  # CC resistor
    'R7': {'x': 83, 'y': 133, 'rot': 90, 'layer': 'F'},  # CC resistor

    # Red power connector next to USB
    # (Assuming this is a power input connector)

    # ========== CENTER-RIGHT - MCU SECTION ==========
    # Main MCU (large QFN) - clearly visible in center-right
    'U1': {'x': 72, 'y': 115, 'rot': 45, 'layer': 'F'},  # ATSAML21 MCU

    # Crystal and caps very close to MCU (visible in photo)
    'X1': {'x': 68, 'y': 110, 'rot': 0, 'layer': 'F'},  # 32.768kHz crystal
    'C42': {'x': 67, 'y': 107, 'rot': 0, 'layer': 'F'},  # Crystal cap
    'C43': {'x': 69, 'y': 107, 'rot': 0, 'layer': 'F'},  # Crystal cap

    # Decoupling caps around MCU (ring pattern visible)
    'C7': {'x': 70, 'y': 120, 'rot': 0, 'layer': 'F'},   # Near MCU
    'C1': {'x': 74, 'y': 120, 'rot': 0, 'layer': 'F'},
    'C18': {'x': 70, 'y': 110, 'rot': 0, 'layer': 'F'},
    'C26': {'x': 74, 'y': 110, 'rot': 0, 'layer': 'F'},
    'C14': {'x': 76, 'y': 115, 'rot': 90, 'layer': 'F'},
    'C28': {'x': 68, 'y': 115, 'rot': 90, 'layer': 'F'},

    # More caps near MCU
    'C19': {'x': 72, 'y': 122, 'rot': 0, 'layer': 'F'},
    'C25': {'x': 76, 'y': 118, 'rot': 0, 'layer': 'F'},
    'C33': {'x': 68, 'y': 118, 'rot': 0, 'layer': 'F'},
    'C37': {'x': 74, 'y': 108, 'rot': 0, 'layer': 'F'},
    'C38': {'x': 78, 'y': 115, 'rot': 90, 'layer': 'F'},
    'C39': {'x': 66, 'y': 115, 'rot': 90, 'layer': 'F'},

    # Resistors near MCU
    'R20': {'x': 77, 'y': 112, 'rot': 90, 'layer': 'F'},
    'R26': {'x': 87, 'y': 57, 'rot': 0, 'layer': 'F'},  # LED resistor

    # ========== TOP-CENTER - DEBUG SECTION ==========
    # J-LINK debug header at top
    'J-LINK1': {'x': 70, 'y': 55, 'rot': 0, 'layer': 'F'},

    # Reset button (visible at bottom-right in photo)
    'BUT1': {'x': 86, 'y': 140, 'rot': 0, 'layer': 'F'},

    # ========== LEFT SIDE - HEADERS ==========
    # Pin headers stacked vertically on left side
    'H2': {'x': 53, 'y': 80, 'rot': 90, 'layer': 'F'},
    'H3': {'x': 53, 'y': 95, 'rot': 90, 'layer': 'F'},
    'H5': {'x': 87, 'y': 70, 'rot': 90, 'layer': 'F'},  # Right side expansion

    # Power input connectors (left side, bottom)
    'P1': {'x': 53, 'y': 125, 'rot': 90, 'layer': 'F'},
    'P2': {'x': 53, 'y': 135, 'rot': 90, 'layer': 'F'},

    # ========== TOP AREA - POWER MANAGEMENT ==========
    # Visible inductors/power components at top-left
    'L1': {'x': 58, 'y': 68, 'rot': 0, 'layer': 'F'},
    'L2': {'x': 62, 'y': 68, 'rot': 0, 'layer': 'F'},
    'L3': {'x': 66, 'y': 68, 'rot': 0, 'layer': 'F'},

    # Power LDOs (small SOT-23 packages visible)
    'U2': {'x': 60, 'y': 75, 'rot': 0, 'layer': 'F'},   # 3.3V LDO
    'U5': {'x': 64, 'y': 75, 'rot': 0, 'layer': 'F'},
    'U11': {'x': 68, 'y': 75, 'rot': 0, 'layer': 'F'},  # Analog LDO

    # Power caps near LDOs
    'C4': {'x': 60, 'y': 78, 'rot': 0, 'layer': 'F'},   # 10uF
    'C6': {'x': 64, 'y': 78, 'rot': 0, 'layer': 'F'},   # 10uF

    # ========== CENTER - ANALOG SECTION ==========
    # Analog ICs (SOT-23-5 packages visible)
    'U4': {'x': 78, 'y': 100, 'rot': 90, 'layer': 'F'},  # LMV793
    'U6': {'x': 80, 'y': 115, 'rot': 90, 'layer': 'F'},  # TLV3201
    'U7': {'x': 78, 'y': 108, 'rot': 90, 'layer': 'F'},  # OPA357
    'U13': {'x': 82, 'y': 108, 'rot': 90, 'layer': 'F'}, # TLV7031

    # Passives around analog section
    'C15': {'x': 76, 'y': 102, 'rot': 0, 'layer': 'F'},
    'C16': {'x': 80, 'y': 102, 'rot': 0, 'layer': 'F'},
    'C22': {'x': 76, 'y': 106, 'rot': 0, 'layer': 'F'},
    'C24': {'x': 80, 'y': 106, 'rot': 0, 'layer': 'F'},

    'R21': {'x': 77, 'y': 104, 'rot': 90, 'layer': 'F'},
    'R25': {'x': 81, 'y': 104, 'rot': 90, 'layer': 'F'},

    # ========== BOTTOM-CENTER - LOGIC SECTION ==========
    # Logic ICs visible in bottom area
    'U3': {'x': 68, 'y': 130, 'rot': 0, 'layer': 'F'},   # MC14043 latch
    'U8': {'x': 74, 'y': 130, 'rot': 90, 'layer': 'F'},
    'U10': {'x': 78, 'y': 130, 'rot': 90, 'layer': 'F'},
    'U14': {'x': 82, 'y': 130, 'rot': 90, 'layer': 'F'},

    # Transistors
    'Q1': {'x': 70, 'y': 125, 'rot': 90, 'layer': 'F'},
    'Q4': {'x': 76, 'y': 125, 'rot': 90, 'layer': 'F'},
    'Q5': {'x': 80, 'y': 125, 'rot': 90, 'layer': 'F'},

    # ========== RIGHT SIDE - EXPANSION ==========
    'MEAS1': {'x': 87, 'y': 130, 'rot': 90, 'layer': 'F'},
    'U15': {'x': 87, 'y': 100, 'rot': 90, 'layer': 'F'},

    # LED
    'LED1': {'x': 87, 'y': 57, 'rot': 180, 'layer': 'F'},

    # ========== DIODES ==========
    'D2': {'x': 62, 'y': 105, 'rot': 90, 'layer': 'F'},
    'D4': {'x': 64, 'y': 105, 'rot': 90, 'layer': 'F'},
    'D5': {'x': 66, 'y': 105, 'rot': 90, 'layer': 'F'},
    'D6': {'x': 68, 'y': 105, 'rot': 90, 'layer': 'F'},
    'D7': {'x': 70, 'y': 105, 'rot': 90, 'layer': 'F'},
    'D9': {'x': 60, 'y': 72, 'rot': 90, 'layer': 'F'},
    'D10': {'x': 64, 'y': 72, 'rot': 90, 'layer': 'F'},
}

# Off-board staging area for components not precisely identified
OFF_BOARD_START = {'x': 100, 'y': 60}

def place_all_components(pcb_file):
    """Place components based on reference photos"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    placed_count = 0
    offboard_count = 0
    offboard_x = OFF_BOARD_START['x']
    offboard_y = OFF_BOARD_START['y']

    def replace_footprint_position(match):
        nonlocal placed_count, offboard_count, offboard_x, offboard_y

        full_block = match.group(0)

        # Extract reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', full_block)
        if not ref_match:
            return full_block

        ref = ref_match.group(1)

        # Skip power symbols
        if ref.startswith('#PWR'):
            return full_block

        # Check if we have precise placement
        if ref in PRECISE_PLACEMENT:
            pos = PRECISE_PLACEMENT[ref]
            x, y, rot = pos['x'], pos['y'], pos['rot']

            # Update position
            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {x} {y} {rot})',
                full_block,
                count=1
            )

            placed_count += 1
            print(f"✓ {ref:10s} -> ({x:5.1f}, {y:5.1f}, {rot:3.0f}°)")
            return new_block

        else:
            # Place off-board in staging area
            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {offboard_x} {offboard_y} 0)',
                full_block,
                count=1
            )

            # Arrange in grid
            offboard_x += 3
            if offboard_x > 118:
                offboard_x = OFF_BOARD_START['x']
                offboard_y += 3

            offboard_count += 1
            if offboard_count <= 20:  # Only print first 20
                print(f"○ {ref:10s} -> OFF-BOARD ({offboard_x-3:.1f}, {offboard_y:.1f})")

            return new_block

    # Process all footprints
    pattern = r'\(footprint\s+[^\n]+\n(?:.*?\n)*?\t\)'
    new_content = re.sub(pattern, replace_footprint_position, content, flags=re.MULTILINE)

    # Write updated file
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n{'='*60}")
    print(f"Placed {placed_count} components precisely")
    print(f"Placed {offboard_count} components off-board for manual positioning")
    print(f"{'='*60}")

    return placed_count, offboard_count

def add_board_outline(pcb_file):
    """Add board outline and basic configuration"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find insertion point
    embedded_fonts_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '(embedded_fonts no)' and lines[i].startswith('\t('):
            if len(lines) - i < 10:
                embedded_fonts_idx = i
                break

    if embedded_fonts_idx == -1:
        print("Warning: Could not add board outline")
        return

    # Board outline
    board_outline = '''\t(gr_rect
\t\t(start 50 50)
\t\t(end 90 150)
\t\t(stroke
\t\t\t(width 0.15)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "board-outline-rect")
\t)
'''

    lines.insert(embedded_fonts_idx, board_outline)

    # Write back
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("✓ Added board outline: 40mm × 100mm")

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("="*60)
    print("PRECISE COMPONENT PLACEMENT")
    print("Based on high-quality reference photos")
    print("="*60)
    print()

    # Place components
    placed, offboard = place_all_components(pcb_file)

    print()

    # Add board outline
    add_board_outline(pcb_file)

    print()
    print("NEXT STEPS:")
    print("1. Open PCB in KiCad")
    print("2. Precisely placed components are on the board")
    print(f"3. {offboard} components are off-board (right side) - drag them into position")
    print("4. Use reference photos to fine-tune positions")
    print("5. Route the board")
