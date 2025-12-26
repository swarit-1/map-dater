"""
Tests for the date parser module.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from map_generation.date_parser import DateParser, ParsedDateRange, DateParseError


class TestDateParser:
    """Tests for DateParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DateParser()

    # --- Valid Input Tests ---

    def test_parse_single_year(self):
        """Test parsing a single year."""
        result = self.parser.parse("1914")

        assert result.year_range.start == 1914
        assert result.year_range.end == 1914
        assert result.is_single_year is True
        assert result.midpoint == 1914

    def test_parse_year_range_dash(self):
        """Test parsing a year range with dash."""
        result = self.parser.parse("1918-1939")

        assert result.year_range.start == 1918
        assert result.year_range.end == 1939
        assert result.is_single_year is False
        assert result.midpoint == 1928

    def test_parse_year_range_en_dash(self):
        """Test parsing a year range with en-dash."""
        result = self.parser.parse("1918–1939")

        assert result.year_range.start == 1918
        assert result.year_range.end == 1939

    def test_parse_year_range_with_spaces(self):
        """Test parsing a year range with spaces around dash."""
        result = self.parser.parse("1918 - 1939")

        assert result.year_range.start == 1918
        assert result.year_range.end == 1939

    def test_parse_year_range_with_to(self):
        """Test parsing a year range with 'to' keyword."""
        result = self.parser.parse("1918 to 1939")

        assert result.year_range.start == 1918
        assert result.year_range.end == 1939

    def test_parse_year_range_with_through(self):
        """Test parsing a year range with 'through' keyword."""
        result = self.parser.parse("1918 through 1939")

        assert result.year_range.start == 1918
        assert result.year_range.end == 1939

    def test_parse_preserves_original_input(self):
        """Test that original input is preserved."""
        result = self.parser.parse("  1914  ")

        assert result.original_input == "  1914  "

    # --- Edge Cases ---

    def test_parse_minimum_year(self):
        """Test parsing the minimum allowed year."""
        result = self.parser.parse("1500")

        assert result.year_range.start == 1500

    def test_parse_current_year(self):
        """Test parsing the current year."""
        import datetime
        current_year = datetime.datetime.now().year

        result = self.parser.parse(str(current_year))

        assert result.year_range.start == current_year

    def test_single_year_span(self):
        """Test that single year has span of 1."""
        result = self.parser.parse("1914")

        assert result.span == 1

    def test_range_span(self):
        """Test span calculation for a range."""
        result = self.parser.parse("1918-1939")

        assert result.span == 22  # 1918 to 1939 inclusive

    # --- Invalid Input Tests ---

    def test_parse_empty_string_raises(self):
        """Test that empty string raises error."""
        with pytest.raises(DateParseError):
            self.parser.parse("")

    def test_parse_none_raises(self):
        """Test that None raises error."""
        with pytest.raises(DateParseError):
            self.parser.parse(None)

    def test_parse_invalid_format_raises(self):
        """Test that invalid format raises error."""
        with pytest.raises(DateParseError):
            self.parser.parse("not a date")

    def test_parse_year_before_minimum_raises(self):
        """Test that year before minimum raises error."""
        with pytest.raises(DateParseError) as excinfo:
            self.parser.parse("1400")

        assert "before minimum" in str(excinfo.value).lower()

    def test_parse_year_after_maximum_raises(self):
        """Test that year after maximum raises error."""
        with pytest.raises(DateParseError) as excinfo:
            self.parser.parse("2200")

        assert "exceeds maximum" in str(excinfo.value).lower()

    def test_parse_inverted_range_raises(self):
        """Test that inverted range raises error."""
        with pytest.raises(DateParseError) as excinfo:
            self.parser.parse("1939-1918")

        assert "after end year" in str(excinfo.value).lower()

    def test_parse_future_year_raises(self):
        """Test that future year raises error when not allowed."""
        import datetime
        future_year = datetime.datetime.now().year + 10

        with pytest.raises(DateParseError) as excinfo:
            self.parser.parse(str(future_year))

        assert "future" in str(excinfo.value).lower()

    def test_parse_partial_year_raises(self):
        """Test that partial year raises error."""
        with pytest.raises(DateParseError):
            self.parser.parse("191")

    # --- Configuration Tests ---

    def test_allow_future_years(self):
        """Test that future years can be allowed."""
        parser = DateParser(allow_future=True)

        result = parser.parse("2050")

        assert result.year_range.start == 2050

    def test_custom_min_year(self):
        """Test custom minimum year."""
        parser = DateParser(min_year=1800)

        with pytest.raises(DateParseError):
            parser.parse("1700")

    def test_custom_max_year(self):
        """Test custom maximum year."""
        parser = DateParser(max_year=2000, allow_future=True)

        with pytest.raises(DateParseError):
            parser.parse("2001")

    # --- Utility Methods ---

    def test_is_valid_true(self):
        """Test is_valid returns True for valid input."""
        assert self.parser.is_valid("1914") is True
        assert self.parser.is_valid("1918-1939") is True

    def test_is_valid_false(self):
        """Test is_valid returns False for invalid input."""
        assert self.parser.is_valid("not a date") is False
        assert self.parser.is_valid("") is False
        assert self.parser.is_valid("1400") is False

    def test_suggest_correction_single_year(self):
        """Test correction suggestion for single year in invalid format."""
        suggestion = self.parser.suggest_correction("year 1914 AD")

        assert suggestion == "1914"

    def test_suggest_correction_range(self):
        """Test correction suggestion for range in invalid format."""
        suggestion = self.parser.suggest_correction("between 1918 and 1939")

        assert suggestion == "1918-1939"

    def test_suggest_correction_no_suggestion(self):
        """Test no suggestion for completely invalid input."""
        suggestion = self.parser.suggest_correction("no dates here")

        assert suggestion is None


class TestParsedDateRange:
    """Tests for ParsedDateRange dataclass."""

    def test_repr_single_year(self):
        """Test string representation of single year."""
        from models import YearRange

        result = ParsedDateRange(
            year_range=YearRange(1914, 1914),
            original_input="1914",
            is_single_year=True
        )

        assert "1914" in repr(result)

    def test_repr_range(self):
        """Test string representation of range."""
        from models import YearRange

        result = ParsedDateRange(
            year_range=YearRange(1918, 1939),
            original_input="1918-1939",
            is_single_year=False
        )

        assert "1918" in repr(result)
        assert "1939" in repr(result)
