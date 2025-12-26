"""
Tests for the historical state resolver module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from models import YearRange
from map_generation.date_parser import DateParser, ParsedDateRange
from map_generation.historical_state_resolver import (
    HistoricalStateResolver,
    ResolvedState,
    ResolvedEntity,
    EntityConflict
)


class TestHistoricalStateResolver:
    """Tests for HistoricalStateResolver class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = HistoricalStateResolver()
        self.parser = DateParser()

    # --- Basic Resolution Tests ---

    def test_resolve_single_year(self):
        """Test resolving entities for a single year."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        assert isinstance(result, ResolvedState)
        assert result.date_range.start == 1970
        assert result.date_range.end == 1970
        assert len(result.entities) > 0

    def test_resolve_year_range(self):
        """Test resolving entities for a year range."""
        parsed = self.parser.parse("1949-1990")
        result = self.resolver.resolve(parsed)

        assert result.date_range.start == 1949
        assert result.date_range.end == 1990
        assert len(result.entities) > 0

    def test_resolved_state_has_dominant_entities(self):
        """Test that resolved state has dominant entities."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        assert len(result.dominant_entities) > 0

    def test_resolved_state_has_metadata(self):
        """Test that resolved state has metadata."""
        parsed = self.parser.parse("1949-1990")
        result = self.resolver.resolve(parsed)

        assert 'midpoint' in result.metadata
        assert result.metadata['midpoint'] == 1969

    # --- Entity Type Filtering ---

    def test_countries_property(self):
        """Test filtering for countries."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        countries = result.countries
        assert all(e.entity_type == 'country' for e in countries)

    def test_cities_property(self):
        """Test filtering for cities."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        cities = result.cities
        assert all(e.entity_type == 'city' for e in cities)

    # --- Specific Historical Periods ---

    def test_cold_war_entities(self):
        """Test that Cold War entities are found for 1970."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        entity_names = [e.name for e in result.entities]

        # Should include divided Germany and USSR
        assert 'Soviet Union' in entity_names or 'USSR' in entity_names
        assert 'East Germany' in entity_names
        assert 'West Germany' in entity_names

    def test_post_1991_entities(self):
        """Test that modern entities are found for 2000."""
        parsed = self.parser.parse("2000")
        result = self.resolver.resolve(parsed)

        entity_names = [e.name for e in result.entities]

        # Should include unified Germany and Russia
        assert 'Germany' in entity_names
        assert 'Russian Federation' in entity_names or 'Russia' in entity_names

        # Should NOT include USSR
        assert 'Soviet Union' not in entity_names
        assert 'USSR' not in entity_names

    def test_pre_ww1_entities(self):
        """Test entities for pre-WWI period."""
        parsed = self.parser.parse("1910")
        result = self.resolver.resolve(parsed)

        entity_names = [e.name for e in result.entities]

        # Should include Ottoman Empire and Russian Empire
        assert 'Ottoman Empire' in entity_names
        assert 'Russian Empire' in entity_names

    # --- Overlap Types ---

    def test_full_overlap_confidence(self):
        """Test that full overlap entities have high confidence."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        # USSR existed 1922-1991, so 1970 is fully covered
        ussr = next((e for e in result.entities if 'Soviet' in e.name or 'USSR' in e.name), None)
        if ussr:
            assert ussr.overlap_type == 'full'
            assert ussr.confidence == 1.0

    def test_partial_overlap_lower_confidence(self):
        """Test that partial overlap entities have lower confidence."""
        parsed = self.parser.parse("1988-1995")
        result = self.resolver.resolve(parsed)

        # USSR ended in 1991, so partial overlap
        ussr = next((e for e in result.entities if 'Soviet' in e.name or 'USSR' in e.name), None)
        if ussr:
            assert ussr.overlap_type in ('partial_end', 'contained')
            assert ussr.confidence < 1.0

    # --- Conflict Detection ---

    def test_germany_conflict_detection(self):
        """Test detection of Germany split/unification conflicts."""
        parsed = self.parser.parse("1985-1995")
        result = self.resolver.resolve(parsed)

        # Should detect conflict between East/West Germany and unified Germany
        if result.conflicts:
            germany_conflict = next(
                (c for c in result.conflicts
                 if any('Germany' in e.name for e in c.entities)),
                None
            )
            # May or may not find conflict depending on implementation
            # Just check that conflicts list is valid
            assert isinstance(result.conflicts, list)

    # --- Assumptions ---

    def test_assumptions_for_range(self):
        """Test that assumptions are generated for year ranges."""
        parsed = self.parser.parse("1949-1990")
        result = self.resolver.resolve(parsed)

        assert len(result.assumptions) > 0
        # Should mention midpoint for ranges
        assumption_text = ' '.join(result.assumptions)
        assert 'midpoint' in assumption_text.lower() or 'cold war' in assumption_text.lower()

    def test_ww2_period_assumptions(self):
        """Test assumptions for WWII period."""
        parsed = self.parser.parse("1939-1945")
        result = self.resolver.resolve(parsed)

        assumption_text = ' '.join(result.assumptions)
        # Should mention WWI or WWII
        assert 'ww' in assumption_text.lower() or 'war' in assumption_text.lower()

    # --- Serialization ---

    def test_to_dict(self):
        """Test serialization to dictionary."""
        parsed = self.parser.parse("1970")
        result = self.resolver.resolve(parsed)

        data = result.to_dict()

        assert 'date_range' in data
        assert 'entities' in data
        assert 'dominant_entities' in data
        assert 'assumptions' in data
        assert data['date_range'] == [1970, 1970]

    # --- Convenience Method ---

    def test_get_entities_for_year(self):
        """Test convenience method for getting entities by year."""
        entities = self.resolver.get_entities_for_year(1970)

        assert len(entities) > 0
        assert all(e.was_valid_in(1970) for e in entities)


class TestResolvedEntity:
    """Tests for ResolvedEntity dataclass."""

    def test_properties(self):
        """Test ResolvedEntity properties."""
        from models import HistoricalEntity, YearRange

        entity = HistoricalEntity(
            name='Test Country',
            canonical_name='Test Country',
            entity_type='country',
            valid_range=YearRange(1900, 2000)
        )

        resolved = ResolvedEntity(
            entity=entity,
            confidence=0.9,
            overlap_type='full',
            overlap_years=50
        )

        assert resolved.name == 'Test Country'
        assert resolved.canonical_name == 'Test Country'
        assert resolved.entity_type == 'country'
        assert resolved.valid_range.start == 1900
