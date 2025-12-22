"""
Historical entity recognition from extracted text.

Matches text to known historical entities (countries, cities, regions)
and returns their temporal validity ranges.
"""

from typing import List, Dict, Set, Optional
from pathlib import Path
import sys
import re

sys.path.append(str(Path(__file__).parent.parent))
from models import TextBlock, HistoricalEntity, YearRange


class EntityRecognizer:
    """
    Recognizes and extracts historical entities from text.

    Uses fuzzy matching and knowledge base lookups to identify
    entities with temporal validity.
    """

    def __init__(self, knowledge_base: Optional[object] = None):
        """
        Initialize the entity recognizer.

        Args:
            knowledge_base: HistoricalKnowledgeBase instance
        """
        self.knowledge_base = knowledge_base
        self._entity_cache: Dict[str, List[HistoricalEntity]] = {}

    def extract_entities(
        self,
        text_blocks: List[TextBlock]
    ) -> List[HistoricalEntity]:
        """
        Extract all historical entities from text blocks.

        Args:
            text_blocks: List of extracted text blocks

        Returns:
            List of identified historical entities
        """
        if self.knowledge_base is None:
            raise ValueError("Knowledge base not initialized")

        entities = []
        seen_entities: Set[str] = set()

        # Combine all text for analysis
        all_text = ' '.join(block.normalized_text for block in text_blocks)

        # Query knowledge base for entities
        for entity in self.knowledge_base.all_entities():
            if self._text_contains_entity(all_text, entity):
                # Avoid duplicates
                entity_key = f"{entity.canonical_name}:{entity.entity_type}"
                if entity_key not in seen_entities:
                    entities.append(entity)
                    seen_entities.add(entity_key)

        return entities

    def _text_contains_entity(
        self,
        text: str,
        entity: HistoricalEntity
    ) -> bool:
        """
        Check if text contains a reference to an entity.

        Uses exact matching on canonical name and alternative names.

        Args:
            text: Normalized text to search
            entity: Entity to look for

        Returns:
            True if entity is found in text
        """
        text_lower = text.lower()

        # Check canonical name
        if entity.canonical_name.lower() in text_lower:
            return True

        # Check alternative names
        for alt_name in entity.alternative_names:
            if alt_name.lower() in text_lower:
                return True

        # Check the original name
        if entity.name.lower() in text_lower:
            return True

        return False

    def extract_specific_entity_types(
        self,
        text_blocks: List[TextBlock],
        entity_types: List[str]
    ) -> List[HistoricalEntity]:
        """
        Extract only specific types of entities.

        Args:
            text_blocks: List of extracted text blocks
            entity_types: List of entity types to extract (e.g., ['country', 'city'])

        Returns:
            Filtered list of entities
        """
        all_entities = self.extract_entities(text_blocks)
        return [
            entity for entity in all_entities
            if entity.entity_type in entity_types
        ]

    def get_most_constraining_entities(
        self,
        entities: List[HistoricalEntity],
        top_n: int = 10
    ) -> List[HistoricalEntity]:
        """
        Get the most temporally constraining entities.

        Entities with shorter validity ranges are more valuable for dating.

        Args:
            entities: List of identified entities
            top_n: Number of top entities to return

        Returns:
            Most constraining entities
        """
        # Sort by range duration (shorter = more constraining)
        sorted_entities = sorted(
            entities,
            key=lambda e: e.valid_range.end - e.valid_range.start
        )

        return sorted_entities[:top_n]

    def filter_by_temporal_overlap(
        self,
        entities: List[HistoricalEntity]
    ) -> Optional[YearRange]:
        """
        Find the temporal overlap of all entities.

        If entities don't all overlap, returns None (inconsistent map).

        Args:
            entities: List of entities to check

        Returns:
            YearRange of overlap, or None if no complete overlap
        """
        if not entities:
            return None

        # Start with the first entity's range
        overlap = entities[0].valid_range

        # Intersect with each subsequent entity
        for entity in entities[1:]:
            new_overlap = overlap.intersection(entity.valid_range)
            if new_overlap is None:
                # No overlap means inconsistent entities
                return None
            overlap = new_overlap

        return overlap

    def analyze_entity_consistency(
        self,
        entities: List[HistoricalEntity]
    ) -> Dict[str, any]:
        """
        Analyze the temporal consistency of extracted entities.

        Returns:
            Dictionary with consistency metrics
        """
        if not entities:
            return {
                'is_consistent': True,
                'overlap': None,
                'conflicts': [],
                'entity_count': 0
            }

        overlap = self.filter_by_temporal_overlap(entities)
        conflicts = []

        # Find pairwise conflicts
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                if not entity1.valid_range.overlaps(entity2.valid_range):
                    conflicts.append({
                        'entity1': entity1.canonical_name,
                        'range1': str(entity1.valid_range),
                        'entity2': entity2.canonical_name,
                        'range2': str(entity2.valid_range),
                    })

        return {
            'is_consistent': overlap is not None,
            'overlap': overlap,
            'conflicts': conflicts,
            'entity_count': len(entities),
            'earliest_start': min(e.valid_range.start for e in entities),
            'latest_end': max(e.valid_range.end for e in entities),
        }
