"""
Main game engine that orchestrates all components.

This is the primary interface for playing the game.
"""

from typing import Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from game.game_models import (
    GameRound, UserGuess, GameResult, DifficultyLevel, PlayerStats
)
from game.round_generator import RoundGenerator
from game.difficulty_manager import DifficultyManager
from scoring.score_calculator import ScoreCalculator
from scoring.metrics_tracker import MetricsTracker
from feedback.feedback_generator import FeedbackGenerator


class GameEngine:
    """
    Main game engine for the Map Dating Game.

    Coordinates all components to provide complete game functionality.
    """

    def __init__(
        self,
        player_id: str = "default_player",
        storage_dir: Optional[str] = None
    ):
        """
        Initialize game engine.

        Args:
            player_id: Unique player identifier
            storage_dir: Optional directory for player data storage
        """
        self.player_id = player_id

        # Initialize components
        self.round_generator = RoundGenerator()
        self.difficulty_manager = DifficultyManager()
        self.score_calculator = ScoreCalculator()
        self.metrics_tracker = MetricsTracker(storage_dir=storage_dir)

        # Load player stats
        self.player_stats = self.metrics_tracker.load_player_stats(player_id)

        # Current round
        self.current_round: Optional[GameRound] = None

    def start_new_round(
        self,
        difficulty: Optional[DifficultyLevel] = None,
        use_mock: bool = False
    ) -> GameRound:
        """
        Start a new game round.

        Args:
            difficulty: Specific difficulty (or use recommended)
            use_mock: Use mock data instead of real images

        Returns:
            GameRound ready for play
        """
        # Determine difficulty
        if difficulty is None:
            difficulty = self.player_stats.get_suggested_difficulty()

        # Generate round
        if use_mock:
            self.current_round = self.round_generator.create_mock_round(difficulty)
        else:
            self.current_round = self.round_generator.generate_round(difficulty)

        return self.current_round

    def submit_guess(
        self,
        guess: UserGuess
    ) -> GameResult:
        """
        Submit a guess for the current round.

        Args:
            guess: User's guess

        Returns:
            GameResult with score and feedback

        Raises:
            RuntimeError: If no round is active
        """
        if self.current_round is None:
            raise RuntimeError("No active round. Call start_new_round() first.")

        # Calculate score
        score = self.score_calculator.calculate_score(guess, self.current_round)

        # Check accuracy
        was_accurate = self.score_calculator.is_accurate(guess, self.current_round)
        was_exact = self.score_calculator.is_exact(guess, self.current_round)

        # Generate feedback
        feedback_gen = FeedbackGenerator(difficulty=self.current_round.difficulty)
        feedback = feedback_gen.generate_feedback(guess, self.current_round, score)

        # Identify correct and missed signals
        correct_signals = feedback_gen.identify_correct_signals(guess, self.current_round)
        missed_signals = feedback_gen.identify_missed_signals(guess, self.current_round)

        # Create result
        result = GameResult(
            round_id=self.current_round.round_id,
            user_guess=guess,
            system_estimate=self.current_round.system_estimate,
            score=score,
            feedback=feedback,
            correct_signals=correct_signals,
            missed_signals=missed_signals,
            was_accurate=was_accurate,
            was_exact=was_exact,
            difficulty=self.current_round.difficulty
        )

        # Record result and update stats
        self.metrics_tracker.record_game_result(self.player_id, result)
        self.player_stats = self.metrics_tracker.load_player_stats(self.player_id)

        # Clear current round
        self.current_round = None

        return result

    def get_player_progress(self) -> str:
        """
        Get a progress report for the player.

        Returns:
            Formatted progress report
        """
        return self.difficulty_manager.generate_progress_report(self.player_stats)

    def get_recommended_difficulty(self) -> DifficultyLevel:
        """
        Get the recommended difficulty for the next round.

        Returns:
            Recommended difficulty level
        """
        return self.player_stats.get_suggested_difficulty()

    def get_stats_summary(self) -> dict:
        """
        Get a summary of player statistics.

        Returns:
            Dictionary with key stats
        """
        return {
            'player_id': self.player_id,
            'rounds_played': self.player_stats.rounds_played,
            'average_score': self.player_stats.get_average_score(),
            'accuracy_rate': self.player_stats.get_accuracy_rate(),
            'recommended_difficulty': self.get_recommended_difficulty().value
        }

    def reset_progress(self):
        """Reset player progress (for testing or restart)."""
        self.metrics_tracker.delete_player_stats(self.player_id)
        self.player_stats = PlayerStats(player_id=self.player_id)
