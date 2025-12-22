"""
Create a mock map image for testing.

This script generates a simple test map with text labels that can be
used to test the full pipeline without requiring real historical maps.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
except ImportError:
    print("Error: PIL (Pillow) is required")
    print("Install with: pip install Pillow")
    sys.exit(1)


def create_mock_map(
    output_path: str,
    scenario: str = "cold_war"
):
    """
    Create a mock map image with text.

    Args:
        output_path: Where to save the image
        scenario: Which historical scenario to create
    """

    # Create a blank image (simulating an old map)
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color=(245, 235, 220))  # Beige background

    draw = ImageDraw.Draw(img)

    # Try to use a basic font
    try:
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_medium = ImageFont.truetype("arial.ttf", 25)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Add labels based on scenario
    if scenario == "cold_war":
        # Simulate a Cold War era map (1949-1990)
        labels = [
            ("USSR", (100, 100), font_large),
            ("East Germany", (200, 300), font_medium),
            ("West Germany", (200, 400), font_medium),
            ("Leningrad", (150, 150), font_small),
            ("1975", (700, 550), font_small),
        ]

    elif scenario == "post_ww1":
        # Simulate post-WWI map (1918-1939)
        labels = [
            ("Czechoslovakia", (200, 250), font_large),
            ("Yugoslavia", (200, 400), font_large),
            ("Constantinople", (500, 300), font_medium),
            ("1925", (700, 550), font_small),
        ]

    elif scenario == "modern":
        # Modern map (1995+)
        labels = [
            ("Czech Republic", (200, 200), font_medium),
            ("Slovakia", (200, 300), font_medium),
            ("Russia", (100, 100), font_large),
            ("Istanbul", (500, 300), font_medium),
            ("Mumbai", (600, 400), font_small),
        ]

    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    # Draw all labels
    for text, position, font in labels:
        draw.text(position, text, fill=(0, 0, 0), font=font)

    # Add some decorative elements to make it look more map-like
    # Draw some borders
    draw.rectangle([(50, 50), (750, 550)], outline=(100, 100, 100), width=2)

    # Add a title
    title_font = font_large
    title = f"Map ({scenario.replace('_', ' ').title()})"
    draw.text((250, 20), title, fill=(50, 50, 50), font=font_medium)

    # Save the image
    img.save(output_path)
    print(f"Created mock map: {output_path}")


def main():
    """Create sample mock maps."""
    output_dir = Path(__file__).parent.parent / 'data' / 'sample_maps'
    output_dir.mkdir(parents=True, exist_ok=True)

    scenarios = ['cold_war', 'post_ww1', 'modern']

    for scenario in scenarios:
        output_path = output_dir / f"mock_map_{scenario}.png"
        create_mock_map(str(output_path), scenario)

    print(f"\nAll mock maps created in: {output_dir}")


if __name__ == '__main__':
    main()
