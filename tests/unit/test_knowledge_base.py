"""
Unit tests for historical knowledge base.
"""

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from knowledge import HistoricalKnowledgeBase
from models import YearRange


class TestHistoricalKnowledgeBase(unittest.TestCase):
    """Test HistoricalKnowledgeBase functionality."""

    def setUp(self):
        """Set up test knowledge base."""
        self.kb = HistoricalKnowledgeBase()

    def test_default_entities_loaded(self):
        """Test that default entities are loaded."""
        entities = self.kb.all_entities()
        self.assertGreater(len(entities), 0)

    def test_get_entities_by_type(self):
        """Test filtering entities by type."""
        countries = self.kb.get_entities_by_type('country')
        cities = self.kb.get_entities_by_type('city')

        self.assertGreater(len(countries), 0)
        self.assertGreater(len(cities), 0)

        # Verify types
        for entity in countries:
            self.assertEqual(entity.entity_type, 'country')

    def test_find_by_name(self):
        """Test finding entities by name."""
        # Find USSR by primary name
        ussr = self.kb.find_by_name('USSR')
        self.assertIsNotNone(ussr)
        self.assertEqual(ussr.canonical_name, 'Soviet Union')

        # Find by canonical name
        ussr2 = self.kb.find_by_name('Soviet Union')
        self.assertIsNotNone(ussr2)

        # Find by alternative name
        ussr3 = self.kb.find_by_name('U.S.S.R.')
        self.assertIsNotNone(ussr3)

        # Non-existent entity
        fake = self.kb.find_by_name('Nonexistent Country')
        self.assertIsNone(fake)

    def test_get_entities_valid_in_year(self):
        """Test finding entities valid in a specific year."""
        # 1950: USSR should exist, Russian Empire should not
        entities_1950 = self.kb.get_entities_valid_in_year(1950)
        names_1950 = [e.canonical_name for e in entities_1950]

        self.assertIn('Soviet Union', names_1950)
        self.assertNotIn('Russian Empire', names_1950)

        # 1900: Russian Empire should exist, USSR should not
        entities_1900 = self.kb.get_entities_valid_in_year(1900)
        names_1900 = [e.canonical_name for e in entities_1900]

        self.assertIn('Russian Empire', names_1900)
        self.assertNotIn('Soviet Union', names_1900)

    def test_city_name_changes(self):
        """Test historical city name changes."""
        # Constantinople vs Istanbul
        constantinople = self.kb.find_by_name('Constantinople')
        istanbul = self.kb.find_by_name('Istanbul')

        self.assertIsNotNone(constantinople)
        self.assertIsNotNone(istanbul)

        # Constantinople valid before 1930
        self.assertTrue(constantinople.was_valid_in(1920))
        self.assertFalse(constantinople.was_valid_in(1940))

        # Istanbul valid after 1930
        self.assertTrue(istanbul.was_valid_in(1940))

    def test_country_splits(self):
        """Test countries that split."""
        # Czechoslovakia existed 1918-1993
        czechoslovakia = self.kb.find_by_name('Czechoslovakia')
        self.assertIsNotNone(czechoslovakia)
        self.assertTrue(czechoslovakia.was_valid_in(1980))
        self.assertFalse(czechoslovakia.was_valid_in(2000))

        # Czech Republic exists post-1993
        czech = self.kb.find_by_name('Czech Republic')
        self.assertIsNotNone(czech)
        self.assertTrue(czech.was_valid_in(2000))
        self.assertFalse(czech.was_valid_in(1980))


if __name__ == '__main__':
    unittest.main()
