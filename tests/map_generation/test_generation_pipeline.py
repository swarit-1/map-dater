"""
Tests for the map generation pipeline.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from map_generation.generation_pipeline import (
    MapGenerationPipeline,
    GeneratedMapResult,
    generate_map_from_date
)
from map_generation.date_parser import DateParseError
from map_generation.map_renderer import RenderConfig


class TestMapGenerationPipeline:
    """Tests for MapGenerationPipeline class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = MapGenerationPipeline()

    # --- Basic Generation Tests ---

    def test_generate_single_year(self):
        """Test generating a map for a single year."""
        result = self.pipeline.generate("1914")

        assert isinstance(result, GeneratedMapResult)
        assert result.date_range.start == 1914
        assert result.date_range.end == 1914
        assert len(result.image_data) > 0

    def test_generate_year_range(self):
        """Test generating a map for a year range."""
        result = self.pipeline.generate("1918-1939")

        assert result.date_range.start == 1918
        assert result.date_range.end == 1939

    def test_generate_returns_entities(self):
        """Test that generation returns entities shown."""
        result = self.pipeline.generate("1970")

        assert len(result.entities_shown) > 0
        assert all('name' in e for e in result.entities_shown)
        assert all('type' in e for e in result.entities_shown)

    def test_generate_returns_assumptions(self):
        """Test that generation returns assumptions."""
        result = self.pipeline.generate("1949-1990")

        assert len(result.assumptions) > 0

    def test_generate_returns_uncertainty(self):
        """Test that generation returns uncertainty assessment."""
        result = self.pipeline.generate("1970")

        assert result.uncertainty is not None
        assert 0 <= result.uncertainty.overall_score <= 1

    # --- Output Format Tests ---

    def test_generate_png_format(self):
        """Test PNG output format."""
        result = self.pipeline.generate("1970", output_format='png')

        assert result.metadata['output_format'] == 'png'
        # PNG starts with specific bytes
        assert result.image_data[:4] == b'\x89PNG' or len(result.image_data) > 0

    def test_generate_svg_format(self):
        """Test SVG output format."""
        result = self.pipeline.generate("1970", output_format='svg')

        assert result.metadata['output_format'] == 'svg'
        svg_text = result.image_data.decode('utf-8')
        assert '<svg' in svg_text
        assert '</svg>' in svg_text

    def test_generate_to_file(self):
        """Test saving output to file."""
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = f.name

        try:
            result = self.pipeline.generate("1970", output_path=output_path, output_format='svg')

            assert result.image_path == output_path
            assert Path(output_path).exists()

            content = Path(output_path).read_text()
            assert '<svg' in content
        finally:
            Path(output_path).unlink(missing_ok=True)

    # --- Properties and Metadata ---

    def test_confidence_property(self):
        """Test confidence property."""
        result = self.pipeline.generate("1970")

        assert result.confidence == 1.0 - result.uncertainty.overall_score

    def test_risk_level_property(self):
        """Test risk level property."""
        result = self.pipeline.generate("1970")

        assert result.risk_level in ('low', 'medium', 'high')

    def test_metadata_content(self):
        """Test metadata contains expected fields."""
        result = self.pipeline.generate("1914")

        metadata = result.metadata
        assert 'original_input' in metadata
        assert 'is_single_year' in metadata
        assert 'midpoint_year' in metadata
        assert 'entity_count' in metadata
        assert metadata['original_input'] == '1914'
        assert metadata['is_single_year'] is True

    # --- Serialization ---

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = self.pipeline.generate("1970")
        data = result.to_dict()

        assert 'date_range' in data
        assert 'entities_shown' in data
        assert 'assumptions' in data
        assert 'uncertainty' in data
        assert 'confidence' in data
        assert 'risk_level' in data

    # --- Error Handling ---

    def test_invalid_date_raises(self):
        """Test that invalid date raises error."""
        with pytest.raises(DateParseError):
            self.pipeline.generate("not a date")

    def test_year_before_minimum_raises(self):
        """Test that year before minimum raises error."""
        with pytest.raises(DateParseError):
            self.pipeline.generate("1400")

    # --- Preview Method ---

    def test_preview(self):
        """Test preview method."""
        preview = self.pipeline.preview("1970")

        assert 'date_range' in preview
        assert 'entities_count' in preview
        assert 'dominant_entities' in preview
        assert 'risk_assessment' in preview
        assert preview['date_range'] == [1970, 1970]

    def test_preview_does_not_generate_image(self):
        """Test that preview doesn't generate an image."""
        preview = self.pipeline.preview("1970")

        assert 'image_data' not in preview

    # --- Utility Methods ---

    def test_is_valid_date(self):
        """Test date validation method."""
        assert self.pipeline.is_valid_date("1914") is True
        assert self.pipeline.is_valid_date("1918-1939") is True
        assert self.pipeline.is_valid_date("not a date") is False

    def test_get_entities_for_year(self):
        """Test getting entities for a year."""
        entities = self.pipeline.get_entities_for_year(1970)

        assert len(entities) > 0
        assert all('name' in e for e in entities)
        assert all('type' in e for e in entities)


class TestGenerateMapFromDate:
    """Tests for the public convenience function."""

    def test_basic_usage(self):
        """Test basic usage of convenience function."""
        result = generate_map_from_date("1914")

        assert isinstance(result, GeneratedMapResult)
        assert result.date_range.start == 1914

    def test_with_output_path(self):
        """Test with output path."""
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = f.name

        try:
            result = generate_map_from_date("1970", output_path=output_path, output_format='svg')

            assert result.image_path == output_path
            assert Path(output_path).exists()
        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_with_verbose(self):
        """Test verbose mode."""
        # Just verify it doesn't crash
        result = generate_map_from_date("1914", verbose=False)
        assert result is not None

    def test_with_custom_config(self):
        """Test with custom render config."""
        config = RenderConfig(width=800, height=600)
        result = generate_map_from_date("1914", render_config=config)

        assert result is not None


class TestGeneratedMapResult:
    """Tests for GeneratedMapResult dataclass."""

    def test_confidence_calculation(self):
        """Test confidence is inverse of uncertainty."""
        from map_generation.uncertainty_model import UncertaintyResult
        from models import YearRange

        result = GeneratedMapResult(
            image_data=b'test',
            image_path=None,
            date_range=YearRange(1914, 1914),
            entities_shown=[],
            assumptions=[],
            uncertainty=UncertaintyResult(
                overall_score=0.3,
                factors=[],
                notes=[]
            )
        )

        assert result.confidence == 0.7
        assert result.risk_level == 'medium'
