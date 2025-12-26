"""
Geographic Data Fetcher for Historical Map Generation.

Fetches real historical boundary data from external APIs:
- Thenmap API (1945+): http://api.thenmap.net/v2/world-2/geo/YYYY-MM-DD
- Historical-basemaps GitHub (1492+): Raw GeoJSON files

Falls back to simplified boundaries when external data unavailable.
"""

import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import os


@dataclass
class GeoFeature:
    """A geographic feature with properties and geometry."""
    name: str
    geometry_type: str  # 'Polygon' or 'MultiPolygon'
    coordinates: List[Any]  # Nested coordinate arrays
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeoDataResult:
    """Result from fetching geographic data."""
    success: bool
    features: List[GeoFeature] = field(default_factory=list)
    source: str = "unknown"
    date_used: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GeoDataFetcher:
    """
    Fetches historical geographic boundary data from external sources.

    Primary source: Thenmap API (covers 1945-present)
    Fallback: GitHub historical-basemaps repository (covers 1492-present)
    """

    # Thenmap API configuration
    THENMAP_BASE_URL = "http://api.thenmap.net/v2"
    THENMAP_WORLD_DATASET = "world-2"
    THENMAP_MIN_YEAR = 1945

    # Historical basemaps GitHub raw URLs
    HISTORICAL_BASEMAPS_BASE = "https://raw.githubusercontent.com/aourednik/historical-basemaps/master/geojson"

    # Available years in historical-basemaps (subset - most commonly used)
    HISTORICAL_BASEMAPS_YEARS = [
        1492, 1530, 1650, 1715, 1783, 1815, 1880, 1900,
        1914, 1920, 1938, 1945, 1960, 1994, 2000
    ]

    # Cache directory for downloaded data
    CACHE_DIR = Path(__file__).parent.parent.parent / "cache" / "geo_data"

    def __init__(self, use_cache: bool = True, timeout: int = 10):
        """
        Initialize the fetcher.

        Args:
            use_cache: Whether to cache downloaded data locally
            timeout: Request timeout in seconds
        """
        self.use_cache = use_cache
        self.timeout = timeout

        if use_cache:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def fetch_boundaries_for_year(self, year: int) -> GeoDataResult:
        """
        Fetch world boundaries for a specific year.

        Automatically selects the best data source based on year.

        Args:
            year: The year to fetch boundaries for

        Returns:
            GeoDataResult with features or error information
        """
        # Try cache first
        if self.use_cache:
            cached = self._load_from_cache(year)
            if cached:
                return cached

        # Choose data source based on year
        if year >= self.THENMAP_MIN_YEAR:
            result = self._fetch_from_thenmap(year)
        else:
            result = self._fetch_from_historical_basemaps(year)

        # Cache successful results
        if result.success and self.use_cache:
            self._save_to_cache(year, result)

        return result

    def _fetch_from_thenmap(self, year: int) -> GeoDataResult:
        """Fetch boundaries from Thenmap API."""
        # Use January 1st of the year
        date_str = f"{year}-01-01"
        # Include geo_props=name to get country names in the response
        url = f"{self.THENMAP_BASE_URL}/{self.THENMAP_WORLD_DATASET}/geo/{date_str}?geo_props=name"

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'MapDater/1.0'}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))

            features = self._parse_geojson(data)

            return GeoDataResult(
                success=True,
                features=features,
                source="thenmap",
                date_used=date_str,
                metadata={"api_url": url, "feature_count": len(features)}
            )

        except urllib.error.HTTPError as e:
            return GeoDataResult(
                success=False,
                source="thenmap",
                error=f"HTTP error {e.code}: {e.reason}"
            )
        except urllib.error.URLError as e:
            return GeoDataResult(
                success=False,
                source="thenmap",
                error=f"URL error: {str(e.reason)}"
            )
        except json.JSONDecodeError as e:
            return GeoDataResult(
                success=False,
                source="thenmap",
                error=f"Invalid JSON response: {str(e)}"
            )
        except Exception as e:
            return GeoDataResult(
                success=False,
                source="thenmap",
                error=f"Unexpected error: {str(e)}"
            )

    def _fetch_from_historical_basemaps(self, year: int) -> GeoDataResult:
        """Fetch boundaries from historical-basemaps GitHub repo."""
        # Find closest available year
        closest_year = self._find_closest_year(year, self.HISTORICAL_BASEMAPS_YEARS)

        # The file naming convention in the repo
        filename = f"world_{closest_year}.geojson"
        url = f"{self.HISTORICAL_BASEMAPS_BASE}/{filename}"

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'MapDater/1.0'}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))

            features = self._parse_geojson(data)

            return GeoDataResult(
                success=True,
                features=features,
                source="historical-basemaps",
                date_used=str(closest_year),
                metadata={
                    "requested_year": year,
                    "actual_year": closest_year,
                    "github_url": url,
                    "feature_count": len(features)
                }
            )

        except urllib.error.HTTPError as e:
            # Try alternative filename patterns
            return self._try_alternative_basemap_urls(year, closest_year)
        except Exception as e:
            return GeoDataResult(
                success=False,
                source="historical-basemaps",
                error=f"Error fetching historical basemap: {str(e)}"
            )

    def _try_alternative_basemap_urls(self, year: int, closest_year: int) -> GeoDataResult:
        """Try alternative URL patterns for historical basemaps."""
        # Alternative filename patterns used in the repo
        patterns = [
            f"world_{closest_year}.geojson",
            f"world_{closest_year}AD.geojson",
            f"borders_{closest_year}.geojson",
        ]

        for pattern in patterns:
            url = f"{self.HISTORICAL_BASEMAPS_BASE}/{pattern}"
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'MapDater/1.0'}
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode('utf-8'))

                features = self._parse_geojson(data)

                return GeoDataResult(
                    success=True,
                    features=features,
                    source="historical-basemaps",
                    date_used=str(closest_year),
                    metadata={
                        "requested_year": year,
                        "actual_year": closest_year,
                        "feature_count": len(features)
                    }
                )
            except:
                continue

        return GeoDataResult(
            success=False,
            source="historical-basemaps",
            error=f"No basemap found for year {year} (tried closest: {closest_year})"
        )

    def _parse_geojson(self, data: Dict) -> List[GeoFeature]:
        """Parse GeoJSON FeatureCollection into GeoFeature objects."""
        features = []

        if data.get("type") != "FeatureCollection":
            # Try to handle single feature or geometry
            if data.get("type") == "Feature":
                data = {"type": "FeatureCollection", "features": [data]}
            else:
                return features

        for feature in data.get("features", []):
            try:
                geometry = feature.get("geometry", {})
                properties = feature.get("properties", {})

                # Extract name from various property fields
                name = (
                    properties.get("name") or
                    properties.get("NAME") or
                    properties.get("ADMIN") or
                    properties.get("sovereignt") or
                    properties.get("id", "Unknown")
                )

                geo_feature = GeoFeature(
                    name=str(name),
                    geometry_type=geometry.get("type", "Unknown"),
                    coordinates=geometry.get("coordinates", []),
                    properties=properties
                )
                features.append(geo_feature)

            except Exception:
                # Skip malformed features
                continue

        return features

    def _find_closest_year(self, target: int, available: List[int]) -> int:
        """Find the closest available year to the target."""
        if not available:
            return target

        return min(available, key=lambda x: abs(x - target))

    def _get_cache_path(self, year: int) -> Path:
        """Get the cache file path for a year."""
        return self.CACHE_DIR / f"boundaries_{year}.json"

    def _load_from_cache(self, year: int) -> Optional[GeoDataResult]:
        """Load cached data if available."""
        cache_path = self._get_cache_path(year)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            features = [
                GeoFeature(**f) for f in data.get("features", [])
            ]

            return GeoDataResult(
                success=True,
                features=features,
                source=data.get("source", "cache"),
                date_used=data.get("date_used", str(year)),
                metadata={"cached": True, **data.get("metadata", {})}
            )
        except Exception:
            return None

    def _save_to_cache(self, year: int, result: GeoDataResult) -> None:
        """Save result to cache."""
        cache_path = self._get_cache_path(year)

        try:
            data = {
                "source": result.source,
                "date_used": result.date_used,
                "metadata": result.metadata,
                "features": [
                    {
                        "name": f.name,
                        "geometry_type": f.geometry_type,
                        "coordinates": f.coordinates,
                        "properties": f.properties
                    }
                    for f in result.features
                ]
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass  # Silently fail cache writes

    def clear_cache(self) -> int:
        """Clear all cached data. Returns number of files deleted."""
        count = 0
        if self.CACHE_DIR.exists():
            for f in self.CACHE_DIR.glob("*.json"):
                try:
                    f.unlink()
                    count += 1
                except:
                    pass
        return count

    def get_available_sources(self, year: int) -> Dict[str, bool]:
        """Check which data sources are available for a year."""
        return {
            "thenmap": year >= self.THENMAP_MIN_YEAR,
            "historical_basemaps": any(
                abs(y - year) <= 50 for y in self.HISTORICAL_BASEMAPS_YEARS
            )
        }
