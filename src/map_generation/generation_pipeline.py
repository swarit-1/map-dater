"""
Map Generation Pipeline.

Main orchestration module for generating historical maps from date input.
This is the public entry point for the map generation feature.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import YearRange
from knowledge.knowledge_base import HistoricalKnowledgeBase

from .date_parser import DateParser, ParsedDateRange, DateParseError
from .historical_state_resolver import HistoricalStateResolver, ResolvedState
from .boundary_engine import BoundaryEngine, BoundarySet
from .map_renderer import MapRenderer, RenderConfig
from .uncertainty_model import UncertaintyModel, UncertaintyResult


@dataclass
class GeneratedMapResult:
    """
    Complete result of map generation.

    Attributes:
        image_data: PNG or SVG image as bytes
        image_path: Path if saved to file, None otherwise
        date_range: The date range represented
        entities_shown: List of entities displayed on the map
        assumptions: Assumptions made during generation
        uncertainty: Uncertainty assessment
        metadata: Additional metadata about the generation
    """
    image_data: bytes
    image_path: Optional[str]
    date_range: YearRange
    entities_shown: List[Dict[str, Any]]
    assumptions: List[str]
    uncertainty: UncertaintyResult
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def confidence(self) -> float:
        """Get overall confidence (inverse of uncertainty)."""
        return self.uncertainty.confidence

    @property
    def risk_level(self) -> str:
        """Get risk level from uncertainty assessment."""
        return self.uncertainty.risk_level

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date_range': [self.date_range.start, self.date_range.end],
            'entities_shown': self.entities_shown,
            'assumptions': self.assumptions,
            'uncertainty': self.uncertainty.to_dict(),
            'confidence': self.confidence,
            'risk_level': self.risk_level,
            'image_path': self.image_path,
            'metadata': self.metadata
        }


class MapGenerationPipeline:
    """
    Main pipeline for generating historical maps from date input.

    Orchestrates:
    1. Date parsing and validation
    2. Historical state resolution
    3. Boundary generation
    4. Map rendering
    5. Uncertainty assessment

    This is the inverse of the map dating pipeline:
    - Map dating: Image -> Date estimate
    - Map generation: Date -> Image
    """

    def __init__(
        self,
        knowledge_base: Optional[HistoricalKnowledgeBase] = None,
        render_config: Optional[RenderConfig] = None,
        verbose: bool = False
    ):
        """
        Initialize the map generation pipeline.

        Args:
            knowledge_base: Optional custom knowledge base
            render_config: Optional render configuration
            verbose: Whether to print progress messages
        """
        self.knowledge_base = knowledge_base or HistoricalKnowledgeBase()
        self.render_config = render_config or RenderConfig()
        self.verbose = verbose

        # Initialize components
        self.date_parser = DateParser()
        self.state_resolver = HistoricalStateResolver(self.knowledge_base)
        self.boundary_engine = BoundaryEngine()
        self.map_renderer = MapRenderer(self.render_config)
        self.uncertainty_model = UncertaintyModel()

    def generate(
        self,
        date_input: str,
        output_path: Optional[str] = None,
        output_format: str = 'png',
        title: Optional[str] = None,
        hide_date_in_title: bool = False,
        region: Optional[str] = None
    ) -> GeneratedMapResult:
        """
        Generate a historical map from a date input.

        Args:
            date_input: Date string (e.g., "1914" or "1918-1939")
            output_path: Optional path to save the image
            output_format: 'png' or 'svg'
            title: Custom title for the map (None = auto-generate)
            hide_date_in_title: If True, use generic title without revealing the date
            region: Optional region to zoom into ('world', 'europe', 'asia', 'africa', 'americas')

        Returns:
            GeneratedMapResult with image and metadata

        Raises:
            DateParseError: If the date input is invalid
            ValueError: If generation fails
        """
        # Import region viewports
        from .map_renderer import REGION_VIEWPORTS

        # Configure viewport for region if specified
        if region and region in REGION_VIEWPORTS:
            self.render_config.viewport = REGION_VIEWPORTS[region]
            # Recreate renderer with new viewport
            self.map_renderer = MapRenderer(self.render_config)
        if self.verbose:
            print(f"Generating map for: {date_input}")

        # Step 1: Parse the date
        if self.verbose:
            print("  [1/5] Parsing date input...")
        parsed_date = self.date_parser.parse(date_input)

        if self.verbose:
            print(f"        Parsed: {parsed_date.year_range}")

        # Step 2: Resolve historical state
        if self.verbose:
            print("  [2/5] Resolving historical state...")
        resolved_state = self.state_resolver.resolve(parsed_date)

        if self.verbose:
            print(f"        Found {len(resolved_state.entities)} entities")
            print(f"        Dominant: {len(resolved_state.dominant_entities)} entities")

        # Step 3: Generate boundaries
        if self.verbose:
            print("  [3/5] Generating boundaries...")
        boundaries = self.boundary_engine.generate_boundaries(resolved_state)

        if self.verbose:
            print(f"        Generated {len(boundaries.polygons)} polygons")

        # Step 4: Calculate uncertainty
        if self.verbose:
            print("  [4/5] Calculating uncertainty...")
        uncertainty = self.uncertainty_model.calculate(resolved_state, boundaries)

        if self.verbose:
            print(f"        Uncertainty: {uncertainty.overall_score:.2f}")
            print(f"        Risk level: {uncertainty.risk_level}")

        # Step 5: Render the map
        if self.verbose:
            print("  [5/5] Rendering map...")

        # Set title - can be customized or hidden for game mode
        if title is not None:
            map_title = title
        elif hide_date_in_title:
            map_title = "Historical World Map"
        else:
            map_title = f"Historical Map: {parsed_date.year_range}"
        self.map_renderer.config.title = map_title

        if output_format.lower() == 'svg':
            image_data = self.map_renderer._render_as_svg(boundaries).encode('utf-8')
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(image_data.decode('utf-8'))
        else:
            image_data = self.map_renderer.render(boundaries, output_path)

        if self.verbose:
            if output_path:
                print(f"        Saved to: {output_path}")
            print("  Done!")

        # Compile entities shown
        entities_shown = [
            {
                'name': e.name,
                'canonical_name': e.canonical_name,
                'type': e.entity_type,
                'valid_range': [e.valid_range.start, e.valid_range.end],
                'confidence': e.confidence
            }
            for e in resolved_state.dominant_entities
        ]

        # Compile assumptions
        assumptions = resolved_state.assumptions + boundaries.notes

        return GeneratedMapResult(
            image_data=image_data,
            image_path=output_path,
            date_range=parsed_date.year_range,
            entities_shown=entities_shown,
            assumptions=assumptions,
            uncertainty=uncertainty,
            metadata={
                'original_input': date_input,
                'is_single_year': parsed_date.is_single_year,
                'midpoint_year': parsed_date.midpoint,
                'entity_count': len(resolved_state.entities),
                'dominant_count': len(resolved_state.dominant_entities),
                'polygon_count': len(boundaries.polygons),
                'conflict_count': len(resolved_state.conflicts),
                'output_format': output_format
            }
        )

    def preview(self, date_input: str) -> Dict[str, Any]:
        """
        Preview what would be generated without actually rendering.

        Useful for validation and quick uncertainty assessment.

        Args:
            date_input: Date string

        Returns:
            Dictionary with preview information
        """
        # Parse date
        parsed_date = self.date_parser.parse(date_input)

        # Resolve state
        resolved_state = self.state_resolver.resolve(parsed_date)

        # Quick uncertainty assessment
        risk_assessment = self.uncertainty_model.get_period_risk_assessment(
            parsed_date.year_range.start,
            parsed_date.year_range.end
        )

        return {
            'date_range': [parsed_date.year_range.start, parsed_date.year_range.end],
            'is_single_year': parsed_date.is_single_year,
            'midpoint': parsed_date.midpoint,
            'entities_count': len(resolved_state.entities),
            'dominant_entities': [e.name for e in resolved_state.dominant_entities],
            'conflicts': [
                {
                    'type': c.conflict_type,
                    'entities': [e.name for e in c.entities],
                    'description': c.description
                }
                for c in resolved_state.conflicts
            ],
            'risk_assessment': risk_assessment,
            'assumptions': resolved_state.assumptions
        }

    def is_valid_date(self, date_input: str) -> bool:
        """Check if a date input is valid."""
        return self.date_parser.is_valid(date_input)

    def get_entities_for_year(self, year: int) -> List[Dict[str, Any]]:
        """
        Get all known entities for a specific year.

        Args:
            year: Year to query

        Returns:
            List of entity dictionaries
        """
        entities = self.state_resolver.get_entities_for_year(year)
        return [
            {
                'name': e.name,
                'canonical_name': e.canonical_name,
                'type': e.entity_type,
                'valid_range': [e.valid_range.start, e.valid_range.end]
            }
            for e in entities
        ]


# Public convenience function
def generate_map_from_date(
    date_input: str,
    output_path: Optional[str] = None,
    output_format: str = 'png',
    verbose: bool = False,
    render_config: Optional[RenderConfig] = None,
    title: Optional[str] = None,
    hide_date_in_title: bool = False,
    region: Optional[str] = None
) -> GeneratedMapResult:
    """
    Generate a historical map from a date input.

    This is the main public entry point for the map generation feature.

    Args:
        date_input: Date string (e.g., "1914" or "1918-1939")
        output_path: Optional path to save the image
        output_format: 'png' or 'svg' (default: 'png')
        verbose: Whether to print progress messages
        render_config: Optional rendering configuration
        title: Custom title for the map (None = auto-generate)
        hide_date_in_title: If True, use generic title without revealing the date
        region: Optional region to zoom into ('world', 'europe', 'asia', 'africa', 'americas')

    Returns:
        GeneratedMapResult containing:
        - image_data: PNG or SVG bytes
        - image_path: Path if saved
        - date_range: YearRange represented
        - entities_shown: List of entities on the map
        - assumptions: List of assumptions made
        - uncertainty: UncertaintyResult with confidence/risk

    Raises:
        DateParseError: If date_input cannot be parsed

    Examples:
        >>> result = generate_map_from_date("1914")
        >>> print(result.date_range)
        1914

        >>> result = generate_map_from_date("1918-1939", output_path="interwar.png")
        >>> print(result.entities_shown)
        [{'name': 'Soviet Union', ...}, ...]

        >>> result = generate_map_from_date("1949", verbose=True, region="europe")
        Generating map for: 1949
          [1/5] Parsing date input...
          ...
    """
    pipeline = MapGenerationPipeline(
        render_config=render_config,
        verbose=verbose
    )
    return pipeline.generate(date_input, output_path, output_format, title, hide_date_in_title, region)
