"""
Demo script showing how to use the Map Dater system.

This example demonstrates the end-to-end pipeline without requiring
an actual map image (uses mock data for demonstration).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from models import (
    HistoricalEntity, YearRange, TextBlock, BoundingBox,
    ProcessedImage
)
from knowledge import HistoricalKnowledgeBase
from entities import EntityRecognizer
from inference import DateEstimator
from explanations import ExplanationGenerator
import numpy as np


def demo_knowledge_base():
    """Demonstrate the knowledge base."""
    print("="*60)
    print("KNOWLEDGE BASE DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    print(f"\nTotal entities: {len(kb.all_entities())}")

    # Show some countries
    print("\nSample countries:")
    countries = kb.get_entities_by_type('country')
    for country in countries[:5]:
        print(f"  - {country.canonical_name}: {country.valid_range}")

    # Show city name changes
    print("\nHistorical city name changes:")
    cities = kb.get_entities_by_type('city')
    for city in cities[:5]:
        print(f"  - {city.canonical_name}: {city.valid_range}")

    # Find specific entity
    print("\nLooking up 'USSR':")
    ussr = kb.find_by_name('USSR')
    if ussr:
        print(f"  Name: {ussr.canonical_name}")
        print(f"  Type: {ussr.entity_type}")
        print(f"  Valid: {ussr.valid_range}")
        print(f"  Alternatives: {ussr.alternative_names}")

    print()


def demo_entity_inference():
    """Demonstrate date estimation from entities."""
    print("="*60)
    print("DATE ESTIMATION DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    # Scenario: A map showing USSR and East Germany
    print("\nScenario: Map shows 'USSR' and 'East Germany'")

    entities = [
        kb.find_by_name('USSR'),
        kb.find_by_name('East Germany')
    ]

    print("\nIdentified entities:")
    for entity in entities:
        print(f"  - {entity.canonical_name}: {entity.valid_range}")

    # Estimate date
    estimator = DateEstimator()
    estimate = estimator.estimate_date(entities)

    # Generate explanation
    explainer = ExplanationGenerator(verbose=True)
    explanation = explainer.generate_explanation(estimate)

    print(f"\n{explanation}")


def demo_conflicting_entities():
    """Demonstrate handling of conflicting entities."""
    print("\n" + "="*60)
    print("CONFLICTING ENTITIES DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    # Scenario: A map showing USSR (1922-1991) and Constantinople (330-1930)
    print("\nScenario: Map shows 'USSR' and 'Constantinople'")

    entities = [
        kb.find_by_name('USSR'),
        kb.find_by_name('Constantinople')
    ]

    print("\nIdentified entities:")
    for entity in entities:
        print(f"  - {entity.canonical_name}: {entity.valid_range}")

    # These overlap in 1922-1930
    estimator = DateEstimator()
    estimate = estimator.estimate_date(entities)

    explainer = ExplanationGenerator(verbose=True)
    explanation = explainer.generate_explanation(estimate)

    print(f"\n{explanation}")


def demo_narrow_constraint():
    """Demonstrate highly constrained dating."""
    print("\n" + "="*60)
    print("NARROW CONSTRAINT DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    # Scenario: Map shows Leningrad (1924-1991) and East Germany (1949-1990)
    print("\nScenario: Map shows 'Leningrad' and 'East Germany'")

    entities = [
        kb.find_by_name('Leningrad'),
        kb.find_by_name('East Germany')
    ]

    print("\nIdentified entities:")
    for entity in entities:
        print(f"  - {entity.canonical_name}: {entity.valid_range}")

    # These overlap only in 1949-1990
    estimator = DateEstimator()
    estimate = estimator.estimate_date(entities)

    explainer = ExplanationGenerator(verbose=True)
    explanation = explainer.generate_explanation(estimate)

    print(f"\n{explanation}")


def demo_json_export():
    """Demonstrate JSON export of results."""
    print("\n" + "="*60)
    print("JSON EXPORT DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    entities = [
        kb.find_by_name('Czechoslovakia'),
    ]

    estimator = DateEstimator()
    estimate = estimator.estimate_date(entities)

    explainer = ExplanationGenerator()
    json_result = explainer.generate_json_explanation(estimate)

    import json
    print("\nJSON output:")
    print(json.dumps(json_result, indent=2))


def demo_complete_scenario():
    """Demonstrate a complete realistic scenario."""
    print("\n" + "="*60)
    print("COMPLETE SCENARIO DEMO")
    print("="*60)

    kb = HistoricalKnowledgeBase()

    # Realistic scenario: Cold War era map
    print("\nScenario: Map contains:")
    print("  - 'USSR'")
    print("  - 'West Germany'")
    print("  - 'Bombay' (not Mumbai)")
    print("  - Year reference: 1975")

    entities = [
        kb.find_by_name('USSR'),
        kb.find_by_name('West Germany'),
        kb.find_by_name('Bombay')
    ]

    print("\nIdentified entities:")
    for entity in entities:
        print(f"  - {entity.canonical_name}: {entity.valid_range}")

    # Estimate with year reference
    estimator = DateEstimator()
    estimate = estimator.estimate_date(
        entities=entities,
        extracted_years=[1975]
    )

    explainer = ExplanationGenerator(verbose=True)
    explanation = explainer.generate_explanation(estimate)

    print(f"\n{explanation}")


def main():
    """Run all demos."""
    print("\n" + "#"*60)
    print("# MAP DATER SYSTEM - DEMONSTRATION")
    print("#"*60 + "\n")

    try:
        demo_knowledge_base()
        demo_entity_inference()
        demo_conflicting_entities()
        demo_narrow_constraint()
        demo_json_export()
        demo_complete_scenario()

        print("\n" + "#"*60)
        print("# DEMO COMPLETE")
        print("#"*60 + "\n")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
