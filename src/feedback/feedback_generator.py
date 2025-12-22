"""
Educational feedback generation.

Explains what the user got right, what they missed, and teaches
historical reasoning skills.
"""

from typing import List, Tuple
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from models import DateSignal, SignalType, YearRange
from game.game_models import UserGuess, GameRound, ScoreBreakdown, DifficultyLevel


class FeedbackGenerator:
    """
    Generates educational feedback for game guesses.

    Focus on teaching, not just scoring.
    """

    def __init__(self, difficulty: DifficultyLevel = DifficultyLevel.BEGINNER):
        """
        Initialize feedback generator.

        Args:
            difficulty: Controls verbosity and detail level
        """
        self.difficulty = difficulty

    def generate_feedback(
        self,
        user_guess: UserGuess,
        game_round: GameRound,
        score: ScoreBreakdown
    ) -> str:
        """
        Generate comprehensive educational feedback.

        Args:
            user_guess: User's guess
            game_round: Game round information
            score: Score breakdown

        Returns:
            Multi-line feedback text
        """
        parts = []

        # Header with comparison
        parts.append(self._generate_header(user_guess, game_round))

        # Explain the direction of error
        parts.append(self._explain_error_direction(user_guess, game_round))

        # Key clues analysis
        parts.append(self._analyze_key_clues(user_guess, game_round))

        # Learning tips
        if self.difficulty == DifficultyLevel.BEGINNER:
            parts.append(self._generate_beginner_tip(game_round))

        # Scoring explanation
        parts.append(self._explain_score(score))

        return "\n\n".join(parts)

    def _generate_header(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> str:
        """Generate feedback header with guess comparison."""
        guess_range = user_guess.to_range()
        answer_range = game_round.get_answer_range()
        most_likely = game_round.system_estimate.most_likely_year

        guess_str = str(guess_range) if user_guess.get_width() > 0 else str(guess_range.start)
        answer_str = str(answer_range)

        overlaps = guess_range.overlaps(answer_range)

        if overlaps:
            verdict = "[OK] Your guess overlaps with the system estimate!"
        else:
            verdict = "[X] Your guess does not overlap with the system estimate."

        return (
            f"YOUR GUESS: {guess_str}\n"
            f"SYSTEM ESTIMATE: {answer_str}\n"
            f"Most likely year: {most_likely}\n"
            f"\n{verdict}"
        )

    def _explain_error_direction(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> str:
        """Explain if the user guessed too early, too late, or correctly."""
        guess_range = user_guess.to_range()
        answer_range = game_round.get_answer_range()
        most_likely = game_round.system_estimate.most_likely_year

        # Check relationship
        if guess_range.overlaps(answer_range):
            if guess_range.start < answer_range.start and guess_range.end > answer_range.end:
                return "Your guess range encompasses the entire answer range. Good caution, but try to narrow it down!"
            elif guess_range.start >= answer_range.start and guess_range.end <= answer_range.end:
                return "Your guess range fits entirely within the answer range. Excellent precision!"
            else:
                return "Your guess partially overlaps with the answer. Close!"

        # Doesn't overlap - which direction?
        if guess_range.end < answer_range.start:
            years_gap = answer_range.start - guess_range.end
            return f"You guessed TOO EARLY by about {years_gap} years."
        else:
            years_gap = guess_range.start - answer_range.end
            return f"You guessed TOO LATE by about {years_gap} years."

    def _analyze_key_clues(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> str:
        """Analyze which clues support vs contradict the guess."""
        guess_range = user_guess.to_range()
        key_signals = game_round.get_key_signals()

        lines = ["KEY CLUES YOU SHOULD KNOW:"]

        for i, signal in enumerate(key_signals, 1):
            signal_range = signal.year_range

            # Does this signal support the user's guess?
            supports_guess = guess_range.overlaps(signal_range)

            if supports_guess:
                icon = "[+]"
                verdict = "This supports your guess!"
            else:
                icon = "[-]"
                verdict = "This contradicts your guess."

            lines.append(
                f"  {i}. {icon} {signal.description}\n"
                f"     Valid: {signal_range}\n"
                f"     {verdict}\n"
                f"     Why: {signal.reasoning}"
            )

        return "\n".join(lines)

    def _generate_beginner_tip(self, game_round: GameRound) -> str:
        """Generate a helpful tip for beginners."""
        key_signals = game_round.get_key_signals()

        if not key_signals:
            return "TIP: Look for political entity names like countries and cities!"

        # Give tip based on most important signal type
        top_signal = key_signals[0]

        tips = {
            SignalType.ENTITY: (
                "TIP: Pay close attention to political entity names. "
                "Countries and cities change names when borders shift or regimes change. "
                "For example: USSR (1922-1991), Constantinople->Istanbul (1930)."
            ),
            SignalType.TEXTUAL: (
                "TIP: Years mentioned in text can be clues, but be careful! "
                "A map from 1950 might reference events from 1914. "
                "Look for multiple temporal clues to triangulate."
            ),
            SignalType.VISUAL: (
                "TIP: Visual features like printing style, border drawing, and colors "
                "can reveal the era of production. Hand-drawn borders suggest earlier maps, "
                "while digital precision suggests modern ones."
            )
        }

        return tips.get(top_signal.signal_type, "TIP: Look for multiple types of clues!")

    def _explain_score(self, score: ScoreBreakdown) -> str:
        """Explain how the score was calculated."""
        lines = ["SCORING BREAKDOWN:"]

        lines.append(f"  Base score (overlap): {score.base_score:.1f} points")

        if score.accuracy_bonus > 0:
            lines.append(f"  Accuracy bonus: +{score.accuracy_bonus:.1f} points")

        if score.confidence_penalty > 0:
            lines.append(f"  Overconfidence penalty: -{score.confidence_penalty:.1f} points")

        if score.difficulty_multiplier != 1.0:
            lines.append(f"  Difficulty multiplier: ×{score.difficulty_multiplier:.1f}")

        lines.append(f"\n  FINAL SCORE: {score.final_score:.1f}/100")

        # Add interpretation
        if score.final_score >= 80:
            lines.append("  [***] Excellent work!")
        elif score.final_score >= 60:
            lines.append("  [++] Good job!")
        elif score.final_score >= 40:
            lines.append("  [~] Keep learning!")
        else:
            lines.append("  [!] Try again - you'll improve!")

        return "\n".join(lines)

    def identify_correct_signals(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> List[DateSignal]:
        """
        Identify which signals the user's guess aligns with.

        Args:
            user_guess: User's guess
            game_round: Game round

        Returns:
            List of signals that support the guess
        """
        guess_range = user_guess.to_range()
        correct_signals = []

        for signal in game_round.get_key_signals():
            if guess_range.overlaps(signal.year_range):
                correct_signals.append(signal)

        return correct_signals

    def identify_missed_signals(
        self,
        user_guess: UserGuess,
        game_round: GameRound
    ) -> List[DateSignal]:
        """
        Identify which signals the user missed or ignored.

        Args:
            user_guess: User's guess
            game_round: Game round

        Returns:
            List of signals that contradict the guess
        """
        guess_range = user_guess.to_range()
        missed_signals = []

        for signal in game_round.get_key_signals():
            if not guess_range.overlaps(signal.year_range):
                missed_signals.append(signal)

        return missed_signals

    def generate_short_feedback(
        self,
        user_guess: UserGuess,
        game_round: GameRound,
        score: ScoreBreakdown
    ) -> str:
        """
        Generate brief feedback for quick games.

        Args:
            user_guess: User's guess
            game_round: Game round
            score: Score breakdown

        Returns:
            One-paragraph feedback
        """
        guess_range = user_guess.to_range()
        answer_range = game_round.get_answer_range()
        most_likely = game_round.system_estimate.most_likely_year

        if guess_range.overlaps(answer_range):
            result = "Correct!"
        elif guess_range.end < answer_range.start:
            result = "Too early."
        else:
            result = "Too late."

        top_signal = game_round.get_key_signals()[0] if game_round.get_key_signals() else None

        if top_signal:
            key_clue = f"Key clue: {top_signal.description} ({top_signal.year_range})."
        else:
            key_clue = ""

        return (
            f"{result} System estimate: {answer_range} (most likely: {most_likely}). "
            f"{key_clue} "
            f"Score: {score.final_score:.0f}/100."
        )
