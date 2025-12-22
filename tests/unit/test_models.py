"""
Unit tests for core data models.
"""

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from models import YearRange, HistoricalEntity, DateSignal, SignalType


class TestYearRange(unittest.TestCase):
    """Test YearRange functionality."""

    def test_valid_range(self):
        """Test creating a valid year range."""
        yr = YearRange(1900, 1950)
        self.assertEqual(yr.start, 1900)
        self.assertEqual(yr.end, 1950)

    def test_invalid_range(self):
        """Test that invalid ranges raise errors."""
        with self.assertRaises(ValueError):
            YearRange(1950, 1900)

    def test_overlaps(self):
        """Test overlap detection."""
        yr1 = YearRange(1900, 1950)
        yr2 = YearRange(1940, 1990)
        yr3 = YearRange(1960, 2000)

        self.assertTrue(yr1.overlaps(yr2))
        self.assertTrue(yr2.overlaps(yr1))
        self.assertFalse(yr1.overlaps(yr3))

    def test_intersection(self):
        """Test range intersection."""
        yr1 = YearRange(1900, 1950)
        yr2 = YearRange(1940, 1990)
        yr3 = YearRange(1960, 2000)

        # Overlapping ranges
        intersection = yr1.intersection(yr2)
        self.assertIsNotNone(intersection)
        self.assertEqual(intersection.start, 1940)
        self.assertEqual(intersection.end, 1950)

        # Non-overlapping ranges
        intersection = yr1.intersection(yr3)
        self.assertIsNone(intersection)

    def test_repr(self):
        """Test string representation."""
        yr1 = YearRange(1900, 1950)
        yr2 = YearRange(1945, 1945)

        self.assertEqual(repr(yr1), "1900-1950")
        self.assertEqual(repr(yr2), "1945")


class TestHistoricalEntity(unittest.TestCase):
    """Test HistoricalEntity functionality."""

    def test_entity_creation(self):
        """Test creating a historical entity."""
        entity = HistoricalEntity(
            name="USSR",
            canonical_name="Soviet Union",
            entity_type="country",
            valid_range=YearRange(1922, 1991),
            alternative_names=["U.S.S.R.", "Soviet Union"]
        )

        self.assertEqual(entity.name, "USSR")
        self.assertEqual(entity.canonical_name, "Soviet Union")
        self.assertEqual(entity.entity_type, "country")

    def test_was_valid_in(self):
        """Test temporal validity checking."""
        entity = HistoricalEntity(
            name="USSR",
            canonical_name="Soviet Union",
            entity_type="country",
            valid_range=YearRange(1922, 1991)
        )

        self.assertTrue(entity.was_valid_in(1950))
        self.assertTrue(entity.was_valid_in(1922))
        self.assertTrue(entity.was_valid_in(1991))
        self.assertFalse(entity.was_valid_in(1921))
        self.assertFalse(entity.was_valid_in(1992))


class TestDateSignal(unittest.TestCase):
    """Test DateSignal functionality."""

    def test_signal_creation(self):
        """Test creating a date signal."""
        signal = DateSignal(
            signal_type=SignalType.ENTITY,
            description="USSR present",
            year_range=YearRange(1922, 1991),
            confidence=0.95,
            source="entity:USSR",
            reasoning="USSR existed 1922-1991"
        )

        self.assertEqual(signal.signal_type, SignalType.ENTITY)
        self.assertEqual(signal.confidence, 0.95)

    def test_invalid_confidence(self):
        """Test that invalid confidence raises error."""
        with self.assertRaises(ValueError):
            DateSignal(
                signal_type=SignalType.ENTITY,
                description="Test",
                year_range=YearRange(1900, 1950),
                confidence=1.5,  # Invalid
                source="test",
                reasoning="test"
            )


if __name__ == '__main__':
    unittest.main()
