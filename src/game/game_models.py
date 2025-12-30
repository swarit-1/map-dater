"""
Core data models for the map dating game.

Defines game rounds, user guesses, results, and difficulty levels.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
import sys
import uuid

sys.path.append(str(Path(__file__).parent.parent))
from models import DateEstimate, YearRange, DateSignal


class DifficultyLevel(Enum):
    """Difficulty tiers for map dating challenges."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    GEOGRAPHIC_GOD = "geographic_god"


# Difficulty configuration for scoring
DIFFICULTY_CONFIG = {
    DifficultyLevel.BEGINNER: {
        "tolerance_years": 20,  # Within 20 years for full accuracy bonus
        "base_multiplier": 1.0,
        "description": "Obvious historical markers (Cold War divisions, major empires)",
    },
    DifficultyLevel.INTERMEDIATE: {
        "tolerance_years": 10,  # Within 10 years for full accuracy bonus
        "base_multiplier": 1.25,
        "description": "Requires knowledge of interwar period and decolonization",
    },
    DifficultyLevel.ADVANCED: {
        "tolerance_years": 5,  # Within 5 years for full accuracy bonus
        "base_multiplier": 1.5,
        "description": "Transitional periods with subtle boundary changes",
    },
    DifficultyLevel.GEOGRAPHIC_GOD: {
        "tolerance_years": 2,  # Within 2 years for full accuracy bonus
        "base_multiplier": 2.0,
        "description": "Specific treaty years, short-lived states, obscure changes",
    },
}


@dataclass
class MapMetadata:
    """Metadata about a source map."""
    map_id: str
    source: str  # "Library of Congress", "British Library", etc.
    url: Optional[str] = None
    region: str = "Unknown"
    known_date: Optional[int] = None  # Avoid using this for validation
    image_path: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def create_mock(cls, map_id: Optional[str] = None) -> 'MapMetadata':
        """Create a mock map for testing."""
        return cls(
            map_id=map_id or str(uuid.uuid4()),
            source="Mock Source",
            region="World"
        )


@dataclass
class UserGuess:
    """A user's guess for when a map was created."""

    # The guess can be a single year or a range
    year: Optional[int] = None
    year_range: Optional[YearRange] = None

    def __post_init__(self):
        """Validate that exactly one guess type is provided."""
        if self.year is None and self.year_range is None:
            raise ValueError("Must provide either year or year_range")

        if self.year is not None and self.year_range is not None:
            raise ValueError("Cannot provide both year and year_range")

    def to_range(self) -> YearRange:
        """
        Convert the guess to a year range for comparison.

        Single years are converted to single-year ranges.
        """
        if self.year_range is not None:
            return self.year_range
        else:
            return YearRange(self.year, self.year)

    def is_point_guess(self) -> bool:
        """Check if this is a single-year guess."""
        return self.year is not None

    def get_width(self) -> int:
        """Get the width of the guess range."""
        guess_range = self.to_range()
        return guess_range.end - guess_range.start

    def __repr__(self) -> str:
        if self.year is not None:
            return f"UserGuess(year={self.year})"
        else:
            return f"UserGuess(range={self.year_range})"


