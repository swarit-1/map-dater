"""
Probabilistic date estimation engine.

Combines multiple signals (entities, visual features, text) to estimate
when a map was created.
"""

from typing import List, Tuple, Optional
from pathlib import Path
import sys
from collections import defaultdict
import math

sys.path.append(str(Path(__file__).parent.parent))
from models import (
    DateSignal, DateEstimate, YearRange, HistoricalEntity,
    VisualFeature, SignalType
)


class DateEstimator:
    """
    Estimates map creation date from multiple signals.

    Uses a combination of:
    - Hard constraints (entity existence)
    - Soft signals (visual features, text patterns)
    - Confidence weighting
    - Probabilistic aggregation
    """

    def __init__(
        self,
        entity_weight: float = 0.7,
        visual_weight: float = 0.2,
        textual_weight: float = 0.1,
        confidence_threshold: float = 0.4
    ):
        """
        Initialize the date estimator.

        Args:
            entity_weight: Weight for entity signals
            visual_weight: Weight for visual features
            textual_weight: Weight for textual patterns
            confidence_threshold: Minimum confidence to include estimate
        """
        self.entity_weight = entity_weight
        self.visual_weight = visual_weight
        self.textual_weight = textual_weight
        self.confidence_threshold = confidence_threshold

    def estimate_date(
        self,
        entities: List[HistoricalEntity],
        visual_features: Optional[List[VisualFeature]] = None,
        extracted_years: Optional[List[int]] = None
    ) -> DateEstimate:
        """
        Estimate the creation date of a map.

        Args:
            entities: Extracted historical entities
            visual_features: Visual features (optional)
            extracted_years: Years found in text (optional)

        Returns:
            DateEstimate with range, confidence, and explanation

        Raises:
            ValueError: If no entities provided or if entities are inconsistent
        """
        if not entities:
            raise ValueError("At least one historical entity required for dating")

        visual_features = visual_features or []
        extracted_years = extracted_years or []

        # Convert inputs to signals
        signals = self._create_signals_from_entities(entities)
        signals.extend(self._create_signals_from_visual(visual_features))
        signals.extend(self._create_signals_from_years(extracted_years))

        # Find the temporal intersection
        year_range = self._compute_year_range(signals)

        if year_range is None:
            raise ValueError(
                "Conflicting signals - entities do not temporally overlap. "
                "This may indicate a composite or anachronistic map."
            )

        # Compute confidence
        confidence = self._compute_confidence(signals, year_range)

        # Find most likely year within range
        most_likely_year = self._find_most_likely_year(signals, year_range)

        return DateEstimate(
            year_range=year_range,
            confidence=confidence,
            signals=signals,
            most_likely_year=most_likely_year,
            explanation=""  # Will be filled by explanation generator
        )

    def _create_signals_from_entities(
        self,
        entities: List[HistoricalEntity]
    ) -> List[DateSignal]:
        """
        Convert historical entities to date signals.

        Args:
            entities: List of identified entities

        Returns:
            List of DateSignal objects
        """
        signals = []

        for entity in entities:
            # Entity existence is a hard constraint
            signal = DateSignal(
                signal_type=SignalType.ENTITY,
                description=f"{entity.entity_type.capitalize()}: {entity.canonical_name}",
                year_range=entity.valid_range,
                confidence=0.95,  # High confidence - entities are factual
                source=f"entity:{entity.canonical_name}",
                reasoning=(
                    f"{entity.canonical_name} existed from "
                    f"{entity.valid_range.start} to {entity.valid_range.end}"
                )
            )
            signals.append(signal)

        return signals

    def _create_signals_from_visual(
        self,
        visual_features: List[VisualFeature]
    ) -> List[DateSignal]:
        """
        Convert visual features to date signals.

        Args:
            visual_features: List of visual features

        Returns:
            List of DateSignal objects
        """
        signals = []

        for feature in visual_features:
            # Only include features with temporal information
            if feature.year_range is None:
                continue

            signal = DateSignal(
                signal_type=SignalType.VISUAL,
                description=feature.description,
                year_range=feature.year_range,
                confidence=feature.confidence,
                source=f"visual:{feature.feature_type}",
                reasoning=f"Visual analysis suggests {feature.description}"
            )
            signals.append(signal)

        return signals

    def _create_signals_from_years(
        self,
        extracted_years: List[int]
    ) -> List[DateSignal]:
        """
        Convert extracted years to date signals.

        Years found in text can indicate:
        - Publication year (if near other contextual clues)
        - Historical events referenced
        - Copyright dates

        Args:
            extracted_years: Years extracted from OCR

        Returns:
            List of DateSignal objects
        """
        signals = []

        if not extracted_years:
            return signals

        # Group nearby years
        year_groups = self._group_nearby_years(extracted_years)

        for years in year_groups:
            median_year = int(sum(years) / len(years))

            # Assume map was made within 20 years of found year
            # (could be before or after reference)
            signal = DateSignal(
                signal_type=SignalType.TEXTUAL,
                description=f"Year reference: {median_year}",
                year_range=YearRange(median_year - 10, median_year + 10),
                confidence=0.6,  # Moderate confidence
                source=f"text_year:{median_year}",
                reasoning=f"Text contains year {median_year}"
            )
            signals.append(signal)

        return signals

    def _group_nearby_years(
        self,
        years: List[int],
        threshold: int = 5
    ) -> List[List[int]]:
        """
        Group years that are close together.

        Args:
            years: List of years
            threshold: Years within this distance are grouped

        Returns:
            List of year groups
        """
        if not years:
            return []

        sorted_years = sorted(years)
        groups = []
        current_group = [sorted_years[0]]

        for year in sorted_years[1:]:
            if year - current_group[-1] <= threshold:
                current_group.append(year)
            else:
                groups.append(current_group)
                current_group = [year]

        groups.append(current_group)
        return groups

    def _compute_year_range(
        self,
        signals: List[DateSignal]
    ) -> Optional[YearRange]:
        """
        Compute the intersection of all signal year ranges.

        Args:
            signals: List of date signals

        Returns:
            Intersected year range, or None if no overlap
        """
        if not signals:
            return None

        # Start with the first signal's range
        intersection = signals[0].year_range

        # Intersect with each subsequent signal
        # Weight by confidence: only use high-confidence signals for hard constraints
        high_confidence_signals = [
            s for s in signals
            if s.confidence >= 0.7 or s.signal_type == SignalType.ENTITY
        ]

        if high_confidence_signals:
            intersection = high_confidence_signals[0].year_range

            for signal in high_confidence_signals[1:]:
                new_intersection = intersection.intersection(signal.year_range)
                if new_intersection is None:
                    # Check if it's just a slight mismatch
                    # Allow some flexibility for low-confidence signals
                    continue
                intersection = new_intersection

        return intersection

    def _compute_confidence(
        self,
        signals: List[DateSignal],
        year_range: YearRange
    ) -> float:
        """
        Compute overall confidence in the date estimate.

        Factors:
        - Number of signals
        - Agreement between signals
        - Individual signal confidences
        - Range narrowness (narrower = more confident)

        Args:
            signals: List of date signals
            year_range: Estimated year range

        Returns:
            Confidence score (0-1)
        """
        if not signals:
            return 0.0

        # Factor 1: Average signal confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        # Factor 2: Number of signals (more is better, with diminishing returns)
        signal_factor = min(1.0, len(signals) / 5.0)

        # Factor 3: Range narrowness
        range_width = year_range.end - year_range.start
        if range_width == 0:
            narrowness_factor = 1.0
        else:
            # Penalize very wide ranges
            narrowness_factor = 1.0 / (1.0 + math.log10(range_width + 1))

        # Factor 4: Signal type diversity
        signal_types = set(s.signal_type for s in signals)
        diversity_factor = min(1.0, len(signal_types) / 2.0)

        # Weighted combination
        confidence = (
            0.4 * avg_confidence +
            0.2 * signal_factor +
            0.2 * narrowness_factor +
            0.2 * diversity_factor
        )

        return min(1.0, max(0.0, confidence))

    def _find_most_likely_year(
        self,
        signals: List[DateSignal],
        year_range: YearRange
    ) -> int:
        """
        Find the most likely specific year within the range.

        Uses a voting mechanism weighted by signal confidence.

        Args:
            signals: List of date signals
            year_range: Valid year range

        Returns:
            Most likely year
        """
        # Create a probability distribution over the range
        year_scores = defaultdict(float)

        for signal in signals:
            # Add votes for each year in the signal's range
            for year in range(
                max(signal.year_range.start, year_range.start),
                min(signal.year_range.end, year_range.end) + 1
            ):
                # Weight by confidence and distance from signal center
                signal_center = (signal.year_range.start + signal.year_range.end) / 2
                distance_factor = 1.0 / (1.0 + abs(year - signal_center) / 10.0)
                year_scores[year] += signal.confidence * distance_factor

        if not year_scores:
            # Fallback to midpoint
            return (year_range.start + year_range.end) // 2

        # Return year with highest score
        most_likely = max(year_scores.items(), key=lambda x: x[1])
        return most_likely[0]

    def analyze_signal_conflicts(
        self,
        signals: List[DateSignal]
    ) -> List[Tuple[DateSignal, DateSignal]]:
        """
        Identify pairs of conflicting signals.

        Args:
            signals: List of date signals

        Returns:
            List of conflicting signal pairs
        """
        conflicts = []

        for i, signal1 in enumerate(signals):
            for signal2 in signals[i+1:]:
                if not signal1.year_range.overlaps(signal2.year_range):
                    conflicts.append((signal1, signal2))

        return conflicts
