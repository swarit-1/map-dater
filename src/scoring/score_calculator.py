"""
Score calculation for map dating guesses.

Implements fair scoring that rewards accuracy and penalizes overconfidence.
"""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from models import YearRange
from game.game_models import (
    UserGuess, GameRound, ScoreBreakdown, DifficultyLevel
)


class ScoreCalculator:
    """
    Calculates scores for map dating guesses.

    Scoring philosophy:
    - Reward overlap with system estimate
    - Bonus for precision when correct
    - Penalty for overconfident narrow guesses that miss
    - Scale by difficulty
    """

    # Difficulty multipliers
    DIFFICULTY_MULTIPLIERS = {
        DifficultyLevel.BEGINNER: 1.0,
        DifficultyLevel.INTERMEDIATE: 1.3,
        DifficultyLevel.EXPERT: 1.6
    }

    def __init__(self):
        """Initialize the score calculator."""
        pass

    def calculate_score(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> ScoreBreakdown:
        """
        Calculate score for a user's guess.

        Args:
            user_guess: The user's guess
            game_round: The game round being played

        Returns:
            ScoreBreakdown with detailed scoring information
        """
        guess_range = user_guess.to_range()
        answer_range = game_round.get_answer_range()
        most_likely_year = game_round.system_estimate.most_likely_year

        # Calculate base metrics
        overlap_pct = self._calculate_overlap_percentage(guess_range, answer_range)
        years_off = self._calculate_years_off(guess_range, most_likely_year)
        guess_width = user_guess.get_width()

        # Calculate base score from overlap
        base_score = self._base_score_from_overlap(overlap_pct)

        # Accuracy bonus for precise correct guesses
        accuracy_bonus = self._calculate_accuracy_bonus(
            guess_range, answer_range, guess_width, overlap_pct
        )

        # Confidence penalty for narrow misses
        confidence_penalty = self._calculate_confidence_penalty(
            guess_width, overlap_pct, years_off
        )

        # Difficulty multiplier
        difficulty_multiplier = self.DIFFICULTY_MULTIPLIERS[game_round.difficulty]

        return ScoreBreakdown(
            base_score=base_score,
            accuracy_bonus=accuracy_bonus,
            confidence_penalty=confidence_penalty,
            difficulty_multiplier=difficulty_multiplier,
            overlap_percentage=overlap_pct,
            guess_width=guess_width,
            years_off=years_off
        )

    def _calculate_overlap_percentage(
        self,
        guess_range: YearRange,
        answer_range: YearRange
    ) -> float:
        """
        Calculate what percentage of the guess overlaps with the answer.

        Returns:
            Percentage (0-100) of overlap relative to guess range
        """
        intersection = guess_range.intersection(answer_range)

        if intersection is None:
            return 0.0

        intersection_width = intersection.end - intersection.start + 1
        guess_width = guess_range.end - guess_range.start + 1

        return (intersection_width / guess_width) * 100

    def _calculate_years_off(
        self,
        guess_range: YearRange,
        most_likely_year: int
    ) -> int:
        """
        Calculate how far off the guess is from the most likely year.

        Returns:
            Number of years off (0 if most likely year is in guess range)
        """
        # If most likely year is in the guess range, years off is 0
        if guess_range.start <= most_likely_year <= guess_range.end:
            return 0

        # Otherwise, distance to nearest edge
        if most_likely_year < guess_range.start:
            return guess_range.start - most_likely_year
        else:
            return most_likely_year - guess_range.end

    def _base_score_from_overlap(self, overlap_pct: float) -> float:
        """
        Convert overlap percentage to base score.

        100% overlap → 80 points (leaving room for bonuses)
        50% overlap → 40 points
        0% overlap → 0 points
        """
        return overlap_pct * 0.8

    def _calculate_accuracy_bonus(
        self,
        guess_range: YearRange,
        answer_range: YearRange,
        guess_width: int,
        overlap_pct: float
    ) -> float:
        """
        Bonus for precise correct guesses.

        Reward users who:
        - Make narrow guesses (showing confidence)
        - Get high overlap (showing accuracy)

        Args:
            guess_range: User's guess range
            answer_range: System's answer range
            guess_width: Width of guess in years
            overlap_pct: Overlap percentage

        Returns:
            Bonus points (0-20)
        """
        if overlap_pct < 50:
            return 0.0

        # Precision factor: narrow guesses are harder
        # 1-year guess → 2.0x
        # 10-year guess → 1.5x
        # 50-year guess → 1.0x
        # 100+ year guess → 0.5x
        if guess_width <= 1:
            precision_factor = 2.0
        elif guess_width <= 10:
            precision_factor = 1.5
        elif guess_width <= 50:
            precision_factor = 1.0
        else:
            precision_factor = 0.5

        # Overlap factor: higher overlap → more bonus
        overlap_factor = (overlap_pct / 100)

        # Maximum bonus is 20 points
        bonus = 20 * precision_factor * overlap_factor

        return min(20.0, bonus)

    def _calculate_confidence_penalty(
        self,
        guess_width: int,
        overlap_pct: float,
        years_off: int
    ) -> float:
        """
        Penalty for overconfident narrow guesses that miss.

        Penalize users who:
        - Make very narrow guesses (high confidence)
        - Miss the answer significantly

        Args:
            guess_width: Width of guess in years
            overlap_pct: Overlap percentage
            years_off: Distance from most likely year

        Returns:
            Penalty points (0-30)
        """
        # No penalty for accurate guesses
        if overlap_pct > 50:
            return 0.0

        # Confidence factor: narrower guess = more overconfident
        # 1-year guess → 3.0x
        # 10-year guess → 2.0x
        # 50-year guess → 1.0x
        # 100+ year guess → 0.5x
        if guess_width <= 1:
            confidence_factor = 3.0
        elif guess_width <= 10:
            confidence_factor = 2.0
        elif guess_width <= 50:
            confidence_factor = 1.0
        else:
            confidence_factor = 0.5

        # Miss severity: how far off
        # Within 10 years → 0.2x
        # Within 50 years → 0.5x
        # Within 100 years → 1.0x
        # More than 100 years → 1.5x
        if years_off <= 10:
            miss_factor = 0.2
        elif years_off <= 50:
            miss_factor = 0.5
        elif years_off <= 100:
            miss_factor = 1.0
        else:
            miss_factor = 1.5

        # Maximum penalty is 30 points
        penalty = 30 * confidence_factor * miss_factor

        return min(30.0, penalty)

    def is_accurate(self, user_guess: UserGuess, game_round: GameRound) -> bool:
        """
        Check if the guess is considered accurate.

        Accurate means any overlap with the answer range.

        Args:
            user_guess: User's guess
            game_round: Game round

        Returns:
            True if accurate
        """
        guess_range = user_guess.to_range()
        answer_range = game_round.get_answer_range()

        return guess_range.overlaps(answer_range)

    def is_exact(self, user_guess: UserGuess, game_round: GameRound) -> bool:
        """
        Check if the guess is considered exact.

        Exact means within 5 years of the most likely year.

        Args:
            user_guess: User's guess
            game_round: Game round

        Returns:
            True if exact
        """
        guess_range = user_guess.to_range()
        most_likely = game_round.system_estimate.most_likely_year

        # Check if most likely year is within 5 years of guess range
        return (
            abs(guess_range.start - most_likely) <= 5 or
            abs(guess_range.end - most_likely) <= 5 or
            (guess_range.start <= most_likely <= guess_range.end)
        )
