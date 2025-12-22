"""
Game round generation.

Creates game rounds by:
1. Selecting a map
2. Running it through the dating engine
3. Storing the system's estimate as the "answer"
"""

from typing import Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from pipeline import MapDaterPipeline
from game.game_models import GameRound, MapMetadata, DifficultyLevel
from game.map_sourcer import MapSourcer
from models import DateEstimate


class RoundGenerator:
    """
    Generates game rounds by analyzing maps and storing answers.

    Uses the map dating pipeline as the source of truth.
    """

    def __init__(
        self,
        pipeline: Optional[MapDaterPipeline] = None,
        map_sourcer: Optional[MapSourcer] = None
    ):
        """
        Initialize round generator.

        Args:
            pipeline: Map dating pipeline (or create new one)
            map_sourcer: Map sourcer (or create new one)
        """
        self.pipeline = pipeline or MapDaterPipeline(verbose=False)
        self.map_sourcer = map_sourcer or MapSourcer()

    def generate_round(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        map_id: Optional[str] = None
    ) -> GameRound:
        """
        Generate a new game round.

        Args:
            difficulty: Difficulty level
            map_id: Optional specific map ID (otherwise random)

        Returns:
            GameRound ready for play

        Raises:
            ValueError: If no suitable map found
            RuntimeError: If map analysis fails
        """
        # Select map
        if map_id:
            map_metadata = self.map_sourcer.get_map_by_id(map_id)
            if not map_metadata:
                raise ValueError(f"Map not found: {map_id}")
        else:
            map_metadata = self.map_sourcer.get_random_map(difficulty=difficulty)
            if not map_metadata:
                raise ValueError("No maps available in catalog")

        # Validate map quality
        if not self.map_sourcer.validate_map_quality(map_metadata):
            raise ValueError(f"Map quality insufficient: {map_metadata.map_id}")

        # Run through dating pipeline
        try:
            system_estimate = self.pipeline.analyze_map(map_metadata.image_path)
        except Exception as e:
            raise RuntimeError(f"Failed to analyze map: {e}")

        # Create game round
        game_round = GameRound.create(
            map_metadata=map_metadata,
            system_estimate=system_estimate,
            difficulty=difficulty
        )

        return game_round

    def generate_round_from_local_file(
        self,
        image_path: str,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        description: Optional[str] = None
    ) -> GameRound:
        """
        Generate a game round from a local image file.

        Useful for testing or user-uploaded maps.

        Args:
            image_path: Path to image file
            difficulty: Difficulty level
            description: Optional map description

        Returns:
            GameRound ready for play
        """
        # Create temporary metadata
        map_metadata = MapMetadata(
            map_id=f"local_{Path(image_path).stem}",
            source="Local File",
            image_path=image_path,
            region="Unknown",
            description=description
        )

        # Analyze the map
        system_estimate = self.pipeline.analyze_map(image_path)

        # Create game round
        return GameRound.create(
            map_metadata=map_metadata,
            system_estimate=system_estimate,
            difficulty=difficulty
        )

    def create_mock_round(
        self,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    ) -> GameRound:
        """
        Create a mock game round for testing (no image required).

        Uses mock data from the knowledge base.

        Args:
            difficulty: Difficulty level

        Returns:
            GameRound with mock data
        """
        from knowledge import HistoricalKnowledgeBase
        from models import DateEstimate, DateSignal, SignalType, YearRange
        import uuid

        kb = HistoricalKnowledgeBase()

        # Create mock signals based on difficulty
        if difficulty == DifficultyLevel.BEGINNER:
            # Obvious signals: USSR, East Germany
            entities = [
                kb.find_by_name('USSR'),
                kb.find_by_name('East Germany')
            ]
            year_range = YearRange(1949, 1990)
            most_likely = 1970

        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Subtle signals: Constantinople (pre-1930)
            entities = [
                kb.find_by_name('USSR'),
                kb.find_by_name('Constantinople')
            ]
            year_range = YearRange(1922, 1930)
            most_likely = 1926

        else:  # EXPERT
            # Narrow window: Leningrad + East Germany
            entities = [
                kb.find_by_name('Leningrad'),
                kb.find_by_name('East Germany'),
                kb.find_by_name('Bombay')  # Pre-1995
            ]
            year_range = YearRange(1949, 1990)
            most_likely = 1970

        # Create signals
        signals = []
        for entity in entities:
            signal = DateSignal(
                signal_type=SignalType.ENTITY,
                description=f"{entity.entity_type.capitalize()}: {entity.canonical_name}",
                year_range=entity.valid_range,
                confidence=0.95,
                source=f"entity:{entity.canonical_name}",
                reasoning=f"{entity.canonical_name} existed from {entity.valid_range.start} to {entity.valid_range.end}"
            )
            signals.append(signal)

        # Create mock estimate
        estimate = DateEstimate(
            year_range=year_range,
            confidence=0.85,
            signals=signals,
            explanation="Mock estimate for testing",
            most_likely_year=most_likely
        )

        # Create mock metadata
        map_metadata = MapMetadata(
            map_id=f"mock_{uuid.uuid4().hex[:8]}",
            source="Mock Source",
            region="World",
            description=f"Mock map for {difficulty.value} difficulty"
        )

        return GameRound.create(
            map_metadata=map_metadata,
            system_estimate=estimate,
            difficulty=difficulty
        )