@dataclass
class GameRound:
    """
    A single round of the map dating game.

    Contains the map, system's answer, and difficulty settings.
    """
    round_id: str
    map_metadata: MapMetadata
    system_estimate: DateEstimate
    difficulty: DifficultyLevel
    created_at: float = field(default_factory=lambda: __import__('time').time())

    # Hidden answer (not revealed until after guess)
    _answer_range: YearRange = field(init=False)
    _confidence: float = field(init=False)
    _key_signals: List[DateSignal] = field(init=False)

    def __post_init__(self):
        """Extract key information from the system estimate."""
        self._answer_range = self.system_estimate.year_range
        self._confidence = self.system_estimate.confidence

        # Extract most important signals (highest confidence)
        sorted_signals = sorted(
            self.system_estimate.signals,
            key=lambda s: s.confidence,
            reverse=True
        )
        self._key_signals = sorted_signals[:5]  # Top 5 signals

    def get_answer_range(self) -> YearRange:
        """Get the system's estimated range."""
        return self._answer_range

    def get_confidence(self) -> float:
        """Get the system's confidence."""
        return self._confidence

    def get_key_signals(self) -> List[DateSignal]:
        """Get the most important dating signals."""
        return self._key_signals

    @classmethod
    def create(
        cls,
        map_metadata: MapMetadata,
        system_estimate: DateEstimate,
        difficulty: DifficultyLevel
    ) -> 'GameRound':
        """Create a new game round."""
        return cls(
            round_id=str(uuid.uuid4()),
            map_metadata=map_metadata,
            system_estimate=system_estimate,
            difficulty=difficulty
        )


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of how a score was calculated."""
    base_score: float  # 0-100
    accuracy_bonus: float = 0.0
    confidence_penalty: float = 0.0
    difficulty_multiplier: float = 1.0
    final_score: float = 0.0

    # Metrics
    overlap_percentage: float = 0.0
    guess_width: int = 0
    years_off: int = 0  # Distance from system's most likely year

    def __post_init__(self):
        """Calculate final score."""
        self.final_score = (
            (self.base_score + self.accuracy_bonus - self.confidence_penalty)
            * self.difficulty_multiplier
        )
        self.final_score = max(0.0, min(100.0, self.final_score))


@dataclass
class GameResult:
    """
    Result of a game round after the user guesses.

    Contains score, feedback, and educational content.
    """
    round_id: str
    user_guess: UserGuess
    system_estimate: DateEstimate
    score: ScoreBreakdown
    feedback: str  # Educational feedback text

    # Analysis
    correct_signals: List[DateSignal] = field(default_factory=list)
    missed_signals: List[DateSignal] = field(default_factory=list)

    # Performance
    was_accurate: bool = False  # Did guess overlap with answer?
    was_exact: bool = False  # Within 5 years of most likely year?
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER

    def get_summary(self) -> str:
        """Get a one-line summary of performance."""
        if self.was_exact:
            return f"🎯 Excellent! Score: {self.score.final_score:.0f}/100"
        elif self.was_accurate:
            return f"✓ Good guess! Score: {self.score.final_score:.0f}/100"
        else:
            return f"❌ Try again. Score: {self.score.final_score:.0f}/100"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'round_id': self.round_id,
            'user_guess': str(self.user_guess),
            'system_estimate': {
                'range': str(self.system_estimate.year_range),
                'most_likely': self.system_estimate.most_likely_year,
                'confidence': self.system_estimate.confidence
            },
            'score': {
                'final': self.score.final_score,
                'base': self.score.base_score,
                'years_off': self.score.years_off,
                'overlap_pct': self.score.overlap_percentage
            },
            'performance': {
                'accurate': self.was_accurate,
                'exact': self.was_exact,
                'difficulty': self.difficulty.value
            },
            'feedback': self.feedback
        }


@dataclass
class PlayerStats:
    """Track player performance over time."""
    player_id: str
    rounds_played: int = 0
    total_score: float = 0.0

    # Accuracy metrics
    accurate_guesses: int = 0
    exact_guesses: int = 0

    # Difficulty progression
    beginner_rounds: int = 0
    intermediate_rounds: int = 0
    expert_rounds: int = 0

    # Learning metrics
    avg_years_off: float = 0.0
    frequently_missed_signals: Dict[str, int] = field(default_factory=dict)

    def get_average_score(self) -> float:
        """Get average score across all rounds."""
        if self.rounds_played == 0:
            return 0.0
        return self.total_score / self.rounds_played

    def get_accuracy_rate(self) -> float:
        """Get percentage of accurate guesses."""
        if self.rounds_played == 0:
            return 0.0
        return (self.accurate_guesses / self.rounds_played) * 100

    def get_suggested_difficulty(self) -> DifficultyLevel:
        """Suggest next difficulty based on performance."""
        accuracy = self.get_accuracy_rate()
        avg_score = self.get_average_score()

        # Need at least 3 rounds to recommend intermediate
        if self.rounds_played < 3:
            return DifficultyLevel.BEGINNER

        # Promote to intermediate if doing well at beginner
        if self.beginner_rounds >= 3 and accuracy >= 70 and avg_score >= 60:
            return DifficultyLevel.INTERMEDIATE

        # Promote to expert if doing well at intermediate
        if self.intermediate_rounds >= 5 and accuracy >= 60 and avg_score >= 50:
            return DifficultyLevel.EXPERT

        # Stay at current level
        if self.expert_rounds > 0:
            return DifficultyLevel.EXPERT
        elif self.intermediate_rounds > 0:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER

    def update_with_result(self, result: GameResult):
        """Update stats with a new game result."""
        self.rounds_played += 1
        self.total_score += result.score.final_score

        if result.was_accurate:
            self.accurate_guesses += 1

        if result.was_exact:
            self.exact_guesses += 1

        # Track by difficulty
        if result.difficulty == DifficultyLevel.BEGINNER:
            self.beginner_rounds += 1
        elif result.difficulty == DifficultyLevel.INTERMEDIATE:
            self.intermediate_rounds += 1
        else:
            self.expert_rounds += 1

        # Update average years off
        prev_total = self.avg_years_off * (self.rounds_played - 1)
        self.avg_years_off = (prev_total + result.score.years_off) / self.rounds_played

        # Track missed signals
        for signal in result.missed_signals:
            key = signal.description
            self.frequently_missed_signals[key] = (
                self.frequently_missed_signals.get(key, 0) + 1
            )
