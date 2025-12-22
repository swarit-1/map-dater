"""
Hint generation based on difficulty and player performance.

Provides progressive hints to help players improve.
"""

from typing import List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from models import DateSignal, SignalType
from game.game_models import DifficultyLevel, GameRound


class HintEngine:
    """
    Generates difficulty-appropriate hints for players.

    Beginners get more explicit hints, experts get minimal guidance.
    """

    def __init__(self):
        """Initialize hint engine."""
        pass

    def generate_pre_guess_hints(
        self,
        game_round: GameRound,
        reveal_count: int = 1
    ) -> List[str]:
        """
        Generate hints before the user guesses.

        These are mild nudges, not full answers.

        Args:
            game_round: Current game round
            reveal_count: How many hints to reveal

        Returns:
            List of hint strings
        """
        hints = []
        signals = game_round.get_key_signals()

        difficulty = game_round.difficulty

        if difficulty == DifficultyLevel.BEGINNER:
            # Explicit hints for beginners
            for signal in signals[:reveal_count]:
                if signal.signal_type == SignalType.ENTITY:
                    hints.append(
                        f"Look for country or city names. "
                        f"They often changed throughout the 20th century."
                    )
                elif signal.signal_type == SignalType.TEXTUAL:
                    hints.append(
                        f"Check if any years are mentioned in the text. "
                        f"They might indicate when events occurred."
                    )

        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Vague hints for intermediate players
            hints.append("Focus on political entities and territorial names.")
            hints.append("Consider major historical events that changed borders.")

        else:  # EXPERT
            # Minimal hints for experts
            hints.append("Analyze all available signals carefully.")

        return hints

    def generate_post_guess_learning_points(
        self,
        game_round: GameRound,
        missed_signals: List[DateSignal]
    ) -> List[str]:
        """
        Generate learning points based on what the user missed.

        Args:
            game_round: Current game round
            missed_signals: Signals the user didn't account for

        Returns:
            List of educational points
        """
        learning_points = []

        # Group missed signals by type
        entity_signals = [
            s for s in missed_signals
            if s.signal_type == SignalType.ENTITY
        ]

        if entity_signals:
            learning_points.append(
                "💡 LEARNING POINT: Historical entity names are powerful dating clues. "
                "Countries like 'USSR', 'East Germany', and cities like 'Leningrad' "
                "have precise existence dates."
            )

        visual_signals = [
            s for s in missed_signals
            if s.signal_type == SignalType.VISUAL
        ]

        if visual_signals and game_round.difficulty == DifficultyLevel.EXPERT:
            learning_points.append(
                "💡 LEARNING POINT: At expert level, visual features matter. "
                "Border drawing style, typography, and printing techniques "
                "can narrow down the era significantly."
            )

        return learning_points

    def get_difficulty_description(self, difficulty: DifficultyLevel) -> str:
        """Get a description of what each difficulty level tests."""
        descriptions = {
            DifficultyLevel.BEGINNER: (
                "BEGINNER MODE\n"
                "Maps with clear political entity clues (USSR, East Germany, etc.). "
                "Focus on recognizing country and city names."
            ),
            DifficultyLevel.INTERMEDIATE: (
                "INTERMEDIATE MODE\n"
                "Maps requiring attention to subtle name changes (Constantinople→Istanbul). "
                "Combine multiple weak signals."
            ),
            DifficultyLevel.EXPERT: (
                "EXPERT MODE\n"
                "Maps where visual analysis matters. "
                "Typography, border styles, and printing techniques are critical. "
                "Entity clues may be ambiguous."
            )
        }

        return descriptions[difficulty]
