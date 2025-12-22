"""
Difficulty scaling and progression management.

Determines appropriate difficulty based on player performance.
"""

from typing import Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from game.game_models import DifficultyLevel, PlayerStats, GameResult


class DifficultyManager:
    """
    Manages difficulty progression for players.

    Automatically adjusts difficulty based on performance.
    """

    # Performance thresholds for progression
    BEGINNER_TO_INTERMEDIATE = {
        'min_rounds': 3,
        'min_accuracy': 70.0,  # percentage
        'min_avg_score': 60.0
    }

    INTERMEDIATE_TO_EXPERT = {
        'min_rounds': 5,
        'min_accuracy': 60.0,
        'min_avg_score': 50.0
    }

    def __init__(self):
        """Initialize difficulty manager."""
        pass

    def recommend_difficulty(
        self,
        player_stats: PlayerStats,
        current_difficulty: Optional[DifficultyLevel] = None
    ) -> DifficultyLevel:
        """
        Recommend next difficulty level based on performance.

        Args:
            player_stats: Player's statistics
            current_difficulty: Current difficulty (optional)

        Returns:
            Recommended difficulty level
        """
        # Use player stats' built-in suggestion
        return player_stats.get_suggested_difficulty()

    def should_promote(
        self,
        player_stats: PlayerStats,
        current_difficulty: DifficultyLevel
    ) -> bool:
        """
        Check if player should be promoted to next difficulty.

        Args:
            player_stats: Player statistics
            current_difficulty: Current difficulty

        Returns:
            True if player is ready for promotion
        """
        accuracy = player_stats.get_accuracy_rate()
        avg_score = player_stats.get_average_score()

        if current_difficulty == DifficultyLevel.BEGINNER:
            return (
                player_stats.beginner_rounds >= self.BEGINNER_TO_INTERMEDIATE['min_rounds']
                and accuracy >= self.BEGINNER_TO_INTERMEDIATE['min_accuracy']
                and avg_score >= self.BEGINNER_TO_INTERMEDIATE['min_avg_score']
            )

        elif current_difficulty == DifficultyLevel.INTERMEDIATE:
            return (
                player_stats.intermediate_rounds >= self.INTERMEDIATE_TO_EXPERT['min_rounds']
                and accuracy >= self.INTERMEDIATE_TO_EXPERT['min_accuracy']
                and avg_score >= self.INTERMEDIATE_TO_EXPERT['min_avg_score']
            )

        return False

    def get_scoring_strictness(self, difficulty: DifficultyLevel) -> float:
        """
        Get scoring strictness multiplier for difficulty.

        Higher difficulty = stricter scoring.

        Args:
            difficulty: Difficulty level

        Returns:
            Strictness multiplier
        """
        strictness = {
            DifficultyLevel.BEGINNER: 0.8,  # More forgiving
            DifficultyLevel.INTERMEDIATE: 1.0,  # Standard
            DifficultyLevel.EXPERT: 1.2  # Stricter
        }

        return strictness[difficulty]

    def get_hint_count(self, difficulty: DifficultyLevel) -> int:
        """
        Get number of hints to show based on difficulty.

        Args:
            difficulty: Difficulty level

        Returns:
            Number of hints
        """
        hints = {
            DifficultyLevel.BEGINNER: 2,
            DifficultyLevel.INTERMEDIATE: 1,
            DifficultyLevel.EXPERT: 0
        }

        return hints[difficulty]

    def get_time_bonus_enabled(self, difficulty: DifficultyLevel) -> bool:
        """
        Check if time bonuses are enabled for this difficulty.

        Args:
            difficulty: Difficulty level

        Returns:
            True if time bonuses apply
        """
        # Only beginners get no time pressure
        return difficulty != DifficultyLevel.BEGINNER

    def generate_progress_report(self, player_stats: PlayerStats) -> str:
        """
        Generate a progress report for the player.

        Args:
            player_stats: Player statistics

        Returns:
            Formatted progress report
        """
        lines = []
        lines.append("=" * 50)
        lines.append("PLAYER PROGRESS REPORT")
        lines.append("=" * 50)

        # Overview
        lines.append(f"\nRounds played: {player_stats.rounds_played}")
        lines.append(f"Average score: {player_stats.get_average_score():.1f}/100")
        lines.append(f"Accuracy rate: {player_stats.get_accuracy_rate():.1f}%")

        # Difficulty breakdown
        lines.append("\nPerformance by difficulty:")
        if player_stats.beginner_rounds > 0:
            lines.append(f"  Beginner: {player_stats.beginner_rounds} rounds")
        if player_stats.intermediate_rounds > 0:
            lines.append(f"  Intermediate: {player_stats.intermediate_rounds} rounds")
        if player_stats.expert_rounds > 0:
            lines.append(f"  Expert: {player_stats.expert_rounds} rounds")

        # Recommendation
        recommended = player_stats.get_suggested_difficulty()
        lines.append(f"\nRecommended difficulty: {recommended.value.upper()}")

        # Common mistakes
        if player_stats.frequently_missed_signals:
            lines.append("\nSignals you frequently miss:")
            sorted_signals = sorted(
                player_stats.frequently_missed_signals.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for signal, count in sorted_signals[:3]:
                lines.append(f"  • {signal} (missed {count} times)")

        lines.append("\n" + "=" * 50)

        return "\n".join(lines)
