"""Test region zoom and SVG clipping."""
import sys
sys.path.insert(0, 'src')

from map_generation.generation_pipeline import generate_map_from_date
from map_generation.map_renderer import REGION_VIEWPORTS

# Test Europe region map generation
print("Testing Europe region zoom...")
result = generate_map_from_date('1950', output_format='svg', hide_date_in_title=True, region='europe')
print(f'Image generated: {result.image_data is not None}')
print(f'Image length: {len(result.image_data) if result.image_data else 0}')

# Check SVG content (it's bytes, not base64)
svg_content = result.image_data.decode('utf-8')
print(f'\nHas clipPath: {"clipPath" in svg_content}')
print(f'Has clip-path attribute: {"clip-path=" in svg_content}')
print(f'Has closing g tag: {"</g>" in svg_content}')

# Check viewport being used
print(f'\nEurope viewport: {REGION_VIEWPORTS["europe"]}')

# Save SVG for manual inspection
with open('test_europe_map.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)
print("\nSaved test_europe_map.svg for inspection")

# Print first few and last few lines of SVG
lines = svg_content.split('\n')
print("\nFirst 30 lines of SVG:")
for line in lines[:30]:
    print(line)
print("\n... middle content ...")
print("\nLast 15 lines of SVG:")
for line in lines[-15:]:
    print(line)
