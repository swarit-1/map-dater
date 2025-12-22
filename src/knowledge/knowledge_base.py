"""
Historical knowledge base containing temporal facts about entities.

This is the core reference database for dating maps.
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from models import HistoricalEntity, YearRange


class HistoricalKnowledgeBase:
    """
    Storage and retrieval of historical entities with temporal validity.

    This knowledge base contains:
    - Countries and their existence periods
    - Cities and their historical names
    - Empires and territorial entities
    - Other cartographic features with temporal significance
    """

    def __init__(self):
        """Initialize the knowledge base with core historical facts."""
        self.entities: List[HistoricalEntity] = []
        self._load_default_entities()

    def _load_default_entities(self):
        """Load default historical entities into the knowledge base."""

        # Major 20th century political entities
        entities_data = [
            # Soviet Union and related
            {
                'name': 'USSR',
                'canonical': 'Soviet Union',
                'type': 'country',
                'range': (1922, 1991),
                'alts': ['Soviet Union', 'U.S.S.R.', 'Union of Soviet Socialist Republics', 'CCCP']
            },
            {
                'name': 'Russian Empire',
                'canonical': 'Russian Empire',
                'type': 'country',
                'range': (1721, 1917),
                'alts': ['Imperial Russia', 'Tsarist Russia']
            },
            {
                'name': 'Russian Federation',
                'canonical': 'Russia',
                'type': 'country',
                'range': (1991, 2100),
                'alts': ['Russia', 'Russian Federation']
            },

            # Germany
            {
                'name': 'Weimar Republic',
                'canonical': 'Weimar Republic',
                'type': 'country',
                'range': (1919, 1933),
                'alts': ['German Republic']
            },
            {
                'name': 'Nazi Germany',
                'canonical': 'Nazi Germany',
                'type': 'country',
                'range': (1933, 1945),
                'alts': ['Third Reich', 'Greater German Reich', 'Deutsches Reich']
            },
            {
                'name': 'East Germany',
                'canonical': 'East Germany',
                'type': 'country',
                'range': (1949, 1990),
                'alts': ['German Democratic Republic', 'GDR', 'DDR']
            },
            {
                'name': 'West Germany',
                'canonical': 'West Germany',
                'type': 'country',
                'range': (1949, 1990),
                'alts': ['Federal Republic of Germany', 'FRG', 'BRD']
            },
            {
                'name': 'Germany',
                'canonical': 'Germany',
                'type': 'country',
                'range': (1990, 2100),
                'alts': ['Federal Republic of Germany', 'Deutschland']
            },

            # Yugoslavia
            {
                'name': 'Yugoslavia',
                'canonical': 'Yugoslavia',
                'type': 'country',
                'range': (1918, 1992),
                'alts': ['Kingdom of Yugoslavia', 'Socialist Federal Republic of Yugoslavia', 'SFRY']
            },

            # Czechoslovakia
            {
                'name': 'Czechoslovakia',
                'canonical': 'Czechoslovakia',
                'type': 'country',
                'range': (1918, 1993),
                'alts': ['Czecho-Slovakia', 'CSSR']
            },
            {
                'name': 'Czech Republic',
                'canonical': 'Czech Republic',
                'type': 'country',
                'range': (1993, 2100),
                'alts': ['Czechia']
            },
            {
                'name': 'Slovakia',
                'canonical': 'Slovakia',
                'type': 'country',
                'range': (1993, 2100),
                'alts': ['Slovak Republic']
            },

            # Middle East
            {
                'name': 'Palestine',
                'canonical': 'British Mandate of Palestine',
                'type': 'territory',
                'range': (1920, 1948),
                'alts': ['Palestine', 'Mandatory Palestine']
            },
            {
                'name': 'Israel',
                'canonical': 'Israel',
                'type': 'country',
                'range': (1948, 2100),
                'alts': ['State of Israel']
            },
            {
                'name': 'Ottoman Empire',
                'canonical': 'Ottoman Empire',
                'type': 'empire',
                'range': (1299, 1922),
                'alts': ['Turkish Empire']
            },

            # Asia
            {
                'name': 'Siam',
                'canonical': 'Siam',
                'type': 'country',
                'range': (1350, 1939),
                'alts': ['Kingdom of Siam']
            },
            {
                'name': 'Thailand',
                'canonical': 'Thailand',
                'type': 'country',
                'range': (1939, 2100),
                'alts': ['Kingdom of Thailand']
            },
            {
                'name': 'Burma',
                'canonical': 'Burma',
                'type': 'country',
                'range': (1948, 1989),
                'alts': ['Union of Burma']
            },
            {
                'name': 'Myanmar',
                'canonical': 'Myanmar',
                'type': 'country',
                'range': (1989, 2100),
                'alts': ['Union of Myanmar']
            },
            {
                'name': 'Ceylon',
                'canonical': 'Ceylon',
                'type': 'country',
                'range': (1505, 1972),
                'alts': ['British Ceylon', 'Dominion of Ceylon']
            },
            {
                'name': 'Sri Lanka',
                'canonical': 'Sri Lanka',
                'type': 'country',
                'range': (1972, 2100),
                'alts': ['Democratic Socialist Republic of Sri Lanka']
            },

            # Africa
            {
                'name': 'Rhodesia',
                'canonical': 'Rhodesia',
                'type': 'country',
                'range': (1965, 1979),
                'alts': ['Southern Rhodesia']
            },
            {
                'name': 'Zimbabwe',
                'canonical': 'Zimbabwe',
                'type': 'country',
                'range': (1980, 2100),
                'alts': ['Republic of Zimbabwe']
            },
            {
                'name': 'Zaire',
                'canonical': 'Zaire',
                'type': 'country',
                'range': (1971, 1997),
                'alts': ['Republic of Zaire']
            },
            {
                'name': 'Democratic Republic of Congo',
                'canonical': 'Democratic Republic of Congo',
                'type': 'country',
                'range': (1997, 2100),
                'alts': ['DRC', 'DR Congo', 'Congo-Kinshasa']
            },

            # Cities with name changes
            {
                'name': 'Constantinople',
                'canonical': 'Constantinople',
                'type': 'city',
                'range': (330, 1930),
                'alts': ['Byzantium']
            },
            {
                'name': 'Istanbul',
                'canonical': 'Istanbul',
                'type': 'city',
                'range': (1930, 2100),
                'alts': []
            },
            {
                'name': 'Leningrad',
                'canonical': 'Leningrad',
                'type': 'city',
                'range': (1924, 1991),
                'alts': []
            },
            {
                'name': 'St. Petersburg',
                'canonical': 'St. Petersburg',
                'type': 'city',
                'range': (1703, 1914),
                'alts': ['Saint Petersburg', 'Sankt-Peterburg']
            },
            {
                'name': 'Petrograd',
                'canonical': 'Petrograd',
                'type': 'city',
                'range': (1914, 1924),
                'alts': []
            },
            {
                'name': 'St. Petersburg',
                'canonical': 'St. Petersburg',
                'type': 'city',
                'range': (1991, 2100),
                'alts': ['Saint Petersburg']
            },
            {
                'name': 'Bombay',
                'canonical': 'Bombay',
                'type': 'city',
                'range': (1534, 1995),
                'alts': []
            },
            {
                'name': 'Mumbai',
                'canonical': 'Mumbai',
                'type': 'city',
                'range': (1995, 2100),
                'alts': []
            },
            {
                'name': 'Peking',
                'canonical': 'Peking',
                'type': 'city',
                'range': (1403, 1949),
                'alts': ['Peiping']
            },
            {
                'name': 'Beijing',
                'canonical': 'Beijing',
                'type': 'city',
                'range': (1949, 2100),
                'alts': []
            },
            {
                'name': 'Saigon',
                'canonical': 'Saigon',
                'type': 'city',
                'range': (1698, 1976),
                'alts': []
            },
            {
                'name': 'Ho Chi Minh City',
                'canonical': 'Ho Chi Minh City',
                'type': 'city',
                'range': (1976, 2100),
                'alts': []
            },
        ]

        for data in entities_data:
            entity = HistoricalEntity(
                name=data['name'],
                canonical_name=data['canonical'],
                entity_type=data['type'],
                valid_range=YearRange(data['range'][0], data['range'][1]),
                alternative_names=data['alts']
            )
            self.entities.append(entity)

    def add_entity(self, entity: HistoricalEntity):
        """
        Add a new entity to the knowledge base.

        Args:
            entity: HistoricalEntity to add
        """
        self.entities.append(entity)

    def all_entities(self) -> List[HistoricalEntity]:
        """
        Get all entities in the knowledge base.

        Returns:
            List of all entities
        """
        return self.entities

    def get_entities_by_type(self, entity_type: str) -> List[HistoricalEntity]:
        """
        Get all entities of a specific type.

        Args:
            entity_type: Type to filter by (e.g., 'country', 'city')

        Returns:
            Filtered list of entities
        """
        return [e for e in self.entities if e.entity_type == entity_type]

    def get_entities_valid_in_year(self, year: int) -> List[HistoricalEntity]:
        """
        Get all entities that existed in a specific year.

        Args:
            year: Year to check

        Returns:
            List of entities valid in that year
        """
        return [e for e in self.entities if e.was_valid_in(year)]

    def find_by_name(self, name: str) -> Optional[HistoricalEntity]:
        """
        Find an entity by any of its names.

        Args:
            name: Name to search for (case-insensitive)

        Returns:
            First matching entity, or None
        """
        name_lower = name.lower()

        for entity in self.entities:
            if entity.name.lower() == name_lower:
                return entity
            if entity.canonical_name.lower() == name_lower:
                return entity
            if any(alt.lower() == name_lower for alt in entity.alternative_names):
                return entity

        return None

    def load_from_json(self, json_path: str):
        """
        Load additional entities from a JSON file.

        Expected format:
        [
            {
                "name": "Entity Name",
                "canonical_name": "Canonical Name",
                "entity_type": "country",
                "valid_range": [1900, 1950],
                "alternative_names": ["Alt1", "Alt2"]
            },
            ...
        ]

        Args:
            json_path: Path to JSON file
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            entity = HistoricalEntity(
                name=item['name'],
                canonical_name=item['canonical_name'],
                entity_type=item['entity_type'],
                valid_range=YearRange(item['valid_range'][0], item['valid_range'][1]),
                alternative_names=item.get('alternative_names', []),
                context=item.get('context', {})
            )
            self.add_entity(entity)

    def save_to_json(self, json_path: str):
        """
        Save the knowledge base to a JSON file.

        Args:
            json_path: Path to save to
        """
        data = []
        for entity in self.entities:
            data.append({
                'name': entity.name,
                'canonical_name': entity.canonical_name,
                'entity_type': entity.entity_type,
                'valid_range': [entity.valid_range.start, entity.valid_range.end],
                'alternative_names': entity.alternative_names,
                'context': entity.context
            })

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
