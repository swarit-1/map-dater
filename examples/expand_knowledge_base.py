"""
Example: Expanding the historical knowledge base.

This script demonstrates how to add new historical entities to improve
the dating accuracy of the system.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from knowledge import HistoricalKnowledgeBase
from models import HistoricalEntity, YearRange


def add_asian_entities():
    """Add Asian historical entities."""
    kb = HistoricalKnowledgeBase()

    # Add more Asian countries
    entities = [
        {
            'name': 'Manchukuo',
            'canonical': 'Manchukuo',
            'type': 'country',
            'range': (1932, 1945),
            'alts': ['Manchuria', 'State of Manchuria'],
            'context': {'puppet_state': True, 'controller': 'Japan'}
        },
        {
            'name': 'Republic of China',
            'canonical': 'Republic of China',
            'type': 'country',
            'range': (1912, 1949),
            'alts': ['ROC', 'Nationalist China'],
            'context': {'succeeded_by': 'PRC', 'relocated_to': 'Taiwan'}
        },
        {
            'name': "People's Republic of China",
            'canonical': "People's Republic of China",
            'type': 'country',
            'range': (1949, 2100),
            'alts': ['PRC', 'Communist China', 'China'],
            'context': {}
        },
        {
            'name': 'French Indochina',
            'canonical': 'French Indochina',
            'type': 'territory',
            'range': (1887, 1954),
            'alts': ['Indochine', 'Indochina'],
            'context': {'colonial_power': 'France'}
        },
        {
            'name': 'Dutch East Indies',
            'canonical': 'Dutch East Indies',
            'type': 'territory',
            'range': (1800, 1949),
            'alts': ['Netherlands East Indies', 'NEI'],
            'context': {'became': 'Indonesia'}
        },
        {
            'name': 'Indonesia',
            'canonical': 'Indonesia',
            'type': 'country',
            'range': (1949, 2100),
            'alts': ['Republic of Indonesia'],
            'context': {}
        },
    ]

    for data in entities:
        entity = HistoricalEntity(
            name=data['name'],
            canonical_name=data['canonical'],
            entity_type=data['type'],
            valid_range=YearRange(data['range'][0], data['range'][1]),
            alternative_names=data['alts'],
            context=data['context']
        )
        kb.add_entity(entity)

    print(f"Added {len(entities)} Asian entities")
    return kb


def add_african_entities():
    """Add African historical entities."""
    kb = HistoricalKnowledgeBase()

    entities = [
        {
            'name': 'Gold Coast',
            'canonical': 'Gold Coast',
            'type': 'territory',
            'range': (1867, 1957),
            'alts': ['British Gold Coast'],
            'context': {'became': 'Ghana'}
        },
        {
            'name': 'Ghana',
            'canonical': 'Ghana',
            'type': 'country',
            'range': (1957, 2100),
            'alts': ['Republic of Ghana'],
            'context': {}
        },
        {
            'name': 'Tanganyika',
            'canonical': 'Tanganyika',
            'type': 'territory',
            'range': (1920, 1964),
            'alts': ['British Tanganyika'],
            'context': {}
        },
        {
            'name': 'Tanzania',
            'canonical': 'Tanzania',
            'type': 'country',
            'range': (1964, 2100),
            'alts': ['United Republic of Tanzania'],
            'context': {'formed_from': ['Tanganyika', 'Zanzibar']}
        },
        {
            'name': 'Upper Volta',
            'canonical': 'Upper Volta',
            'type': 'country',
            'range': (1958, 1984),
            'alts': ['Republic of Upper Volta'],
            'context': {}
        },
        {
            'name': 'Burkina Faso',
            'canonical': 'Burkina Faso',
            'type': 'country',
            'range': (1984, 2100),
            'alts': [],
            'context': {'formerly': 'Upper Volta'}
        },
    ]

    for data in entities:
        entity = HistoricalEntity(
            name=data['name'],
            canonical_name=data['canonical'],
            entity_type=data['type'],
            valid_range=YearRange(data['range'][0], data['range'][1]),
            alternative_names=data['alts'],
            context=data['context']
        )
        kb.add_entity(entity)

    print(f"Added {len(entities)} African entities")
    return kb


def demonstrate_custom_knowledge_base():
    """Show how to use a custom knowledge base."""
    print("="*60)
    print("CUSTOM KNOWLEDGE BASE DEMO")
    print("="*60)

    # Create base KB
    kb = HistoricalKnowledgeBase()

    # Add custom entities
    custom_entity = HistoricalEntity(
        name="My Historical Entity",
        canonical_name="My Historical Entity",
        entity_type="region",
        valid_range=YearRange(1800, 1900),
        alternative_names=["Alternative Name"],
        context={'note': 'Custom entity for testing'}
    )

    kb.add_entity(custom_entity)

    # Save to file
    output_path = Path(__file__).parent.parent / 'data' / 'knowledge_base' / 'custom_entities.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    kb.save_to_json(str(output_path))
    print(f"\nSaved knowledge base to: {output_path}")

    # Load it back
    kb2 = HistoricalKnowledgeBase()
    kb2.load_from_json(str(output_path))

    print(f"Loaded knowledge base with {len(kb2.all_entities())} entities")

    # Use in pipeline
    from pipeline import MapDaterPipeline

    pipeline = MapDaterPipeline(knowledge_base=kb2)
    print("\nPipeline initialized with custom knowledge base")

    info = pipeline.get_pipeline_info()
    print(f"Knowledge base contains {info['knowledge_base']['entities']} entities")


def main():
    """Run all examples."""
    print("\n" + "#"*60)
    print("# KNOWLEDGE BASE EXPANSION EXAMPLES")
    print("#"*60 + "\n")

    kb_asian = add_asian_entities()
    kb_african = add_african_entities()

    print("\n" + "-"*60)

    # Combine all
    kb_full = HistoricalKnowledgeBase()

    # Add Asian entities
    for entity in kb_asian.all_entities():
        if entity not in kb_full.all_entities():
            kb_full.add_entity(entity)

    # Add African entities
    for entity in kb_african.all_entities():
        if entity not in kb_full.all_entities():
            kb_full.add_entity(entity)

    print(f"\nCombined knowledge base has {len(kb_full.all_entities())} entities")

    # Show by type
    print("\nEntities by type:")
    for entity_type in ['country', 'city', 'territory', 'empire', 'region']:
        count = len(kb_full.get_entities_by_type(entity_type))
        if count > 0:
            print(f"  {entity_type}: {count}")

    print("\n" + "-"*60 + "\n")

    demonstrate_custom_knowledge_base()

    print("\n" + "#"*60)
    print("# EXAMPLES COMPLETE")
    print("#"*60 + "\n")


if __name__ == '__main__':
    main()
