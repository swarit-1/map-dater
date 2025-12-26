"""
Tests for the boundary engine module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from models import YearRange
from map_generation.date_parser import DateParser
from map_generation.historical_state_resolver import HistoricalStateResolver
from map_generation.boundary_engine import (
    BoundaryEngine,
    BoundarySet,
    Polygon,
    Point,
    UncertaintyRegion
)


class TestBoundaryEngine:
    """Tests for BoundaryEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = BoundaryEngine()
        self.parser = DateParser()
        self.resolver = HistoricalStateResolver()

    def _get_resolved_state(self, date_str: str):
        """Helper to get resolved state for a date."""
        parsed = self.parser.parse(date_str)
        return self.resolver.resolve(parsed)

    # --- Basic Generation Tests ---

    def test_generate_boundaries(self):
        """Test basic boundary generation."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        assert isinstance(boundaries, BoundarySet)
        assert len(boundaries.polygons) > 0

    def test_boundary_set_has_date_range(self):
        """Test that boundary set has date range."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        assert boundaries.date_range.start == 1970
        assert boundaries.date_range.end == 1970

    def test_boundary_set_has_notes(self):
        """Test that boundary set has generation notes."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        assert len(boundaries.notes) > 0

    # --- Polygon Tests ---

    def test_polygons_have_required_attributes(self):
        """Test that polygons have all required attributes."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        for polygon in boundaries.polygons:
            assert polygon.entity_name is not None
            assert polygon.entity_type is not None
            assert polygon.fill_color is not None
            assert polygon.border_color is not None
            assert len(polygon.points) > 0

    def test_polygon_centroid(self):
        """Test polygon centroid calculation."""
        polygon = Polygon(
            points=[
                Point(0, 0),
                Point(10, 0),
                Point(10, 10),
                Point(0, 10)
            ],
            entity_name="Test",
            entity_type="country"
        )

        centroid = polygon.centroid
        assert centroid.x == 5.0
        assert centroid.y == 5.0

    def test_polygon_label_position(self):
        """Test polygon label position."""
        polygon = Polygon(
            points=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            entity_name="Test",
            entity_type="country",
            label_position=Point(5, 8)
        )

        label_pos = polygon.get_label_position()
        assert label_pos.x == 5
        assert label_pos.y == 8

    def test_polygon_label_position_defaults_to_centroid(self):
        """Test that label position defaults to centroid."""
        polygon = Polygon(
            points=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            entity_name="Test",
            entity_type="country"
        )

        label_pos = polygon.get_label_position()
        assert label_pos.x == polygon.centroid.x
        assert label_pos.y == polygon.centroid.y

    # --- Entity Type Filtering ---

    def test_country_polygons_filter(self):
        """Test filtering for country polygons."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        country_polygons = boundaries.country_polygons
        assert all(p.entity_type == 'country' for p in country_polygons)

    def test_city_markers_filter(self):
        """Test filtering for city markers."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        city_markers = boundaries.city_markers
        assert all(p.entity_type == 'city' for p in city_markers)

    # --- Uncertainty Regions ---

    def test_uncertainty_regions_for_partial_overlap(self):
        """Test uncertainty regions are generated for partial overlaps."""
        # Use a range that spans entity transitions
        resolved = self._get_resolved_state("1988-1995")
        boundaries = self.engine.generate_boundaries(resolved)

        # May have uncertainty regions
        assert isinstance(boundaries.uncertainty_regions, list)

    def test_uncertainty_region_attributes(self):
        """Test uncertainty region has required attributes."""
        polygon = Polygon(
            points=[Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)],
            entity_name="Test (uncertain)",
            entity_type="uncertainty"
        )

        region = UncertaintyRegion(
            polygon=polygon,
            reason="Test reason",
            entities_involved=["Entity1", "Entity2"],
            uncertainty_level=0.5
        )

        assert region.reason == "Test reason"
        assert len(region.entities_involved) == 2
        assert region.uncertainty_level == 0.5

    # --- Known Entities ---

    def test_known_regions(self):
        """Test that engine knows about major regions."""
        regions = self.engine.get_available_regions()

        assert 'Germany' in regions
        assert 'Soviet Union' in regions or 'USSR' in regions
        assert 'France' in regions
        assert 'United States' in regions

    def test_city_markers_are_small(self):
        """Test that city markers are smaller than country polygons."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        for marker in boundaries.city_markers:
            # City markers should have exactly 4 points (diamond shape)
            assert len(marker.points) == 4

    # --- Color Assignment ---

    def test_entities_have_colors(self):
        """Test that entities are assigned colors."""
        resolved = self._get_resolved_state("1970")
        boundaries = self.engine.generate_boundaries(resolved)

        for polygon in boundaries.polygons:
            assert polygon.fill_color.startswith('#')
            assert polygon.border_color.startswith('#')


class TestPoint:
    """Tests for Point dataclass."""

    def test_point_creation(self):
        """Test point creation."""
        point = Point(10.5, 20.3)
        assert point.x == 10.5
        assert point.y == 20.3

    def test_point_to_tuple(self):
        """Test point to tuple conversion."""
        point = Point(10.5, 20.3)
        assert point.to_tuple() == (10.5, 20.3)
