#!/usr/bin/env python3
"""
Add board outline and 4-layer configuration to PCB
"""

import re

def add_board_config(pcb_file):
    """Add board outline and layer configuration"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if board outline already exists
    if 'gr_rect' in content and 'Edge.Cuts' in content:
        print("Board outline already exists")
    else:
        # Add board outline before embedded_fonts
        board_outline = '''	(gr_rect
		(start 50 50)
		(end 90 150)
		(stroke
			(width 0.15)
			(type default)
		)
		(layer "Edge.Cuts")
		(uuid "00000000-0000-0000-0000-000000000001")
	)
'''
        content = content.replace('(embedded_fonts no)', board_outline + '\t(embedded_fonts no)')
        print("Added board outline: 40mm x 100mm")

    # Update layers to 4-layer if not already
    if 'In1.Cu' not in content:
        # Replace 2-layer with 4-layer
        old_layers = '''	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)'''

        new_layers = '''	(layers
		(0 "F.Cu" signal)
		(1 "In1.Cu" power "GND")
		(2 "In2.Cu" power "VCC")
		(3 "B.Cu" signal)'''

        content = content.replace(old_layers, new_layers)

        # Update mask layer numbers
        content = content.replace('(1 "F.Mask" user)', '(4 "F.Mask" user)')
        content = content.replace('(3 "B.Mask" user)', '(6 "B.Mask" user)')

        print("Upgraded to 4-layer stackup")

    # Add stackup configuration if not present
    if 'stackup' not in content:
        stackup_config = '''		(stackup
			(layer "F.SilkS"
				(type "Top Silk Screen")
			)
			(layer "F.Paste"
				(type "Top Solder Paste")
			)
			(layer "F.Mask"
				(type "Top Solder Mask")
				(thickness 0.01)
			)
			(layer "F.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "dielectric 1"
				(type "core")
				(thickness 0.48)
				(material "FR4")
				(epsilon_r 4.5)
				(loss_tangent 0.02)
			)
			(layer "In1.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "dielectric 2"
				(type "prepreg")
				(thickness 0.48)
				(material "FR4")
				(epsilon_r 4.5)
				(loss_tangent 0.02)
			)
			(layer "In2.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "dielectric 3"
				(type "core")
				(thickness 0.48)
				(material "FR4")
				(epsilon_r 4.5)
				(loss_tangent 0.02)
			)
			(layer "B.Cu"
				(type "copper")
				(thickness 0.035)
			)
			(layer "B.Mask"
				(type "Bottom Solder Mask")
				(thickness 0.01)
			)
			(layer "B.Paste"
				(type "Bottom Solder Paste")
			)
			(layer "B.SilkS"
				(type "Bottom Silk Screen")
			)
			(copper_finish "None")
			(dielectric_constraints no)
		)
'''
        # Insert after (setup
        content = content.replace('(setup\n', f'(setup\n{stackup_config}')
        print("Added 4-layer stackup configuration")

    # Write updated content
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\nBoard configuration complete!")

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"
    add_board_config(pcb_file)
