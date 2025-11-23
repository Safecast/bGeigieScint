#!/usr/bin/env python3
"""
Add silkscreen text to the front side of PomeloCore PCB
Based on top-side reference board image
"""

import uuid

def add_frontside_silkscreen(pcb_file):
    """Add text elements to front silkscreen"""

    with open(pcb_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Text elements for front silkscreen
    # Format: (text, x, y, size, rotation, justification)
    front_text_elements = [
        # Main branding/version
        ("Pomelo", 70, 100, 6.0, 0, "center"),
        ("Physics", 70, 106, 2.0, 0, "center"),
        ("v1.0", 70, 109, 1.2, 0, "center"),

        # MCU label (near U1)
        ("M. Cuciuc", 68, 94, 0.8, 0, "center"),

        # Connector labels - Left side
        ("Pomelo", 52, 58, 0.8, 90, "left"),
        ("Physics", 52, 62, 0.8, 90, "left"),

        # GPIO expansion labels
        ("GPIO", 85, 70, 1.0, 0, "center"),

        # USB label (near USBC1)
        ("USB", 88, 98, 0.8, 0, "center"),

        # Power labels
        ("+3V3", 62, 88, 0.6, 0, "left"),
        ("GND", 62, 90, 0.6, 0, "left"),

        # Test point labels (examples)
        ("RESET", 68, 86, 0.5, 0, "left"),
        ("SWDIO", 72, 56, 0.5, 0, "left"),
        ("SWCLK", 74, 56, 0.5, 0, "left"),

        # Component reference labels
        ("J-LINK", 70, 52, 0.7, 0, "center"),

        # Debug/measurement labels
        ("DEBUG", 70, 118, 0.8, 0, "center"),

        # SiPM section label
        ("SiPM", 82, 110, 0.8, 0, "left"),

        # Voltage labels near test points
        ("VCC", 76, 88, 0.5, 0, "left"),
        ("Vbias", 80, 92, 0.5, 0, "left"),
        ("Vload", 78, 110, 0.5, 0, "left"),

        # Crystal label
        ("32.768kHz", 65, 88, 0.4, 0, "left"),

        # Button label
        ("RST", 59, 91, 0.6, 0, "center"),

        # LED label
        ("PWR", 87, 56, 0.5, 0, "left"),
    ]

    # Generate gr_text elements for front silkscreen
    text_elements = []

    for text, x, y, size, rotation, justify in front_text_elements:
        uid = str(uuid.uuid4())

        justify_effect = ""
        if justify == "left":
            justify_effect = "\n\t\t\t(justify left)"
        elif justify == "right":
            justify_effect = "\n\t\t\t(justify right)"

        thickness = size * 0.15  # Standard thickness ratio

        text_element = f'''\t(gr_text "{text}"
\t\t(at {x} {y} {rotation})
\t\t(layer "F.SilkS")
\t\t(uuid "{uid}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t\t(thickness {thickness:.2f})
\t\t\t){justify_effect}
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

    print(f"\nAdded {len(text_elements)} text elements to front silkscreen")
    return True

def add_logo_or_graphics(pcb_file):
    """Add graphical elements like the radiation symbol"""

    # The Pomelo board has a radiation trefoil symbol
    # This would need to be added as gr_arc or gr_poly elements
    # For now, just note where it should go

    print("\nNote: To add the radiation symbol logo:")
    print("1. Use KiCad's 'Add Bitmap' tool to import an image")
    print("2. Or create it with gr_arc and gr_circle elements")
    print(f"3. Position it around (70, 97) on F.SilkS layer")

if __name__ == '__main__':
    pcb_file = "/home/rob/Documents/Safecast/PomeloCore-KiCad/Polemo Core/Polemo Core 2/Polemo Core 2.kicad_pcb"

    print("Adding frontside silkscreen text to PomeloCore PCB...\n")

    # Add text to front silkscreen
    success = add_frontside_silkscreen(pcb_file)

    if success:
        print("\n" + "="*50)
        print("Frontside text added successfully!")
        print("="*50)

        add_logo_or_graphics(pcb_file)

        print("\nYou can now open the PCB in KiCad to:")
        print("- View the silkscreen text on both sides")
        print("- Fine-tune text positions")
        print("- Add the radiation symbol logo")
        print("- Adjust component placement")
    else:
        print("\nError adding frontside text")
