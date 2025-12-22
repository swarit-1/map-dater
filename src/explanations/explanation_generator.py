"""
Human-readable explanation generation.

Converts date estimates and signals into clear, justifiable explanations
suitable for academic or museum contexts.
"""

from typing import List, Dict
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from models import DateEstimate, DateSignal, SignalType


class ExplanationGenerator:
    """
    Generates human-readable explanations for date estimates.

    Prioritizes:
    - Clarity for non-technical users
    - Traceable reasoning
    - Highlighting key evidence
    - Acknowledging uncertainty
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the explanation generator.

        Args:
            verbose: Whether to include detailed technical information
        """
        self.verbose = verbose

    def generate_explanation(self, estimate: DateEstimate) -> str:
        """
        Generate a complete explanation for a date estimate.

        Args:
            estimate: DateEstimate to explain

        Returns:
            Human-readable explanation string
        """
        parts = []

        # Header with main estimate
        parts.append(self._format_header(estimate))

        # Evidence summary
        parts.append(self._format_evidence_summary(estimate.signals))

        # Detailed evidence
        parts.append(self._format_detailed_evidence(estimate.signals))

        # Confidence explanation
        parts.append(self._format_confidence_explanation(estimate))

        # Caveats and limitations
        if self.verbose:
            parts.append(self._format_caveats(estimate))

        return '\n\n'.join(parts)

    def _format_header(self, estimate: DateEstimate) -> str:
        """Format the main estimate header."""
        if estimate.year_range.start == estimate.year_range.end:
            date_str = f"{estimate.year_range.start}"
        else:
            date_str = f"{estimate.year_range.start}-{estimate.year_range.end}"

        confidence_pct = int(estimate.confidence * 100)

        return (
            f"ESTIMATED DATE: {date_str}\n"
            f"Most likely year: {estimate.most_likely_year}\n"
            f"Confidence: {confidence_pct}% ({self._confidence_label(estimate.confidence)})"
        )

    def _confidence_label(self, confidence: float) -> str:
        """Convert confidence score to qualitative label."""
        if confidence >= 0.9:
            return "very high"
        elif confidence >= 0.75:
            return "high"
        elif confidence >= 0.6:
            return "moderate"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very low"

    def _format_evidence_summary(self, signals: List[DateSignal]) -> str:
        """Format a summary of evidence types."""
        by_type = self._group_signals_by_type(signals)

        lines = ["EVIDENCE SUMMARY:"]

        if SignalType.ENTITY in by_type:
            count = len(by_type[SignalType.ENTITY])
            lines.append(f"  - {count} historical entit{'y' if count == 1 else 'ies'}")

        if SignalType.TEXTUAL in by_type:
            count = len(by_type[SignalType.TEXTUAL])
            lines.append(f"  - {count} textual reference{'s' if count != 1 else ''}")

        if SignalType.VISUAL in by_type:
            count = len(by_type[SignalType.VISUAL])
            lines.append(f"  - {count} visual feature{'s' if count != 1 else ''}")

        return '\n'.join(lines)

    def _format_detailed_evidence(self, signals: List[DateSignal]) -> str:
        """Format detailed evidence with reasoning."""
        # Sort by confidence (highest first)
        sorted_signals = sorted(signals, key=lambda s: s.confidence, reverse=True)

        lines = ["DETAILED EVIDENCE:"]

        for i, signal in enumerate(sorted_signals, 1):
            year_str = str(signal.year_range)
            conf_pct = int(signal.confidence * 100)

            # Format based on signal type
            if signal.signal_type == SignalType.ENTITY:
                icon = "→"
            elif signal.signal_type == SignalType.TEXTUAL:
                icon = "📝"
            elif signal.signal_type == SignalType.VISUAL:
                icon = "👁"
            else:
                icon = "•"

            lines.append(
                f"  {i}. {icon} {signal.description}"
            )
            lines.append(
                f"     Range: {year_str} (confidence: {conf_pct}%)"
            )
            lines.append(
                f"     Reasoning: {signal.reasoning}"
            )

        return '\n'.join(lines)

    def _format_confidence_explanation(self, estimate: DateEstimate) -> str:
        """Explain why the confidence is what it is."""
        lines = ["CONFIDENCE ANALYSIS:"]

        # Range width
        range_width = estimate.year_range.end - estimate.year_range.start
        if range_width == 0:
            lines.append("  ✓ Precise: Signals agree on specific year")
        elif range_width <= 10:
            lines.append(f"  ✓ Narrow range: {range_width} year window")
        elif range_width <= 30:
            lines.append(f"  ⚠ Moderate range: {range_width} year window")
        else:
            lines.append(f"  ⚠ Wide range: {range_width} year window suggests uncertainty")

        # Signal count
        entity_count = sum(1 for s in estimate.signals if s.signal_type == SignalType.ENTITY)
        if entity_count >= 3:
            lines.append(f"  ✓ Multiple entities ({entity_count}) provide cross-validation")
        elif entity_count == 1:
            lines.append("  ⚠ Single entity - limited temporal constraints")

        # Signal agreement
        avg_confidence = sum(s.confidence for s in estimate.signals) / len(estimate.signals)
        if avg_confidence >= 0.8:
            lines.append("  ✓ High-confidence signals")
        elif avg_confidence < 0.5:
            lines.append("  ⚠ Low-confidence signals reduce certainty")

        return '\n'.join(lines)

    def _format_caveats(self, estimate: DateEstimate) -> str:
        """Format caveats and limitations."""
        lines = ["CAVEATS:"]

        # Check for visual features
        has_visual = any(s.signal_type == SignalType.VISUAL for s in estimate.signals)
        if not has_visual:
            lines.append(
                "  • Visual analysis not yet implemented - "
                "estimate based solely on textual evidence"
            )

        # Check for conflicts
        conflicts = self._find_conflicts(estimate.signals)
        if conflicts:
            lines.append(
                f"  • {len(conflicts)} conflicting signal pair(s) detected - "
                "map may be composite or anachronistic"
            )

        # Range-based caveats
        range_width = estimate.year_range.end - estimate.year_range.start
        if range_width > 50:
            lines.append(
                "  • Wide date range suggests limited constraining evidence"
            )

        return '\n'.join(lines)

    def _group_signals_by_type(
        self,
        signals: List[DateSignal]
    ) -> Dict[SignalType, List[DateSignal]]:
        """Group signals by their type."""
        grouped = {}
        for signal in signals:
            if signal.signal_type not in grouped:
                grouped[signal.signal_type] = []
            grouped[signal.signal_type].append(signal)
        return grouped

    def _find_conflicts(self, signals: List[DateSignal]) -> List[tuple]:
        """Find pairs of non-overlapping signals."""
        conflicts = []
        for i, s1 in enumerate(signals):
            for s2 in signals[i+1:]:
                if not s1.year_range.overlaps(s2.year_range):
                    conflicts.append((s1, s2))
        return conflicts

    def generate_short_summary(self, estimate: DateEstimate) -> str:
        """
        Generate a brief one-line summary.

        Useful for UI display or quick reference.

        Args:
            estimate: DateEstimate to summarize

        Returns:
            One-line summary string
        """
        date_str = str(estimate.year_range)
        conf_pct = int(estimate.confidence * 100)
        entity_count = sum(
            1 for s in estimate.signals
            if s.signal_type == SignalType.ENTITY
        )

        return (
            f"Estimated {date_str} ({conf_pct}% confidence) "
            f"based on {entity_count} historical entit{'y' if entity_count == 1 else 'ies'}"
        )

    def generate_json_explanation(self, estimate: DateEstimate) -> dict:
        """
        Generate machine-readable explanation.

        Useful for APIs or further processing.

        Args:
            estimate: DateEstimate to explain

        Returns:
            Dictionary with structured explanation
        """
        return {
            'year_range': {
                'start': estimate.year_range.start,
                'end': estimate.year_range.end,
                'display': str(estimate.year_range)
            },
            'most_likely_year': estimate.most_likely_year,
            'confidence': {
                'score': estimate.confidence,
                'percentage': int(estimate.confidence * 100),
                'label': self._confidence_label(estimate.confidence)
            },
            'signals': [
                {
                    'type': signal.signal_type.value,
                    'description': signal.description,
                    'year_range': str(signal.year_range),
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning
                }
                for signal in estimate.signals
            ],
            'evidence_counts': {
                signal_type.value: len(signals)
                for signal_type, signals in self._group_signals_by_type(estimate.signals).items()
            }
        }
