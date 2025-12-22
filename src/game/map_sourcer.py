"""
Map sourcing from public domain archives.

CURRENT: Mock implementation with local/generated maps
FUTURE: Integration with Library of Congress, British Library, David Rumsey APIs
"""

from typing import List, Optional, Dict
from pathlib import Path
import sys
import json
import uuid

sys.path.append(str(Path(__file__).parent.parent))

from game.game_models import MapMetadata, DifficultyLevel


class MapSourcer:
    """
    Sources historical maps for gameplay.

    Current implementation uses mock/local maps.
    Designed for easy extension to real archive APIs.
    """

    def __init__(self, maps_directory: Optional[str] = None):
        """
        Initialize map sourcer.

        Args:
            maps_directory: Path to directory containing map images
        """
        if maps_directory:
            self.maps_dir = Path(maps_directory)
        else:
            # Default to sample_maps directory
            self.maps_dir = Path(__file__).parent.parent.parent / 'data' / 'sample_maps'

        self.maps_dir.mkdir(parents=True, exist_ok=True)

        # Mock map catalog
        self._catalog: List[MapMetadata] = []
        self._load_catalog()

    def _load_catalog(self):
        """Load the map catalog from disk or create mock catalog."""
        catalog_path = self.maps_dir / 'catalog.json'

        if catalog_path.exists():
            with open(catalog_path, 'r') as f:
                data = json.load(f)
                self._catalog = [
                    MapMetadata(**item) for item in data
                ]
        else:
            # Create mock catalog
            self._create_mock_catalog()

    def _create_mock_catalog(self):
        """Create a mock catalog of maps for testing."""
        mock_maps = [
            {
                'map_id': 'mock_cold_war_1',
                'source': 'Mock Archive',
                'region': 'Europe',
                'description': 'Cold War era map showing USSR and divided Germany',
                'image_path': str(self.maps_dir / 'mock_map_cold_war.png'),
                'difficulty_hint': DifficultyLevel.BEGINNER.value
            },
            {
                'map_id': 'mock_post_ww1_1',
                'source': 'Mock Archive',
                'region': 'Europe',
                'description': 'Post-WWI map showing new nations like Czechoslovakia',
                'image_path': str(self.maps_dir / 'mock_map_post_ww1.png'),
                'difficulty_hint': DifficultyLevel.INTERMEDIATE.value
            },
            {
                'map_id': 'mock_modern_1',
                'source': 'Mock Archive',
                'region': 'World',
                'description': 'Modern map with current country names',
                'image_path': str(self.maps_dir / 'mock_map_modern.png'),
                'difficulty_hint': DifficultyLevel.BEGINNER.value
            },
        ]

        for mock in mock_maps:
            metadata = MapMetadata(
                map_id=mock['map_id'],
                source=mock['source'],
                region=mock['region'],
                description=mock['description'],
                image_path=mock.get('image_path')
            )
            self._catalog.append(metadata)

        # Save catalog
        self._save_catalog()

    def _save_catalog(self):
        """Save catalog to disk."""
        catalog_path = self.maps_dir / 'catalog.json'

        data = [
            {
                'map_id': m.map_id,
                'source': m.source,
                'url': m.url,
                'region': m.region,
                'known_date': m.known_date,
                'image_path': m.image_path,
                'description': m.description
            }
            for m in self._catalog
        ]

        with open(catalog_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_random_map(
        self,
        difficulty: Optional[DifficultyLevel] = None,
        region: Optional[str] = None
    ) -> Optional[MapMetadata]:
        """
        Get a random map from the catalog.

        Args:
            difficulty: Optional difficulty filter
            region: Optional region filter

        Returns:
            MapMetadata or None if no maps available
        """
        import random

        candidates = self._catalog.copy()

        # Apply filters
        if region:
            candidates = [m for m in candidates if m.region == region]

        # TODO: Filter by difficulty once we tag maps

        if not candidates:
            return None

        return random.choice(candidates)

    def get_map_by_id(self, map_id: str) -> Optional[MapMetadata]:
        """
        Get a specific map by ID.

        Args:
            map_id: Map identifier

        Returns:
            MapMetadata or None if not found
        """
        for map_meta in self._catalog:
            if map_meta.map_id == map_id:
                return map_meta

        return None

    def add_map(self, metadata: MapMetadata):
        """
        Add a new map to the catalog.

        Args:
            metadata: Map metadata
        """
        self._catalog.append(metadata)
        self._save_catalog()

    def list_maps(
        self,
        region: Optional[str] = None,
        limit: int = 10
    ) -> List[MapMetadata]:
        """
        List available maps.

        Args:
            region: Optional region filter
            limit: Maximum number to return

        Returns:
            List of MapMetadata
        """
        maps = self._catalog

        if region:
            maps = [m for m in maps if m.region == region]

        return maps[:limit]

    def get_map_count(self) -> int:
        """Get total number of maps in catalog."""
        return len(self._catalog)

    # =========================================================================
    # FUTURE: Real archive integration
    # =========================================================================

    def fetch_from_library_of_congress(
        self,
        query: str,
        max_results: int = 10
    ) -> List[MapMetadata]:
        """
        FUTURE: Fetch maps from Library of Congress API.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of MapMetadata

        TODO: Implement using LOC JSON API:
        https://www.loc.gov/collections/maps/
        """
        raise NotImplementedError(
            "Library of Congress integration not yet implemented. "
            "Design: Use LOC JSON API to search maps, "
            "filter by resolution, download images, "
            "extract metadata."
        )

    def fetch_from_david_rumsey(
        self,
        query: str,
        max_results: int = 10
    ) -> List[MapMetadata]:
        """
        FUTURE: Fetch maps from David Rumsey Map Collection.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of MapMetadata

        TODO: Implement using David Rumsey API
        """
        raise NotImplementedError(
            "David Rumsey integration not yet implemented."
        )

    def validate_map_quality(self, map_metadata: MapMetadata) -> bool:
        """
        Check if a map meets quality standards for gameplay.

        Criteria:
        - Sufficient resolution (>= 800px width)
        - Image file exists and is readable
        - Not corrupted

        Args:
            map_metadata: Map to validate

        Returns:
            True if map is suitable
        """
        if not map_metadata.image_path:
            return False

        image_path = Path(map_metadata.image_path)

        if not image_path.exists():
            return False

        # Check file size (should be > 10KB)
        if image_path.stat().st_size < 10000:
            return False

        # TODO: Check image dimensions using PIL
        # For now, assume valid

        return True
