"""
Core data models for the Map Dater system.

These models define the data structures used throughout the pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class SignalType(Enum):
    """Types of dating signals that can be extracted from maps."""
    ENTITY = "entity"
    VISUAL = "visual"
    CARTOGRAPHIC = "cartographic"
    TEXTUAL = "textual"


@dataclass
class BoundingBox:
    """Represents a rectangular region in an image."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class TextBlock:
    """Extracted text with location and confidence."""
    text: str
    bbox: BoundingBox
    confidence: float
    normalized_text: str = ""


@dataclass
class YearRange:
    """Represents a temporal range with optional uncertainty."""
    start: int
    end: int

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError(f"Invalid range: {self.start} > {self.end}")

    def overlaps(self, other: 'YearRange') -> bool:
        """Check if this range overlaps with another."""
        return self.start <= other.end and other.start <= self.end

    def intersection(self, other: 'YearRange') -> Optional['YearRange']:
        """Return the intersection of two ranges, or None if they don't overlap."""
        if not self.overlaps(other):
            return None
        return YearRange(
            start=max(self.start, other.start),
            end=min(self.end, other.end)
        )

    def __repr__(self) -> str:
        if self.start == self.end:
            return f"{self.start}"
        return f"{self.start}-{self.end}"


@dataclass
class HistoricalEntity:
    """A named entity with temporal validity."""
    name: str
    canonical_name: str
    entity_type: str  # "country", "city", "region", "empire", etc.
    valid_range: YearRange
    alternative_names: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def was_valid_in(self, year: int) -> bool:
        """Check if this entity existed in a given year."""
        return self.valid_range.start <= year <= self.valid_range.end


@dataclass
class DateSignal:
    """A single piece of evidence for dating a map."""
    signal_type: SignalType
    description: str
    year_range: YearRange
    confidence: float  # 0.0 to 1.0
    source: str  # What produced this signal (e.g., "entity: USSR", "visual: border_style")
    reasoning: str  # Human-readable explanation

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class DateEstimate:
    """Final date estimation with supporting evidence."""
    year_range: YearRange
    confidence: float
    signals: List[DateSignal]
    explanation: str
    most_likely_year: int

    def __post_init__(self):
        if not (self.year_range.start <= self.most_likely_year <= self.year_range.end):
            raise ValueError(
                f"Most likely year {self.most_likely_year} not in range {self.year_range}"
            )


@dataclass
class ProcessedImage:
    """Image after preprocessing, ready for analysis."""
    image_data: Any  # numpy array
    original_path: str
    width: int
    height: int
    preprocessing_applied: List[str] = field(default_factory=list)


@dataclass
class VisualFeature:
    """Placeholder for visual features (borders, colors, etc.)."""
    feature_type: str
    description: str
    confidence: float
    year_range: Optional[YearRange] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
