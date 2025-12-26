"""
Demo script for the map generation feature.

Demonstrates generating historical maps from date input.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from map_generation import generate_map_from_date


def main():
    print("=" * 60)
    print("MAP GENERATION DEMO")
    print("=" * 60)
    print()

    # Test 1: Single year (1914 - WWI start)
    print("Test 1: Generating map for 1914 (WWI start)")
    print("-" * 40)
    result = generate_map_from_date("1914", verbose=True)
    print(f"\nResult:")
    print(f"  Date range: {result.date_range}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Risk level: {result.risk_level}")
    print(f"  Entities shown: {len(result.entities_shown)}")
    for e in result.entities_shown[:5]:
        print(f"    - {e['name']} ({e['type']})")
    print(f"  Image size: {len(result.image_data)} bytes")
    print()

    # Test 2: Cold War period
    print("Test 2: Generating map for 1970 (Cold War)")
    print("-" * 40)
    result = generate_map_from_date("1970", output_format="svg")
    print(f"  Date range: {result.date_range}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Entities: {len(result.entities_shown)}")
    entity_names = [e['name'] for e in result.entities_shown]
    if 'Soviet Union' in entity_names or 'USSR' in entity_names:
        print("  Found: Soviet Union/USSR")
    if 'East Germany' in entity_names:
        print("  Found: East Germany")
    if 'West Germany' in entity_names:
        print("  Found: West Germany")
    print()

    # Test 3: Year range spanning a transition
    print("Test 3: Generating map for 1985-1995 (Soviet collapse)")
    print("-" * 40)
    result = generate_map_from_date("1985-1995")
    print(f"  Date range: {result.date_range}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Risk level: {result.risk_level}")
    print(f"  Uncertainty factors: {len(result.uncertainty.factors)}")
    for factor in result.uncertainty.factors:
        print(f"    - {factor.factor_type}: {factor.description[:50]}...")
    print()

    # Test 4: Save to file
    print("Test 4: Saving map to file")
    print("-" * 40)
    output_path = Path(__file__).parent.parent / "data" / "output" / "generated_map_1949.svg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = generate_map_from_date("1949", output_path=str(output_path), output_format="svg")
    print(f"  Saved to: {output_path}")
    print(f"  File exists: {output_path.exists()}")
    print()

    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("This feature is the inverse of map dating:")
    print("  - Map dating: Image -> Date estimate")
    print("  - Map generation: Date -> Image")
    print()
    print("See src/map_generation/ for the implementation.")


if __name__ == "__main__":
    main()
