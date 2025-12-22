"""
Simple Game Demo (No Dependencies Required)

Demonstrates game mechanics without requiring OCR/image processing.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from game.game_models import (
    UserGuess, DifficultyLevel, GameRound, MapMetadata,
    PlayerStats, ScoreBreakdown
)
from models import DateEstimate, DateSignal, SignalType, YearRange
from scoring.score_calculator import ScoreCalculator
from feedback.feedback_generator import FeedbackGenerator
from knowledge import HistoricalKnowledgeBase
import uuid


def create_simple_mock_round(difficulty: DifficultyLevel) -> GameRound:
    """Create a mock round without needing the full pipeline."""
    kb = HistoricalKnowledgeBase()

    # Create signals based on difficulty
    if difficulty == DifficultyLevel.BEGINNER:
        entities = [kb.find_by_name('USSR'), kb.find_by_name('East Germany')]
        year_range = YearRange(1949, 1990)
        most_likely = 1970
    elif difficulty == DifficultyLevel.INTERMEDIATE:
        entities = [kb.find_by_name('USSR'), kb.find_by_name('Constantinople')]
        year_range = YearRange(1922, 1930)
        most_likely = 1926
    else:  # EXPERT
        entities = [
            kb.find_by_name('Leningrad'),
            kb.find_by_name('East Germany'),
            kb.find_by_name('Bombay')
        ]
        year_range = YearRange(1949, 1990)
        most_likely = 1970

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

    estimate = DateEstimate(
        year_range=year_range,
        confidence=0.85,
        signals=signals,
        explanation="Mock estimate",
        most_likely_year=most_likely
    )

    map_metadata = MapMetadata(
        map_id=f"mock_{uuid.uuid4().hex[:8]}",
        source="Mock Source",
        region="Europe",
        description=f"Cold War era map ({difficulty.value} difficulty)"
    )

    return GameRound.create(
        map_metadata=map_metadata,
        system_estimate=estimate,
        difficulty=difficulty
    )


def demo_scoring():
    """Demonstrate the scoring system."""
    print("=" * 70)
    print("SCORING SYSTEM DEMO")
    print("=" * 70)

    calculator = ScoreCalculator()
    game_round = create_simple_mock_round(DifficultyLevel.BEGINNER)

    answer_range = game_round.get_answer_range()
    print(f"\nSystem estimate: {answer_range}")
    print(f"Most likely year: {game_round.system_estimate.most_likely_year}")

    # Test different guesses
    test_cases = [
        ("Perfect overlap", UserGuess(year_range=YearRange(1949, 1990))),
        ("Narrow correct", UserGuess(year=1970)),
        ("Wide correct", UserGuess(year_range=YearRange(1900, 2000))),
        ("Partial overlap", UserGuess(year_range=YearRange(1960, 1980))),
        ("Narrow miss", UserGuess(year=1800)),
        ("Wide miss", UserGuess(year_range=YearRange(1800, 1850))),
    ]

    print("\n" + "-" * 70)
    print("Test Cases:")
    print("-" * 70)

    for name, guess in test_cases:
        score = calculator.calculate_score(guess, game_round)
        print(f"\n{name}: {guess.to_range()}")
        print(f"  Overlap: {score.overlap_percentage:.1f}%")
        print(f"  Years off: {score.years_off}")
        print(f"  Base: {score.base_score:.1f} | Bonus: {score.accuracy_bonus:.1f} | Penalty: {score.confidence_penalty:.1f}")
        print(f"  -> FINAL SCORE: {score.final_score:.1f}/100")


def demo_feedback():
    """Demonstrate educational feedback."""
    print("\n\n" + "=" * 70)
    print("EDUCATIONAL FEEDBACK DEMO")
    print("=" * 70)

    calculator = ScoreCalculator()
    feedback_gen = FeedbackGenerator(difficulty=DifficultyLevel.BEGINNER)
    game_round = create_simple_mock_round(DifficultyLevel.BEGINNER)

    # User makes a wrong guess
    guess = UserGuess(year_range=YearRange(1900, 1920))

    score = calculator.calculate_score(guess, game_round)
    feedback = feedback_gen.generate_feedback(guess, game_round, score)

    print("\nScenario: User guesses 1900-1920")
    print("System estimate: 1949-1990")

    print("\n" + "-" * 70)
    print("FEEDBACK GENERATED:")
    print("-" * 70)
    print(feedback)


def demo_progression():
    """Demonstrate difficulty progression."""
    print("\n\n" + "=" * 70)
    print("DIFFICULTY PROGRESSION DEMO")
    print("=" * 70)

    stats = PlayerStats(player_id="test_player")

    print("\nInitial state:")
    print(f"  Recommended difficulty: {stats.get_suggested_difficulty().value}")

    # Simulate 3 good beginner rounds
    print("\nAfter 3 successful beginner rounds...")
    stats.rounds_played = 3
    stats.beginner_rounds = 3
    stats.accurate_guesses = 3
    stats.total_score = 210  # Avg 70

    print(f"  Average score: {stats.get_average_score():.1f}")
    print(f"  Accuracy: {stats.get_accuracy_rate():.1f}%")
    print(f"  Recommended difficulty: {stats.get_suggested_difficulty().value}")

    # Simulate 5 good intermediate rounds
    print("\nAfter 5 successful intermediate rounds...")
    stats.rounds_played = 8
    stats.intermediate_rounds = 5
    stats.accurate_guesses = 7
    stats.total_score = 480  # Avg 60

    print(f"  Average score: {stats.get_average_score():.1f}")
    print(f"  Accuracy: {stats.get_accuracy_rate():.1f}%")
    print(f"  Recommended difficulty: {stats.get_suggested_difficulty().value}")


def main():
    """Run all demos."""
    print("\n" + "#" * 70)
    print("# MAP DATING GAME - SIMPLE DEMO")
    print("#" * 70)

    try:
        demo_scoring()
        demo_feedback()
        demo_progression()

        print("\n" + "#" * 70)
        print("# DEMO COMPLETE")
        print("#" * 70)

        print("\nGame System Status:")
        print("  * Scoring: Working")
        print("  * Feedback: Working")
        print("  * Progression: Working")
        print("  * Mock Rounds: Working")

        print("\nNote:")
        print("  This demo uses mock data and doesn't require OCR/image processing.")
        print("  For full gameplay with real maps, install dependencies:")
        print("    pip install opencv-python pytesseract")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
