"""
Uncertainty Model for Historical Map Generation.

Quantifies ambiguity in generated maps due to:
- Wide date ranges
- Border disputes
- Transitional periods
- Missing historical data
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import YearRange
from .historical_state_resolver import ResolvedState, ResolvedEntity, EntityConflict
from .boundary_engine import BoundarySet


@dataclass
class UncertaintyFactor:
    """
    A single factor contributing to uncertainty.

    Attributes:
        factor_type: Category of uncertainty
        description: Human-readable description
        severity: Impact on overall uncertainty (0.0-1.0)
        affected_entities: Entities affected by this uncertainty
        recommendations: Suggested actions or caveats
    """
    factor_type: str
    description: str
    severity: float
    affected_entities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class UncertaintyResult:
    """
    Complete uncertainty assessment for a generated map.

    Attributes:
        overall_score: Overall uncertainty score (0.0-1.0, higher = more uncertain)
        factors: List of contributing uncertainty factors
        notes: Human-readable notes about uncertainty
        confidence: Inverse of uncertainty (1.0 - overall_score)
        risk_level: Categorical risk level ('low', 'medium', 'high')
    """
    overall_score: float
    factors: List[UncertaintyFactor]
    notes: List[str]

    @property
    def confidence(self) -> float:
        """Get confidence level (inverse of uncertainty)."""
        return 1.0 - self.overall_score

    @property
    def risk_level(self) -> str:
        """Get categorical risk level."""
        if self.overall_score < 0.2:
            return 'low'
        elif self.overall_score < 0.5:
            return 'medium'
        else:
            return 'high'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'uncertainty_score': self.overall_score,
            'confidence': self.confidence,
            'risk_level': self.risk_level,
            'factors': [
                {
                    'type': f.factor_type,
                    'description': f.description,
                    'severity': f.severity,
                    'affected_entities': f.affected_entities,
                    'recommendations': f.recommendations
                }
                for f in self.factors
            ],
            'notes': self.notes
        }


class UncertaintyModel:
    """
    Calculates and quantifies uncertainty in historical map generation.

    Considers multiple sources of uncertainty:
    - Temporal: Wide date ranges increase uncertainty
    - Transitional: Periods of rapid change (wars, revolutions)
    - Conflicts: Disputed territories and overlapping claims
    - Data: Missing or incomplete historical data
    """

    # Known transitional periods with high uncertainty
    TRANSITIONAL_PERIODS = [
        {
            'name': 'World War I',
            'range': (1914, 1918),
            'description': 'Borders in flux during WWI',
            'severity': 0.7
        },
        {
            'name': 'Post-WWI Settlement',
            'range': (1918, 1923),
            'description': 'New borders being established after WWI',
            'severity': 0.6
        },
        {
            'name': 'World War II',
            'range': (1939, 1945),
            'description': 'Borders changed due to occupation and conquest',
            'severity': 0.8
        },
        {
            'name': 'Post-WWII Settlement',
            'range': (1945, 1949),
            'description': 'Post-war territorial adjustments',
            'severity': 0.5
        },
        {
            'name': 'Decolonization Era',
            'range': (1945, 1975),
            'description': 'Rapid changes in Africa and Asia',
            'severity': 0.4
        },
        {
            'name': 'Soviet Collapse',
            'range': (1989, 1993),
            'description': 'Dissolution of USSR and Eastern Bloc changes',
            'severity': 0.6
        },
        {
            'name': 'Yugoslav Wars',
            'range': (1991, 2001),
            'description': 'Breakup of Yugoslavia with border conflicts',
            'severity': 0.7
        },
    ]

    # Regions with historically disputed borders
    DISPUTED_REGIONS = {
        'Kashmir': ('India', 'Pakistan'),
        'Palestine': ('Israel', 'Palestine'),
        'Alsace-Lorraine': ('France', 'Germany'),
        'Silesia': ('Germany', 'Poland'),
        'Transylvania': ('Hungary', 'Romania'),
        'Bessarabia': ('Romania', 'Moldova', 'Soviet Union'),
        'Danzig': ('Germany', 'Poland'),
        'Sudetenland': ('Germany', 'Czechoslovakia'),
    }

    def __init__(self):
        """Initialize the uncertainty model."""
        pass

    def calculate(
        self,
        resolved_state: ResolvedState,
        boundaries: BoundarySet
    ) -> UncertaintyResult:
        """
        Calculate overall uncertainty for a generated map.

        Args:
            resolved_state: The resolved historical state
            boundaries: The generated boundaries

        Returns:
            UncertaintyResult with full assessment
        """
        factors = []
        notes = []

        # Check temporal uncertainty (date range width)
        temporal_factor = self._assess_temporal_uncertainty(resolved_state)
        if temporal_factor:
            factors.append(temporal_factor)

        # Check transitional period overlap
        transitional_factors = self._assess_transitional_periods(resolved_state)
        factors.extend(transitional_factors)

        # Check entity conflicts
        conflict_factors = self._assess_conflicts(resolved_state)
        factors.extend(conflict_factors)

        # Check partial entity overlaps
        partial_factors = self._assess_partial_overlaps(resolved_state)
        factors.extend(partial_factors)

        # Check data completeness
        data_factor = self._assess_data_completeness(resolved_state, boundaries)
        if data_factor:
            factors.append(data_factor)

        # Calculate overall score (weighted average of factors)
        if factors:
            total_severity = sum(f.severity for f in factors)
            # Normalize to 0-1 range with diminishing returns for many factors
            overall_score = min(1.0, total_severity / (len(factors) + 1) + 0.1 * len(factors))
        else:
            overall_score = 0.1  # Base uncertainty

        # Generate notes
        notes = self._generate_notes(factors, resolved_state)

        return UncertaintyResult(
            overall_score=overall_score,
            factors=factors,
            notes=notes
        )

    def _assess_temporal_uncertainty(
        self,
        resolved_state: ResolvedState
    ) -> UncertaintyFactor | None:
        """Assess uncertainty from date range width."""
        date_range = resolved_state.date_range
        span = date_range.end - date_range.start + 1

        if span <= 1:
            # Single year - minimal temporal uncertainty
            return None
        elif span <= 5:
            # Small range
            return UncertaintyFactor(
                factor_type='temporal',
                description=f'Date range spans {span} years',
                severity=0.1,
                recommendations=[
                    'Consider narrowing to a specific year for more precise boundaries'
                ]
            )
        elif span <= 20:
            # Medium range
            return UncertaintyFactor(
                factor_type='temporal',
                description=f'Date range spans {span} years; borders may have changed',
                severity=0.25,
                recommendations=[
                    'Map shows dominant entities at midpoint of range',
                    'Some border changes may have occurred within this period'
                ]
            )
        else:
            # Wide range
            return UncertaintyFactor(
                factor_type='temporal',
                description=f'Wide date range ({span} years) increases uncertainty',
                severity=0.4,
                recommendations=[
                    'Significant geopolitical changes likely occurred',
                    'Consider generating maps for narrower time slices',
                    'Map represents approximate state at midpoint'
                ]
            )

    def _assess_transitional_periods(
        self,
        resolved_state: ResolvedState
    ) -> List[UncertaintyFactor]:
        """Assess uncertainty from overlapping transitional periods."""
        factors = []
        date_range = resolved_state.date_range

        for period in self.TRANSITIONAL_PERIODS:
            period_range = YearRange(period['range'][0], period['range'][1])

            if date_range.overlaps(period_range):
                # Calculate overlap proportion
                intersection = date_range.intersection(period_range)
                if intersection:
                    overlap_years = intersection.end - intersection.start + 1
                    total_years = date_range.end - date_range.start + 1
                    overlap_ratio = overlap_years / total_years

                    # Scale severity by overlap
                    scaled_severity = period['severity'] * min(1.0, overlap_ratio + 0.3)

                    factors.append(UncertaintyFactor(
                        factor_type='transitional',
                        description=f"{period['name']}: {period['description']}",
                        severity=scaled_severity,
                        recommendations=[
                            f"Borders during {period['name']} were in flux",
                            "Historical maps from this period may show different boundaries"
                        ]
                    ))

        return factors

    def _assess_conflicts(
        self,
        resolved_state: ResolvedState
    ) -> List[UncertaintyFactor]:
        """Assess uncertainty from entity conflicts."""
        factors = []

        for conflict in resolved_state.conflicts:
            entity_names = [e.name for e in conflict.entities]

            severity = 0.3  # Base severity for any conflict
            if conflict.conflict_type == 'split':
                severity = 0.35
            elif conflict.conflict_type == 'merger':
                severity = 0.3
            elif conflict.conflict_type == 'disputed':
                severity = 0.5

            factors.append(UncertaintyFactor(
                factor_type='conflict',
                description=conflict.description,
                severity=severity,
                affected_entities=entity_names,
                recommendations=[
                    conflict.resolution,
                    f"Entities involved: {', '.join(entity_names)}"
                ]
            ))

        return factors

    def _assess_partial_overlaps(
        self,
        resolved_state: ResolvedState
    ) -> List[UncertaintyFactor]:
        """Assess uncertainty from entities with partial temporal overlap."""
        factors = []

        partial_entities = [
            e for e in resolved_state.entities
            if e.overlap_type in ('partial_start', 'partial_end', 'contained')
        ]

        if partial_entities:
            entity_names = [e.name for e in partial_entities]
            avg_confidence = sum(e.confidence for e in partial_entities) / len(partial_entities)

            factors.append(UncertaintyFactor(
                factor_type='partial_overlap',
                description=f'{len(partial_entities)} entities only partially overlap with requested period',
                severity=0.2 + (1.0 - avg_confidence) * 0.3,
                affected_entities=entity_names,
                recommendations=[
                    'Some entities may not have existed for the entire requested period',
                    'Map shows entities at their dominant state during the period'
                ]
            ))

        return factors

    def _assess_data_completeness(
        self,
        resolved_state: ResolvedState,
        boundaries: BoundarySet
    ) -> UncertaintyFactor | None:
        """Assess uncertainty from missing or incomplete data."""
        # Check if we have very few entities for the period
        entity_count = len(resolved_state.dominant_entities)
        polygon_count = len(boundaries.polygons)

        if entity_count < 5:
            return UncertaintyFactor(
                factor_type='data',
                description=f'Limited historical data: only {entity_count} entities found',
                severity=0.3,
                recommendations=[
                    'Knowledge base may not contain all relevant entities for this period',
                    'Consider expanding the knowledge base for better coverage'
                ]
            )

        if polygon_count < entity_count * 0.5:
            return UncertaintyFactor(
                factor_type='data',
                description='Some entities could not be mapped to geographic regions',
                severity=0.2,
                recommendations=[
                    'Boundary data unavailable for some entities',
                    'Map may not show all entities mentioned'
                ]
            )

        return None

    def _generate_notes(
        self,
        factors: List[UncertaintyFactor],
        resolved_state: ResolvedState
    ) -> List[str]:
        """Generate human-readable uncertainty notes."""
        notes = []

        # Overall summary
        if not factors:
            notes.append("Low uncertainty: requested period is well-defined and stable")
        elif len(factors) == 1:
            notes.append(f"One uncertainty factor identified: {factors[0].factor_type}")
        else:
            notes.append(f"Multiple uncertainty factors identified ({len(factors)} total)")

        # Period-specific notes
        date_range = resolved_state.date_range
        midpoint = (date_range.start + date_range.end) // 2

        if date_range.start < 1700:
            notes.append(
                "Pre-1700 maps have higher uncertainty due to less precise historical records"
            )

        if any(f.factor_type == 'transitional' for f in factors):
            notes.append(
                "This period includes transitional events; borders may differ from other sources"
            )

        # Recommendations summary
        high_severity = [f for f in factors if f.severity >= 0.5]
        if high_severity:
            notes.append(
                f"High-impact factors: {', '.join(f.factor_type for f in high_severity)}"
            )

        # Data caveat
        notes.append(
            "All boundaries are approximations based on simplified templates. "
            "Consult historical atlases for precise borders."
        )

        return notes

    def get_period_risk_assessment(
        self,
        start_year: int,
        end_year: int
    ) -> Dict[str, Any]:
        """
        Quick risk assessment for a date range without full generation.

        Args:
            start_year: Start of period
            end_year: End of period

        Returns:
            Dictionary with risk assessment
        """
        date_range = YearRange(start_year, end_year)
        span = end_year - start_year + 1

        # Check transitional period overlap
        overlapping_periods = []
        for period in self.TRANSITIONAL_PERIODS:
            period_range = YearRange(period['range'][0], period['range'][1])
            if date_range.overlaps(period_range):
                overlapping_periods.append(period['name'])

        # Calculate base risk
        risk_score = 0.1  # Base risk

        # Add temporal risk
        if span > 50:
            risk_score += 0.3
        elif span > 20:
            risk_score += 0.2
        elif span > 5:
            risk_score += 0.1

        # Add transitional risk
        risk_score += 0.15 * len(overlapping_periods)

        # Cap at 1.0
        risk_score = min(1.0, risk_score)

        return {
            'date_range': [start_year, end_year],
            'span_years': span,
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score >= 0.5 else 'medium' if risk_score >= 0.2 else 'low',
            'transitional_periods': overlapping_periods,
            'recommendations': self._get_period_recommendations(date_range, overlapping_periods)
        }

    def _get_period_recommendations(
        self,
        date_range: YearRange,
        overlapping_periods: List[str]
    ) -> List[str]:
        """Generate recommendations for a date range."""
        recommendations = []

        span = date_range.end - date_range.start + 1

        if span > 20:
            recommendations.append(
                f"Consider generating separate maps for smaller time periods within {date_range}"
            )

        if overlapping_periods:
            recommendations.append(
                f"Period overlaps with: {', '.join(overlapping_periods)}. "
                "Expect higher uncertainty in affected regions."
            )

        if date_range.start < 1700:
            recommendations.append(
                "Historical borders before 1700 are less precisely documented"
            )

        if not recommendations:
            recommendations.append(
                "Period appears relatively stable with good historical documentation"
            )

        return recommendations
