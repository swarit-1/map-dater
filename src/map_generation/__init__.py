"""
Historical Map Generation Module.

This module provides the inverse functionality of map dating:
Given a date or date range, generate a historically accurate world map.

Main entry point:
    from src.map_generation import generate_map_from_date
    result = generate_map_from_date("1914")
"""

from .generation_pipeline import generate_map_from_date, GeneratedMapResult, MapGenerationPipeline
from .date_parser import DateParser, ParsedDateRange
from .historical_state_resolver import HistoricalStateResolver, ResolvedState
from .boundary_engine import BoundaryEngine, BoundarySet
from .map_renderer import MapRenderer
from .uncertainty_model import UncertaintyModel, UncertaintyResult
from .geo_data_fetcher import GeoDataFetcher, GeoDataResult, GeoFeature

__all__ = [
    'generate_map_from_date',
    'GeneratedMapResult',
    'MapGenerationPipeline',
    'DateParser',
    'ParsedDateRange',
    'HistoricalStateResolver',
    'ResolvedState',
    'BoundaryEngine',
    'BoundarySet',
    'MapRenderer',
    'UncertaintyModel',
    'UncertaintyResult',
    'GeoDataFetcher',
    'GeoDataResult',
    'GeoFeature',
]
