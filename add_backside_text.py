#!/usr/bin/env python3
"""
Add silkscreen text to the backside of PomeloCore PCB
Based on reference board image
"""

import uuid

def add_silkscreen_text(pcb_file):
    """Add text elements to back silkscreen"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Text elements to add on back silkscreen
    # Format: (text, x, y, size, rotation, justification)
    back_text_elements = [
        # Main branding
        ("Pomelo", 70, 100, 8.0, 0, "center"),

        # Section labels
        ("Pomelo Zest", 55, 60, 1.2, 0, "left"),
        ("interface &", 55, 62, 1.0, 0, "left"),
        ("UART", 55, 64, 1.0, 0, "left"),

        ("Expansion GPIO", 75, 55, 1.2, 0, "center"),

        ("Temp", 86, 56, 0.8, 0, "left"),
        ("Sensor", 86, 58, 0.8, 0, "left"),

        # Voltage check points
        ("Vboost", 72, 85, 0.8, 0, "left"),
        ("check", 72, 87, 0.8, 0, "left"),

        ("Vbias", 80, 85, 0.8, 0, "left"),
        ("check", 80, 87, 0.8, 0, "left"),

        # SiPM section
        ("SiPM bias", 83, 105, 1.0, 0, "left"),
        ("and signal", 83, 107, 1.0, 0, "left"),

        # Debug section
        ("Analog debug", 70, 120, 1.0, 0, "center"),

        # Power input
        ("Ext. power", 54, 75, 0.8, 0, "left"),
        ("4.5V to 6V", 54, 77, 0.8, 0, "left"),

        # Current measurement
        ("Out Use track", 54, 125, 0.7, 0, "left"),
        ("for current", 54, 127, 0.7, 0, "left"),
        ("measurement", 54, 129, 0.7, 0, "left"),
    ]

    # Generate gr_text elements for back silkscreen
    text_elements = []

    for text, x, y, size, rotation, justify in back_text_elements:
        uid = str(uuid.uuid4())

        justify_effect = ""
        if justify == "left":
            justify_effect = "\n\t\t\t(justify left)"
        elif justify == "right":
            justify_effect = "\n\t\t\t(justify right)"
        # center is default, no justify needed

        thickness = size * 0.15  # Standard thickness ratio

        text_element = f'''\t(gr_text "{text}"
\t\t(at {x} {y} {rotation})
\t\t(layer "B.SilkS")
\t\t(uuid "{uid}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t\t(thickness {thickness:.2f})
\t\t\t)
\t\t\t(justify mirror){justify_effect}
\t\t)
\t)
'''
        text_elements.append(text_element)
        print(f"Added text: '{text}' at ({x}, {y})")

    # Insert text elements before (embedded_fonts no)
    insertion_point = content.rfind('\t(embedded_fonts no)')

    if insertion_point == -1:
        print("Error: Could not find insertion point")
        return False

    new_content = (
        content[:insertion_point] +
        '\n'.join(text_elements) +
        content[insertion_point:]
    )

    # Write updated content
    with open(pcb_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\nAdded {len(text_elements)} text elements to back silkscreen")
    return True

def move_components_to_back(pcb_file, component_refs):
    """Move specified components to back layer"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    import re

    updates = 0

    for ref in component_refs:
        # Find the footprint block for this component
        # Look for the footprint that contains this reference
        pattern = rf'(\(footprint\s+[^\n]+\n(?:.*?\n)*?\(property "Reference" "{ref}"(?:.*?\n)*?\t\))'

        def replace_layer(match):
            nonlocal updates
            block = match.group(0)

            # Replace layer "F.Cu" with "B.Cu"
            if '(layer "F.Cu")' in block:
                new_block = block.replace('(layer "F.Cu")', '(layer "B.Cu")')
                # Also update any F.SilkS to B.SilkS, F.Fab to B.Fab, etc.
                new_block = new_block.replace('layer "F.SilkS"', 'layer "B.SilkS"')
                new_block = new_block.replace('layer "F.Fab"', 'layer "B.Fab"')
                new_block = new_block.replace('layer "F.Mask"', 'layer "B.Mask"')
                new_block = new_block.replace('layer "F.Paste"', 'layer "B.Paste"')
                new_block = new_block.replace('layer "F.CrtYd"', 'layer "B.CrtYd"')

                updates += 1
                print(f"Moved {ref} to back layer")
                return new_block

            return block

        content = re.sub(pattern, replace_layer, content, flags=re.MULTILINE)

    if updates > 0:
        # Write updated content
        with open(pcb_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nMoved {updates} components to back layer")

    return updates

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("Adding backside text to PomeloCore PCB...\n")

    # Add text to back silkscreen
    success = add_silkscreen_text(pcb_file)

    if success:
        print("\n" + "="*50)
        print("Backside text added successfully!")
        print("="*50)

        # Optionally move some components to back
        # Based on the image, these might be on the back:
        # - Some test points
        # - Some headers
        print("\nNote: If you want to move specific components to the back layer,")
        print("you can edit this script and add them to the component list.")

        # Example of moving components to back (uncomment if needed):
        # components_on_back = ['H2', 'H3', 'H5']  # Example header components
        # move_components_to_back(pcb_file, components_on_back)
    else:
        print("\nError adding backside text")
