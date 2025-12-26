"""
Historical State Resolver for Map Generation.

Determines which political entities exist during a requested time period.
Integrates with the existing HistoricalKnowledgeBase.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import HistoricalEntity, YearRange
from knowledge.knowledge_base import HistoricalKnowledgeBase
from .date_parser import ParsedDateRange


@dataclass
class ResolvedEntity:
    """
    An entity resolved for a specific time period.

    Attributes:
        entity: The original HistoricalEntity
        confidence: How confidently this entity should be shown (0.0-1.0)
        overlap_type: 'full', 'partial_start', 'partial_end', or 'contained'
        overlap_years: Number of years the entity overlaps with requested range
        notes: Any special notes about this entity's status
    """
    entity: HistoricalEntity
    confidence: float
    overlap_type: str
    overlap_years: int
    notes: List[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.entity.name

    @property
    def canonical_name(self) -> str:
        return self.entity.canonical_name

    @property
    def entity_type(self) -> str:
        return self.entity.entity_type

    @property
    def valid_range(self) -> YearRange:
        return self.entity.valid_range


@dataclass
class EntityConflict:
    """
    Represents a conflict between overlapping or successor entities.

    For example, East/West Germany and unified Germany in 1990.
    """
    entities: List[ResolvedEntity]
    conflict_type: str  # 'succession', 'split', 'merger', 'disputed'
    description: str
    resolution: str  # How the conflict was resolved


@dataclass
class ResolvedState:
    """
    The complete resolved historical state for a time period.

    Attributes:
        date_range: The requested date range
        entities: List of resolved entities
        conflicts: Any entity conflicts detected
        dominant_entities: Entities preferred for display (at midpoint)
        assumptions: Assumptions made during resolution
        metadata: Additional metadata
    """
    date_range: YearRange
    entities: List[ResolvedEntity]
    conflicts: List[EntityConflict]
    dominant_entities: List[ResolvedEntity]
    assumptions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def countries(self) -> List[ResolvedEntity]:
        """Get all country entities."""
        return [e for e in self.entities if e.entity_type == 'country']

    @property
    def cities(self) -> List[ResolvedEntity]:
        """Get all city entities."""
        return [e for e in self.entities if e.entity_type == 'city']

    @property
    def empires(self) -> List[ResolvedEntity]:
        """Get all empire entities."""
        return [e for e in self.entities if e.entity_type == 'empire']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date_range': [self.date_range.start, self.date_range.end],
            'entities': [
                {
                    'name': e.name,
                    'canonical_name': e.canonical_name,
                    'entity_type': e.entity_type,
                    'valid_range': [e.valid_range.start, e.valid_range.end],
                    'confidence': e.confidence,
                    'overlap_type': e.overlap_type,
                    'notes': e.notes
                }
                for e in self.entities
            ],
            'conflicts': [
                {
                    'entities': [e.name for e in c.entities],
                    'conflict_type': c.conflict_type,
                    'description': c.description,
                    'resolution': c.resolution
                }
                for c in self.conflicts
            ],
            'dominant_entities': [e.name for e in self.dominant_entities],
            'assumptions': self.assumptions
        }


class HistoricalStateResolver:
    """
    Resolves which political entities exist during a given time period.

    Uses the existing HistoricalKnowledgeBase to look up entities
    and determines:
    - Which entities were valid during the requested period
    - How to handle partial overlaps
    - How to resolve conflicts between successor/predecessor entities
    """

    # Known successor relationships for conflict resolution
    SUCCESSION_CHAINS = {
        'Soviet Union': ['Russian Empire', 'Russian Federation'],
        'East Germany': ['Nazi Germany', 'Germany'],
        'West Germany': ['Nazi Germany', 'Germany'],
        'Germany': ['East Germany', 'West Germany', 'Nazi Germany', 'Weimar Republic'],
        'Czechoslovakia': ['Czech Republic', 'Slovakia'],
        'Yugoslavia': [],  # Complex breakup
        'Ottoman Empire': [],  # Multiple successor states
        'Siam': ['Thailand'],
        'Burma': ['Myanmar'],
        'Ceylon': ['Sri Lanka'],
        'Rhodesia': ['Zimbabwe'],
        'Zaire': ['Democratic Republic of Congo'],
        'Constantinople': ['Istanbul'],
        'Leningrad': ['St. Petersburg', 'Petrograd'],
        'Bombay': ['Mumbai'],
        'Peking': ['Beijing'],
        'Saigon': ['Ho Chi Minh City'],
    }

    def __init__(self, knowledge_base: Optional[HistoricalKnowledgeBase] = None):
        """
        Initialize the resolver.

        Args:
            knowledge_base: Optional custom knowledge base.
                           If None, uses default HistoricalKnowledgeBase.
        """
        self.kb = knowledge_base or HistoricalKnowledgeBase()

    def resolve(self, parsed_date: ParsedDateRange) -> ResolvedState:
        """
        Resolve the historical state for a given date range.

        Args:
            parsed_date: Parsed and validated date range

        Returns:
            ResolvedState containing all entities and metadata
        """
        date_range = parsed_date.year_range
        midpoint = parsed_date.midpoint
        assumptions = []

        # Get all entities that overlap with the date range
        overlapping_entities = self._get_overlapping_entities(date_range)

        # Resolve each entity with confidence and overlap info
        resolved = []
        for entity in overlapping_entities:
            resolved_entity = self._resolve_entity(entity, date_range)
            resolved.append(resolved_entity)

        # Detect conflicts
        conflicts = self._detect_conflicts(resolved, date_range)

        # Determine dominant entities (prefer midpoint validity)
        dominant = self._get_dominant_entities(resolved, midpoint)

        # Record assumptions
        if not parsed_date.is_single_year:
            assumptions.append(
                f"Using midpoint year {midpoint} to resolve entity dominance "
                f"for range {date_range}"
            )

        if conflicts:
            assumptions.append(
                f"Detected {len(conflicts)} entity conflicts; "
                f"resolved based on temporal dominance"
            )

        # Add range-specific assumptions
        assumptions.extend(self._get_range_assumptions(date_range))

        return ResolvedState(
            date_range=date_range,
            entities=resolved,
            conflicts=conflicts,
            dominant_entities=dominant,
            assumptions=assumptions,
            metadata={
                'midpoint': midpoint,
                'is_single_year': parsed_date.is_single_year,
                'entity_count': len(resolved),
                'dominant_count': len(dominant)
            }
        )

    def _get_overlapping_entities(self, date_range: YearRange) -> List[HistoricalEntity]:
        """Get all entities that overlap with the given date range."""
        overlapping = []

        for entity in self.kb.all_entities():
            if entity.valid_range.overlaps(date_range):
                overlapping.append(entity)

        return overlapping

    def _resolve_entity(
        self,
        entity: HistoricalEntity,
        date_range: YearRange
    ) -> ResolvedEntity:
        """
        Resolve a single entity for the given date range.

        Calculates confidence based on overlap type and duration.
        """
        entity_range = entity.valid_range

        # Calculate overlap
        intersection = entity_range.intersection(date_range)
        if not intersection:
            # Should not happen if we filtered correctly
            return ResolvedEntity(
                entity=entity,
                confidence=0.0,
                overlap_type='none',
                overlap_years=0,
                notes=['Entity does not overlap with requested range']
            )

        overlap_years = intersection.end - intersection.start + 1
        total_years = date_range.end - date_range.start + 1

        # Determine overlap type
        if entity_range.start <= date_range.start and entity_range.end >= date_range.end:
            overlap_type = 'full'
            confidence = 1.0
        elif entity_range.start > date_range.start and entity_range.end < date_range.end:
            overlap_type = 'contained'
            # Entity existed only during part of the range
            confidence = overlap_years / total_years
        elif entity_range.start > date_range.start:
            overlap_type = 'partial_start'
            # Entity started during the range
            confidence = 0.5 + (overlap_years / total_years) * 0.5
        else:
            overlap_type = 'partial_end'
            # Entity ended during the range
            confidence = 0.5 + (overlap_years / total_years) * 0.5

        notes = []
        if overlap_type != 'full':
            notes.append(
                f"Entity valid {entity_range.start}-{entity_range.end}, "
                f"overlaps {overlap_years} years with requested range"
            )

        return ResolvedEntity(
            entity=entity,
            confidence=confidence,
            overlap_type=overlap_type,
            overlap_years=overlap_years,
            notes=notes
        )

    def _detect_conflicts(
        self,
        resolved: List[ResolvedEntity],
        date_range: YearRange
    ) -> List[EntityConflict]:
        """
        Detect conflicts between entities (successors, splits, mergers).
        """
        conflicts = []

        # Group by canonical name to find related entities
        seen_chains = set()

        for entity in resolved:
            name = entity.name

            if name in self.SUCCESSION_CHAINS and name not in seen_chains:
                successors = self.SUCCESSION_CHAINS[name]
                related = [entity]

                for other in resolved:
                    if other.name in successors or name in self.SUCCESSION_CHAINS.get(other.name, []):
                        if other not in related:
                            related.append(other)

                if len(related) > 1:
                    # Determine conflict type
                    conflict_type = 'succession'
                    names = [e.name for e in related]

                    if 'East Germany' in names and 'West Germany' in names:
                        conflict_type = 'split'
                        description = "Germany was divided into East and West (1949-1990)"
                        resolution = "Showing both entities as they coexisted"
                    elif 'Czechoslovakia' in names and ('Czech Republic' in names or 'Slovakia' in names):
                        conflict_type = 'split'
                        description = "Czechoslovakia split into Czech Republic and Slovakia (1993)"
                        resolution = "Using dominant entity at midpoint"
                    else:
                        description = f"Succession chain: {' -> '.join(names)}"
                        resolution = "Using dominant entity at midpoint"

                    conflicts.append(EntityConflict(
                        entities=related,
                        conflict_type=conflict_type,
                        description=description,
                        resolution=resolution
                    ))

                    seen_chains.update(names)

        return conflicts

    def _get_dominant_entities(
        self,
        resolved: List[ResolvedEntity],
        midpoint: int
    ) -> List[ResolvedEntity]:
        """
        Get the dominant entities to display, preferring those valid at midpoint.
        """
        # Filter to entities valid at midpoint
        midpoint_valid = [
            e for e in resolved
            if e.entity.was_valid_in(midpoint)
        ]

        # If no midpoint-valid entities, fall back to highest confidence
        if not midpoint_valid:
            return sorted(resolved, key=lambda e: -e.confidence)[:10]

        # Sort by confidence, then by narrower range (more specific)
        def sort_key(e: ResolvedEntity) -> Tuple[float, int]:
            range_width = e.valid_range.end - e.valid_range.start
            return (-e.confidence, range_width)

        return sorted(midpoint_valid, key=sort_key)

    def _get_range_assumptions(self, date_range: YearRange) -> List[str]:
        """Get assumptions specific to certain historical periods."""
        assumptions = []
        start, end = date_range.start, date_range.end

        # WWI period
        if 1914 <= start <= 1918 or 1914 <= end <= 1918:
            assumptions.append(
                "WWI period (1914-1918): Borders were in flux; "
                "showing pre-war or post-war state based on midpoint"
            )

        # WWII period
        if 1939 <= start <= 1945 or 1939 <= end <= 1945:
            assumptions.append(
                "WWII period (1939-1945): Many borders changed during occupation; "
                "showing general political entities"
            )

        # Cold War division
        if 1949 <= start <= 1991 and 1949 <= end <= 1991:
            assumptions.append(
                "Cold War period (1949-1991): Showing divided Germany "
                "and Soviet sphere of influence"
            )

        # Decolonization era
        if 1945 <= start <= 1970:
            assumptions.append(
                "Decolonization era: Many African and Asian nations gained independence; "
                "borders may have changed rapidly"
            )

        # Soviet collapse
        if 1989 <= start <= 1993 or 1989 <= end <= 1993:
            assumptions.append(
                "Post-Soviet transition (1989-1993): Rapid changes in Eastern Europe; "
                "showing dominant entities at midpoint"
            )

        return assumptions

    def get_entities_for_year(self, year: int) -> List[HistoricalEntity]:
        """
        Convenience method to get all entities valid in a specific year.

        Args:
            year: Year to query

        Returns:
            List of HistoricalEntity objects valid in that year
        """
        return self.kb.get_entities_valid_in_year(year)
