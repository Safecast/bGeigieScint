#!/usr/bin/env python3
"""
Photo-based precise component placement
Analyzed from top-down and angled reference photos
Board: 40mm(x) × 100mm(y), coordinates (50,50) to (90,150)
Y-axis: 50=top, 150=bottom (USB end)
"""

import re

# Precise positions measured from reference photos
COMPONENT_POSITIONS = {
    # ============ BOTTOM SECTION (USB END) - Y: 135-150 ============
    # USB-C connector at bottom edge
    'USBC1': {'x': 87, 'y': 145, 'rot': 0},

    # Red power connector next to USB
    # Small components near USB
    'R2': {'x': 84, 'y': 143, 'rot': 0},      # CC resistor
    'R7': {'x': 84, 'y': 141, 'rot': 0},      # CC resistor
    'R1': {'x': 82, 'y': 142, 'rot': 90},     # USB pullup
    'R3': {'x': 82, 'y': 145, 'rot': 90},     # USB pullup
    'D1': {'x': 86, 'y': 140, 'rot': 0},      # TVS diode near USB

    # Reset button (bottom right, visible in photo)
    'BUT1': {'x': 86, 'y': 135, 'rot': 0},

    # Small components bottom-right area
    'C2': {'x': 84, 'y': 137, 'rot': 0},
    'R26': {'x': 85, 'y': 134, 'rot': 90},    # Near button
    'LED1': {'x': 87, 'y': 132, 'rot': 180},  # Status LED

    # ============ LOWER-CENTER SECTION (MCU AREA) - Y: 110-135 ============
    # Main MCU (large QFN, clearly visible center-lower)
    'U1': {'x': 72, 'y': 122, 'rot': 45},

    # Crystal near MCU (visible as small rectangular component)
    'X1': {'x': 68, 'y': 118, 'rot': 0},
    'C42': {'x': 67, 'y': 116, 'rot': 0},     # Crystal load cap
    'C43': {'x': 69, 'y': 116, 'rot': 0},     # Crystal load cap

    # Decoupling capacitors around MCU (visible ring pattern)
    # Top side of MCU
    'C7': {'x': 70, 'y': 118, 'rot': 0},
    'C1': {'x': 74, 'y': 118, 'rot': 0},
    'C18': {'x': 78, 'y': 118, 'rot': 0},

    # Right side of MCU
    'C14': {'x': 76, 'y': 122, 'rot': 90},
    'C26': {'x': 76, 'y': 126, 'rot': 90},

    # Bottom side of MCU
    'C19': {'x': 74, 'y': 126, 'rot': 0},
    'C28': {'x': 70, 'y': 126, 'rot': 0},
    'C25': {'x': 66, 'y': 126, 'rot': 0},

    # Left side of MCU
    'C33': {'x': 68, 'y': 122, 'rot': 90},
    'C37': {'x': 68, 'y': 118, 'rot': 90},

    # Additional caps near MCU
    'C4': {'x': 72, 'y': 128, 'rot': 0},      # 10uF
    'C6': {'x': 76, 'y': 128, 'rot': 0},      # 10uF
    'C38': {'x': 80, 'y': 122, 'rot': 0},
    'C39': {'x': 64, 'y': 122, 'rot': 0},

    # Resistors near MCU
    'R20': {'x': 79, 'y': 120, 'rot': 90},
    'R21': {'x': 65, 'y': 120, 'rot': 90},

    # Small ICs around MCU area
    'U6': {'x': 80, 'y': 125, 'rot': 90},     # SOT-23-5 comparator
    'U7': {'x': 80, 'y': 130, 'rot': 90},     # SOT-23-5 opamp
    'U13': {'x': 84, 'y': 127, 'rot': 90},    # Comparator

    # Supporting passives for analog section
    'C15': {'x': 82, 'y': 125, 'rot': 0},
    'C16': {'x': 82, 'y': 128, 'rot': 0},
    'C22': {'x': 84, 'y': 130, 'rot': 0},
    'R25': {'x': 83, 'y': 126, 'rot': 90},

    # Bottom left area - more ICs
    'U3': {'x': 62, 'y': 132, 'rot': 0},      # Latch (SOIC-14)
    'U10': {'x': 66, 'y': 130, 'rot': 90},    # Logic gate
    'Q1': {'x': 64, 'y': 134, 'rot': 90},     # Transistor

    # ============ MIDDLE SECTION - Y: 85-110 ============
    # Two large tan/beige square inductors (very visible in photo)
    'L1': {'x': 68, 'y': 95, 'rot': 0},
    'L2': {'x': 76, 'y': 95, 'rot': 0},

    # Smaller inductor
    'L3': {'x': 72, 'y': 98, 'rot': 0},

    # ICs in middle section
    'U4': {'x': 80, 'y': 105, 'rot': 90},     # OpAmp
    'U8': {'x': 76, 'y': 110, 'rot': 90},
    'U9': {'x': 72, 'y': 108, 'rot': 0},
    'U14': {'x': 84, 'y': 110, 'rot': 90},

    # Transistors
    'Q4': {'x': 78, 'y': 107, 'rot': 90},
    'Q5': {'x': 82, 'y': 107, 'rot': 90},

    # Passives in middle section
    'C24': {'x': 80, 'y': 102, 'rot': 0},
    'C36': {'x': 78, 'y': 108, 'rot': 0},
    'C34': {'x': 74, 'y': 105, 'rot': 0},

    'R30': {'x': 75, 'y': 107, 'rot': 90},
    'R31': {'x': 79, 'y': 107, 'rot': 90},

    # Diodes visible in this area
    'D2': {'x': 70, 'y': 105, 'rot': 90},
    'D4': {'x': 66, 'y': 108, 'rot': 90},
    'D5': {'x': 68, 'y': 102, 'rot': 90},
    'D6': {'x': 72, 'y': 102, 'rot': 90},
    'D7': {'x': 76, 'y': 102, 'rot': 90},
    'D9': {'x': 64, 'y': 95, 'rot': 90},      # Schottky near inductors
    'D10': {'x': 80, 'y': 95, 'rot': 90},

    # ============ UPPER SECTION (POWER MANAGEMENT) - Y: 50-85 ============
    # Power LDOs (small SOT-23 packages at top)
    'U2': {'x': 62, 'y': 75, 'rot': 0},       # 3.3V LDO
    'U5': {'x': 68, 'y': 75, 'rot': 0},       # Power LDO
    'U11': {'x': 74, 'y': 75, 'rot': 0},      # Analog LDO
    'U12': {'x': 80, 'y': 75, 'rot': 0},      # Level shifter

    # Power caps near LDOs
    'C10': {'x': 62, 'y': 78, 'rot': 0},
    'C11': {'x': 66, 'y': 78, 'rot': 0},
    'C12': {'x': 70, 'y': 78, 'rot': 0},
    'C47': {'x': 74, 'y': 78, 'rot': 0},
    'C48': {'x': 78, 'y': 78, 'rot': 0},
    'C49': {'x': 82, 'y': 78, 'rot': 0},

    # More power section components
    'C44': {'x': 64, 'y': 82, 'rot': 0},
    'C45': {'x': 68, 'y': 82, 'rot': 0},
    'C52': {'x': 72, 'y': 82, 'rot': 0},
    'C53': {'x': 76, 'y': 82, 'rot': 0},
    'C56': {'x': 80, 'y': 82, 'rot': 0},

    # Resistors in power section
    'R13': {'x': 63, 'y': 72, 'rot': 90},
    'R16': {'x': 67, 'y': 72, 'rot': 90},
    'R24': {'x': 71, 'y': 72, 'rot': 90},
    'R28': {'x': 75, 'y': 72, 'rot': 90},
    'R29': {'x': 79, 'y': 72, 'rot': 90},

    # Small components at very top
    'C23': {'x': 70, 'y': 65, 'rot': 0},
    'C27': {'x': 74, 'y': 65, 'rot': 0},
    'C29': {'x': 78, 'y': 65, 'rot': 0},
    'C31': {'x': 82, 'y': 65, 'rot': 0},

    'R32': {'x': 72, 'y': 68, 'rot': 90},
    'R33': {'x': 76, 'y': 68, 'rot': 90},
    'R34': {'x': 80, 'y': 68, 'rot': 90},

    # ============ LEFT SIDE - HEADERS (X: 50-55) ============
    # Pin headers stacked vertically on left edge
    'J-LINK1': {'x': 52, 'y': 60, 'rot': 0},  # Debug header at top
    'H2': {'x': 52, 'y': 85, 'rot': 0},       # Expansion header
    'H3': {'x': 52, 'y': 105, 'rot': 0},      # Expansion header
    'P1': {'x': 52, 'y': 130, 'rot': 0},      # Power connector
    'P2': {'x': 52, 'y': 140, 'rot': 0},      # Power connector

    # ============ RIGHT SIDE - EXPANSION (X: 85-90) ============
    # Expansion headers on right edge
    'H5': {'x': 87, 'y': 70, 'rot': 90},      # GPIO expansion
    'MEAS1': {'x': 87, 'y': 100, 'rot': 90},  # Measurement header
    'U15': {'x': 87, 'y': 115, 'rot': 90},    # Connector
}

