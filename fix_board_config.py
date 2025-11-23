#!/usr/bin/env python3
"""
Add board outline and 4-layer configuration to PCB - FIXED VERSION
Correctly places board outline at end of file, not inside footprints
"""

import re

def fix_board_config(pcb_file):
    """Add board outline and layer configuration"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the last footprint closing
    last_footprint_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == ')' and i > 100:  # Find last closing paren that's not the final one
            # Check if this is after a footprint block
            if i < len(lines) - 5:  # Not the very end
                last_footprint_idx = i
                break

    # Find the final (embedded_fonts no) line (with single tab indentation)
    embedded_fonts_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '(embedded_fonts no)' and lines[i].startswith('\t('):
            # Check it's near the end (last 10 lines)
            if len(lines) - i < 10:
                embedded_fonts_idx = i
                break

    if embedded_fonts_idx == -1:
        print("Error: Could not find (embedded_fonts no) at file level")
        return False

    # Add board outline before embedded_fonts
    board_outline = '''\t(gr_rect
\t\t(start 50 50)
\t\t(end 90 150)
\t\t(stroke
\t\t\t(width 0.15)
\t\t\t(type default)
\t\t)
\t\t(layer "Edge.Cuts")
\t\t(uuid "00000000-0000-0000-0000-000000000001")
\t)
'''

    lines.insert(embedded_fonts_idx, board_outline)
    print("Added board outline: 40mm x 100mm")

    # Now update layers to 4-layer
    content = ''.join(lines)

    if 'In1.Cu' not in content:
        # Replace 2-layer with 4-layer
        old_layers = '''\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)'''

        new_layers = '''\t(layers
\t\t(0 "F.Cu" signal)
\t\t(1 "In1.Cu" power "GND")
\t\t(2 "In2.Cu" power "VCC")
\t\t(3 "B.Cu" signal)'''

        content = content.replace(old_layers, new_layers)

        # Update mask layer numbers for 4-layer
        content = re.sub(r'\(1 "F\.Mask"', '(4 "F.Mask"', content)
        content = re.sub(r'\(3 "B\.Mask"', '(6 "B.Mask"', content)

        print("Upgraded to 4-layer stackup")

    # Add stackup configuration if not present
    if 'stackup' not in content:
        stackup_config = '''\t\t(stackup
\t\t\t(layer "F.SilkS"
\t\t\t\t(type "Top Silk Screen")
\t\t\t)
\t\t\t(layer "F.Paste"
\t\t\t\t(type "Top Solder Paste")
\t\t\t)
\t\t\t(layer "F.Mask"
\t\t\t\t(type "Top Solder Mask")
\t\t\t\t(thickness 0.01)
\t\t\t)
\t\t\t(layer "F.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 1"
\t\t\t\t(type "core")
\t\t\t\t(thickness 0.48)
\t\t\t\t(material "FR4")
\t\t\t\t(epsilon_r 4.5)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In1.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 2"
\t\t\t\t(type "prepreg")
\t\t\t\t(thickness 0.48)
\t\t\t\t(material "FR4")
\t\t\t\t(epsilon_r 4.5)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In2.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 3"
\t\t\t\t(type "core")
\t\t\t\t(thickness 0.48)
\t\t\t\t(material "FR4")
\t\t\t\t(epsilon_r 4.5)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "B.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "B.Mask"
\t\t\t\t(type "Bottom Solder Mask")
\t\t\t\t(thickness 0.01)
\t\t\t)
\t\t\t(layer "B.Paste"
\t\t\t\t(type "Bottom Solder Paste")
\t\t\t)
\t\t\t(layer "B.SilkS"
\t\t\t\t(type "Bottom Silk Screen")
\t\t\t)
\t\t\t(copper_finish "None")
\t\t\t(dielectric_constraints no)
\t\t)
'''
        # Insert after (setup line
        content = re.sub(r'(\(setup)\n', r'\1\n' + stackup_config, content)
        print("Added 4-layer stackup configuration")

    # Write updated content
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\nBoard configuration complete!")
    return True

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"
    success = fix_board_config(pcb_file)

    if success:
        print("\nYou can now open the PCB in KiCad!")
    else:
        print("\nThere was an error. Please check the file manually.")
