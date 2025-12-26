"""
Boundary Engine for Historical Map Generation.

Translates historical entities into geopolitical boundaries.
Uses simplified world boundary templates with historical transformations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
import math
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import YearRange
from .historical_state_resolver import ResolvedState, ResolvedEntity


@dataclass
class Point:
    """A 2D point (latitude, longitude or pixel coordinates)."""
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Polygon:
    """
    A polygon representing a territory boundary.

    Attributes:
        points: List of points forming the polygon
        entity_name: Name of the entity this polygon represents
        entity_type: Type of entity (country, city, etc.)
        fill_color: Suggested fill color (hex)
        border_color: Suggested border color (hex)
        label_position: Suggested position for the label
        uncertainty: Uncertainty level for this boundary (0.0-1.0)
    """
    points: List[Point]
    entity_name: str
    entity_type: str
    fill_color: str = "#CCCCCC"
    border_color: str = "#333333"
    label_position: Optional[Point] = None
    uncertainty: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def centroid(self) -> Point:
        """Calculate the centroid of the polygon."""
        if not self.points:
            return Point(0, 0)

        sum_x = sum(p.x for p in self.points)
        sum_y = sum(p.y for p in self.points)
        n = len(self.points)
        return Point(sum_x / n, sum_y / n)

    def get_label_position(self) -> Point:
        """Get the position for labeling this polygon."""
        return self.label_position or self.centroid


@dataclass
class UncertaintyRegion:
    """
    A region with uncertain or disputed boundaries.

    Attributes:
        polygon: The approximate boundary
        reason: Why this region is uncertain
        entities_involved: Entities that might control this region
        uncertainty_level: How uncertain (0.0-1.0)
    """
    polygon: Polygon
    reason: str
    entities_involved: List[str]
    uncertainty_level: float


@dataclass
class BoundarySet:
    """
    Complete set of boundaries for a historical period.

    Attributes:
        polygons: All territory polygons
        uncertainty_regions: Regions with uncertain boundaries
        date_range: The date range these boundaries represent
        notes: Notes about boundary generation
    """
    polygons: List[Polygon]
    uncertainty_regions: List[UncertaintyRegion]
    date_range: YearRange
    notes: List[str] = field(default_factory=list)

    @property
    def country_polygons(self) -> List[Polygon]:
        """Get only country polygons."""
        return [p for p in self.polygons if p.entity_type == 'country']

    @property
    def city_markers(self) -> List[Polygon]:
        """Get city markers (point-like polygons)."""
        return [p for p in self.polygons if p.entity_type == 'city']


class BoundaryEngine:
    """
    Generates geopolitical boundaries from historical entities.

    Uses simplified boundary templates and applies historical transformations.
    When exact borders are unknown, approximates and records uncertainty.
    """

    # Simplified world regions with approximate centroids (lon, lat)
    # These serve as fallback positions when no detailed data is available
    REGION_CENTROIDS = {
        # Europe
        'Germany': (10.4, 51.2),
        'East Germany': (12.4, 52.0),
        'West Germany': (8.4, 50.5),
        'France': (2.2, 46.6),
        'United Kingdom': (-2.0, 54.0),
        'Poland': (19.4, 52.0),
        'Czechoslovakia': (15.0, 49.8),
        'Czech Republic': (15.5, 49.8),
        'Slovakia': (19.5, 48.7),
        'Austria': (14.6, 47.7),
        'Hungary': (19.5, 47.2),
        'Romania': (25.0, 46.0),
        'Bulgaria': (25.5, 42.7),
        'Yugoslavia': (19.8, 44.0),
        'Serbia': (21.0, 44.0),
        'Croatia': (16.0, 45.2),
        'Greece': (22.0, 39.0),
        'Italy': (12.5, 42.8),
        'Spain': (-3.7, 40.4),
        'Portugal': (-8.2, 39.4),
        'Netherlands': (5.3, 52.1),
        'Belgium': (4.4, 50.8),
        'Switzerland': (8.2, 46.8),
        'Sweden': (18.6, 60.1),
        'Norway': (8.5, 61.0),
        'Denmark': (9.5, 56.3),
        'Finland': (26.0, 64.0),

        # Russia/Soviet
        'Soviet Union': (60.0, 55.0),
        'USSR': (60.0, 55.0),
        'Russian Empire': (60.0, 55.0),
        'Russian Federation': (60.0, 55.0),
        'Russia': (60.0, 55.0),

        # Middle East
        'Ottoman Empire': (35.0, 39.0),
        'Turkey': (35.0, 39.0),
        'Israel': (35.0, 31.5),
        'Palestine': (35.0, 31.5),
        'Egypt': (30.0, 26.8),
        'Saudi Arabia': (45.0, 24.0),
        'Iraq': (44.0, 33.2),
        'Iran': (53.7, 32.4),
        'Persia': (53.7, 32.4),

        # Asia
        'China': (105.0, 35.0),
        'Japan': (138.3, 36.2),
        'India': (78.9, 20.6),
        'Siam': (101.0, 15.0),
        'Thailand': (101.0, 15.0),
        'Burma': (96.0, 22.0),
        'Myanmar': (96.0, 22.0),
        'Vietnam': (108.0, 14.0),
        'Ceylon': (80.8, 7.9),
        'Sri Lanka': (80.8, 7.9),

        # Africa
        'South Africa': (24.0, -29.0),
        'Egypt': (30.0, 27.0),
        'Rhodesia': (29.0, -18.0),
        'Zimbabwe': (29.0, -18.0),
        'Zaire': (23.0, -3.0),
        'Democratic Republic of Congo': (23.0, -3.0),
        'Congo': (23.0, -3.0),

        # Americas
        'United States': (-98.6, 39.8),
        'Canada': (-106.3, 56.1),
        'Mexico': (-102.5, 23.6),
        'Brazil': (-51.9, -14.2),
        'Argentina': (-63.6, -38.4),

        # Cities (marker points)
        'Constantinople': (28.98, 41.01),
        'Istanbul': (28.98, 41.01),
        'Leningrad': (30.31, 59.94),
        'St. Petersburg': (30.31, 59.94),
        'Petrograd': (30.31, 59.94),
        'Bombay': (72.88, 19.08),
        'Mumbai': (72.88, 19.08),
        'Peking': (116.41, 39.90),
        'Beijing': (116.41, 39.90),
        'Saigon': (106.66, 10.82),
        'Ho Chi Minh City': (106.66, 10.82),
    }

    # Color palette for different entity types and eras
    COLOR_PALETTE = {
        # By entity type
        'country': '#E8D4B8',
        'empire': '#D4A574',
        'territory': '#C9B896',
        'city': '#8B4513',

        # Special colors for specific entities
        'Soviet Union': '#CD5C5C',
        'USSR': '#CD5C5C',
        'East Germany': '#BC8F8F',
        'West Germany': '#B8860B',
        'Germany': '#DAA520',
        'Ottoman Empire': '#8B0000',
        'British Empire': '#DC143C',
    }

    def __init__(self):
        """Initialize the boundary engine."""
        pass

    def generate_boundaries(self, resolved_state: ResolvedState) -> BoundarySet:
        """
        Generate boundaries from resolved historical state.

        Args:
            resolved_state: The resolved historical state

        Returns:
            BoundarySet containing all generated boundaries
        """
        polygons = []
        uncertainty_regions = []
        notes = []

        # Generate polygons for dominant entities
        for entity in resolved_state.dominant_entities:
            polygon = self._create_entity_polygon(entity, resolved_state.date_range)
            if polygon:
                polygons.append(polygon)

            # Check for uncertainty
            if entity.confidence < 0.9:
                uncertainty_region = self._create_uncertainty_region(
                    entity, resolved_state.date_range
                )
                if uncertainty_region:
                    uncertainty_regions.append(uncertainty_region)

        # Add notes about generation
        notes.append(f"Generated {len(polygons)} territory polygons")
        notes.append(f"Identified {len(uncertainty_regions)} uncertain regions")

        if resolved_state.conflicts:
            notes.append(
                f"Resolved {len(resolved_state.conflicts)} entity conflicts"
            )

        # Note about approximations
        notes.append(
            "Boundaries are approximated using simplified templates. "
            "Exact historical borders may vary."
        )

        return BoundarySet(
            polygons=polygons,
            uncertainty_regions=uncertainty_regions,
            date_range=resolved_state.date_range,
            notes=notes
        )

    def _create_entity_polygon(
        self,
        entity: ResolvedEntity,
        date_range: YearRange
    ) -> Optional[Polygon]:
        """
        Create a polygon for an entity.

        Uses centroid positions and creates simplified boundary approximations.
        """
        name = entity.name
        entity_type = entity.entity_type

        # Get centroid position
        if name in self.REGION_CENTROIDS:
            lon, lat = self.REGION_CENTROIDS[name]
        elif entity.canonical_name in self.REGION_CENTROIDS:
            lon, lat = self.REGION_CENTROIDS[entity.canonical_name]
        else:
            # Unknown entity - skip or use default
            return None

        # Determine colors
        fill_color = self.COLOR_PALETTE.get(
            name,
            self.COLOR_PALETTE.get(entity_type, '#CCCCCC')
        )

        # Create polygon based on entity type
        if entity_type == 'city':
            # Cities are point markers - create small circle
            points = self._create_city_marker(lon, lat)
        elif entity_type == 'empire':
            # Empires get larger boundaries
            points = self._create_territory_polygon(lon, lat, scale=3.0)
        else:
            # Countries get standard boundaries
            points = self._create_territory_polygon(lon, lat, scale=1.5)

        return Polygon(
            points=points,
            entity_name=name,
            entity_type=entity_type,
            fill_color=fill_color,
            border_color='#333333',
            label_position=Point(lon, lat),
            uncertainty=1.0 - entity.confidence,
            metadata={
                'valid_range': [entity.valid_range.start, entity.valid_range.end],
                'canonical_name': entity.canonical_name,
                'overlap_type': entity.overlap_type
            }
        )

    def _create_territory_polygon(
        self,
        center_lon: float,
        center_lat: float,
        scale: float = 1.0
    ) -> List[Point]:
        """
        Create a simplified territory polygon around a center point.

        Uses an irregular polygon to represent approximate territory.
        This is a placeholder - real implementation would use actual border data.
        """
        # Create an irregular polygon (not a perfect circle)
        points = []
        num_vertices = 8
        base_radius = 5.0 * scale  # degrees

        for i in range(num_vertices):
            angle = (2 * math.pi * i) / num_vertices
            # Add some irregularity
            radius = base_radius * (0.8 + 0.4 * ((i % 3) / 3))
            x = center_lon + radius * math.cos(angle)
            y = center_lat + radius * math.sin(angle) * 0.7  # Flatten slightly
            points.append(Point(x, y))

        return points

    def _create_city_marker(
        self,
        lon: float,
        lat: float
    ) -> List[Point]:
        """
        Create a small marker polygon for a city.
        """
        # Small diamond shape
        size = 0.3
        return [
            Point(lon, lat + size),
            Point(lon + size, lat),
            Point(lon, lat - size),
            Point(lon - size, lat),
        ]

    def _create_uncertainty_region(
        self,
        entity: ResolvedEntity,
        date_range: YearRange
    ) -> Optional[UncertaintyRegion]:
        """
        Create an uncertainty region for a partially-confident entity.
        """
        if entity.confidence >= 0.9:
            return None

        name = entity.name

        # Get position
        if name in self.REGION_CENTROIDS:
            lon, lat = self.REGION_CENTROIDS[name]
        else:
            return None

        # Reason for uncertainty
        if entity.overlap_type == 'partial_start':
            reason = f"{name} did not exist at the start of the period"
        elif entity.overlap_type == 'partial_end':
            reason = f"{name} ceased to exist during the period"
        elif entity.overlap_type == 'contained':
            reason = f"{name} only existed for part of the period"
        else:
            reason = f"Uncertain boundaries for {name}"

        # Create uncertainty polygon (slightly larger than entity polygon)
        points = self._create_territory_polygon(lon, lat, scale=2.0)

        polygon = Polygon(
            points=points,
            entity_name=f"{name} (uncertain)",
            entity_type='uncertainty',
            fill_color='#FFFF0033',  # Semi-transparent yellow
            border_color='#FF8C00',  # Dark orange
            uncertainty=1.0 - entity.confidence
        )

        return UncertaintyRegion(
            polygon=polygon,
            reason=reason,
            entities_involved=[name],
            uncertainty_level=1.0 - entity.confidence
        )

    def get_available_regions(self) -> List[str]:
        """Get list of all regions with known centroids."""
        return list(self.REGION_CENTROIDS.keys())