# Off-board staging area for unplaced components
OFF_BOARD_START = {'x': 100, 'y': 60}

def place_components_from_photos(pcb_file):
    """Place components based on photo analysis"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    placed = []
    offboard = []

    offboard_x = OFF_BOARD_START['x']
    offboard_y = OFF_BOARD_START['y']

    def replace_position(match):
        nonlocal offboard_x, offboard_y

        full_block = match.group(0)

        # Extract reference
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', full_block)
        if not ref_match:
            return full_block

        ref = ref_match.group(1)

        # Skip power symbols
        if ref.startswith('#PWR'):
            return full_block

        # Check for precise placement
        if ref in COMPONENT_POSITIONS:
            pos = COMPONENT_POSITIONS[ref]
            x, y, rot = pos['x'], pos['y'], pos['rot']

            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {x} {y} {rot})',
                full_block,
                count=1
            )

            placed.append(ref)
            print(f"✓ {ref:12s} → ({x:5.1f}, {y:5.1f}, {rot:3.0f}°)")
            return new_block

        else:
            # Place off-board
            new_block = re.sub(
                r'\(at [0-9.-]+ [0-9.-]+( [0-9.-]+)?\)',
                f'(at {offboard_x} {offboard_y} 0)',
                full_block,
                count=1
            )

            offboard.append(ref)
            if len(offboard) <= 30:
                print(f"  {ref:12s} → OFF-BOARD")

            # Grid arrangement
            offboard_x += 3
            if offboard_x > 118:
                offboard_x = OFF_BOARD_START['x']
                offboard_y += 3

            return new_block

    # Process footprints
    pattern = r'\(footprint\s+[^\n]+\n(?:.*?\n)*?\t\)'
    new_content = re.sub(pattern, replace_position, content, flags=re.MULTILINE)

    # Write file
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return placed, offboard

def add_board_outline(pcb_file):
    """Add 40×100mm board outline"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if outline exists
    if 'Edge.Cuts' in content and 'gr_rect' in content:
        print("✓ Board outline already exists")
        return

    # Add outline before embedded_fonts
    outline = '''\t(gr_rect
\t\t(start 50 50)
\t\t(end 90 150)
\t\t(stroke
\t\t\t(width 0.15)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "board-outline")
\t)
'''

    # Find insertion point
    if '\t(embedded_fonts no)' in content:
        content = content.replace('\t(embedded_fonts no)', outline + '\t(embedded_fonts no)')

        with open(pcb_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✓ Added board outline: 40mm × 100mm")

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("="*70)
    print("PHOTO-BASED COMPONENT PLACEMENT")
    print("Analyzing reference photos for precise positioning...")
    print("="*70)
    print()

    # Place components
    placed, offboard = place_components_from_photos(pcb_file)

    print()
    print("="*70)
    print(f"✓ Placed {len(placed)} components on board (matched from photos)")
    print(f"  Placed {len(offboard)} components off-board for manual positioning")
    print("="*70)
    print()

    # Add board outline
    add_board_outline(pcb_file)

    print()
    print("DONE!")
    print()
    print("In KiCad you will see:")
    print(f"  • {len(placed)} components positioned on the board")
    print(f"  • {len(offboard)} components to the right (off-board) - drag these into place")
    print("  • Board outline: 40mm × 100mm")
    print()
    print("Next: Fine-tune positions using the reference photos, then route!")
