"""
Date Parser for Historical Map Generation.

Parses and validates user date input for map generation.
Supports single years and year ranges.
"""

import re
from dataclasses import dataclass
from typing import Optional
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import YearRange


# Reasonable bounds for historical map generation
MIN_YEAR = 1500  # Before this, borders become very uncertain
MAX_YEAR = 2100  # Future limit (current entities project forward)


@dataclass
class ParsedDateRange:
    """
    Represents a parsed and validated date range.

    Attributes:
        year_range: The canonical YearRange object
        original_input: The original user input string
        is_single_year: Whether the input was a single year
        midpoint: The midpoint year (for entity resolution)
    """
    year_range: YearRange
    original_input: str
    is_single_year: bool

    @property
    def midpoint(self) -> int:
        """Calculate the midpoint year for entity resolution."""
        return (self.year_range.start + self.year_range.end) // 2

    @property
    def span(self) -> int:
        """Return the number of years in the range."""
        return self.year_range.end - self.year_range.start + 1

    def __repr__(self) -> str:
        if self.is_single_year:
            return f"ParsedDateRange({self.year_range.start})"
        return f"ParsedDateRange({self.year_range.start}-{self.year_range.end})"


class DateParseError(Exception):
    """Raised when date parsing fails."""
    pass


class DateParser:
    """
    Parser for user-provided date inputs.

    Supports formats:
        - "1914" (single year)
        - "1918-1939" (range with dash)
        - "1918–1939" (range with en-dash)
        - "1918 to 1939" (range with 'to')
        - "1918 - 1939" (range with spaces)

    Validates:
        - Years are within reasonable bounds (1500-2100)
        - Start year <= end year
        - Years are not in the future (relative to current date)
    """

    # Patterns for date parsing (order matters - more specific first)
    RANGE_PATTERNS = [
        # 1918-1939, 1918–1939, 1918—1939
        r'^(\d{4})\s*[-–—]\s*(\d{4})$',
        # 1918 to 1939
        r'^(\d{4})\s+to\s+(\d{4})$',
        # 1918 through 1939
        r'^(\d{4})\s+through\s+(\d{4})$',
    ]

    SINGLE_YEAR_PATTERN = r'^(\d{4})$'

    def __init__(
        self,
        min_year: int = MIN_YEAR,
        max_year: int = MAX_YEAR,
        allow_future: bool = False
    ):
        """
        Initialize the date parser.

        Args:
            min_year: Minimum allowed year (default 1500)
            max_year: Maximum allowed year (default 2100)
            allow_future: Whether to allow years beyond current date
        """
        self.min_year = min_year
        self.max_year = max_year
        self.allow_future = allow_future

    def parse(self, date_input: str) -> ParsedDateRange:
        """
        Parse a date string into a ParsedDateRange.

        Args:
            date_input: User-provided date string

        Returns:
            ParsedDateRange with validated year range

        Raises:
            DateParseError: If the input cannot be parsed or is invalid
        """
        if not date_input or not isinstance(date_input, str):
            raise DateParseError("Date input must be a non-empty string")

        # Normalize input
        normalized = date_input.strip()

        # Try range patterns first
        for pattern in self.RANGE_PATTERNS:
            match = re.match(pattern, normalized, re.IGNORECASE)
            if match:
                start_year = int(match.group(1))
                end_year = int(match.group(2))
                return self._create_range(start_year, end_year, date_input, is_single=False)

        # Try single year pattern
        match = re.match(self.SINGLE_YEAR_PATTERN, normalized)
        if match:
            year = int(match.group(1))
            return self._create_range(year, year, date_input, is_single=True)

        # If nothing matched, provide helpful error
        raise DateParseError(
            f"Cannot parse '{date_input}'. Expected format: "
            f"'YYYY' (e.g., '1914') or 'YYYY-YYYY' (e.g., '1918-1939')"
        )

    def _create_range(
        self,
        start: int,
        end: int,
        original: str,
        is_single: bool
    ) -> ParsedDateRange:
        """
        Create and validate a ParsedDateRange.

        Args:
            start: Start year
            end: End year
            original: Original input string
            is_single: Whether this was a single year input

        Returns:
            Validated ParsedDateRange

        Raises:
            DateParseError: If validation fails
        """
        # Validate order
        if start > end:
            raise DateParseError(
                f"Invalid range: start year {start} is after end year {end}"
            )

        # Validate bounds
        if start < self.min_year:
            raise DateParseError(
                f"Year {start} is before minimum supported year {self.min_year}. "
                f"Maps before {self.min_year} have highly uncertain borders."
            )

        if end > self.max_year:
            raise DateParseError(
                f"Year {end} exceeds maximum supported year {self.max_year}"
            )

        # Check for future dates (if not allowed)
        if not self.allow_future:
            import datetime
            current_year = datetime.datetime.now().year
            if start > current_year:
                raise DateParseError(
                    f"Year {start} is in the future. "
                    f"Cannot generate speculative future maps."
                )

        # Create the YearRange and ParsedDateRange
        try:
            year_range = YearRange(start=start, end=end)
        except ValueError as e:
            raise DateParseError(f"Invalid year range: {e}")

        return ParsedDateRange(
            year_range=year_range,
            original_input=original,
            is_single_year=is_single
        )

    def is_valid(self, date_input: str) -> bool:
        """
        Check if a date input is valid without raising exceptions.

        Args:
            date_input: User-provided date string

        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse(date_input)
            return True
        except DateParseError:
            return False

    def suggest_correction(self, date_input: str) -> Optional[str]:
        """
        Attempt to suggest a corrected version of invalid input.

        Args:
            date_input: User-provided date string

        Returns:
            Suggested correction, or None if no suggestion available
        """
        if not date_input:
            return None

        normalized = date_input.strip()

        # Try to extract any 4-digit numbers
        years = re.findall(r'\d{4}', normalized)

        if len(years) == 0:
            return None
        elif len(years) == 1:
            return years[0]
        elif len(years) >= 2:
            # Take first two years found
            start = min(int(years[0]), int(years[1]))
            end = max(int(years[0]), int(years[1]))
            return f"{start}-{end}"

        return None
