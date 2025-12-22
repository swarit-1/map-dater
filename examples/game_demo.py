"""
Interactive Game Demo

Demonstrates the complete map dating game system with simulated gameplay.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from game.game_engine import GameEngine
from game.game_models import UserGuess, DifficultyLevel
from models import YearRange


def demo_single_round():
    """Demonstrate a single game round."""
    print("=" * 70)
    print("SINGLE ROUND DEMO")
    print("=" * 70)

    # Initialize game engine
    engine = GameEngine(player_id="demo_player")

    # Start a new round (using mock data, no image needed)
    print("\nStarting a new round...")
    game_round = engine.start_new_round(
        difficulty=DifficultyLevel.BEGINNER,
        use_mock=True
    )

    print(f"\nRound ID: {game_round.round_id}")
    print(f"Difficulty: {game_round.difficulty.value}")
    print(f"Map: {game_round.map_metadata.description}")

    # Show some context (but not the answer!)
    print("\n📍 MAP CONTEXT:")
    print(f"  Region: {game_round.map_metadata.region}")
    print(f"  Source: {game_round.map_metadata.source}")

    # Simulate user seeing the map and making a guess
    print("\n" + "-" * 70)
    print("User examines the map and makes a guess...")
    print("-" * 70)

    # User guesses 1960-1980
    user_guess = UserGuess(year_range=YearRange(1960, 1980))
    print(f"\nUSER GUESS: {user_guess.to_range()}")

    # Submit guess and get result
    print("\nProcessing guess...")
    result = engine.submit_guess(user_guess)

    # Show results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\n{result.get_summary()}")
    print(f"\nScore: {result.score.final_score:.1f}/100")
    print(f"Years off: {result.score.years_off}")

    print("\n" + "-" * 70)
    print("FEEDBACK")
    print("-" * 70)
    print(result.feedback)


def demo_multiple_rounds():
    """Demonstrate multiple rounds with progression."""
    print("\n\n" + "=" * 70)
    print("MULTIPLE ROUNDS DEMO - Difficulty Progression")
    print("=" * 70)

    # Initialize game engine
    engine = GameEngine(player_id="progression_demo")
    engine.reset_progress()  # Start fresh

    scenarios = [
        # Round 1: Good guess
        {
            'round_num': 1,
            'guess': UserGuess(year_range=YearRange(1950, 1990)),
            'description': 'Conservative range guess'
        },
        # Round 2: Better guess
        {
            'round_num': 2,
            'guess': UserGuess(year_range=YearRange(1960, 1980)),
            'description': 'Narrower range'
        },
        # Round 3: Precise guess
        {
            'round_num': 3,
            'guess': UserGuess(year=1970),
            'description': 'Confident point guess'
        },
    ]

    for scenario in scenarios:
        print(f"\n{'─' * 70}")
        print(f"ROUND {scenario['round_num']}: {scenario['description']}")
        print(f"{'─' * 70}")

        # Start round
        game_round = engine.start_new_round(use_mock=True)
        recommended_diff = engine.get_recommended_difficulty()

        print(f"\nDifficulty: {game_round.difficulty.value}")
        print(f"User guesses: {scenario['guess'].to_range()}")

        # Submit guess
        result = engine.submit_guess(scenario['guess'])

        # Show compact results
        print(f"\n{result.get_summary()}")
        print(f"  Actual range: {result.system_estimate.year_range}")
        print(f"  Most likely: {result.system_estimate.most_likely_year}")

    # Show final progress
    print("\n" + "=" * 70)
    print("FINAL PROGRESS REPORT")
    print("=" * 70)
    print(engine.get_player_progress())


def demo_difficulty_levels():
    """Demonstrate different difficulty levels."""
    print("\n\n" + "=" * 70)
    print("DIFFICULTY LEVELS DEMO")
    print("=" * 70)

    engine = GameEngine(player_id="difficulty_demo")

    for difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.EXPERT]:
        print(f"\n{'─' * 70}")
        print(f"{difficulty.value.upper()} MODE")
        print(f"{'─' * 70}")

        # Start round
        game_round = engine.start_new_round(difficulty=difficulty, use_mock=True)

        # Show key signals
        print("\nKey dating signals:")
        for i, signal in enumerate(game_round.get_key_signals()[:3], 1):
            print(f"  {i}. {signal.description}")
            print(f"     Range: {signal.year_range}")

        # Make a reasonable guess
        answer_range = game_round.get_answer_range()
        # Guess slightly offset from answer
        guess = UserGuess(year_range=YearRange(
            answer_range.start - 10,
            answer_range.end + 10
        ))

        result = engine.submit_guess(guess)
        print(f"\nGuess: {guess.to_range()}")
        print(f"Answer: {answer_range}")
        print(f"Score: {result.score.final_score:.1f}/100 (difficulty multiplier: {result.score.difficulty_multiplier:.1f})")


def demo_learning_progression():
    """Demonstrate how feedback teaches historical reasoning."""
    print("\n\n" + "=" * 70)
    print("LEARNING PROGRESSION DEMO")
    print("=" * 70)

    engine = GameEngine(player_id="learner")

    print("\nScenario: Player makes increasingly informed guesses")

    # Round 1: Completely wrong
    print("\n" + "─" * 70)
    print("ROUND 1: Player doesn't know what to look for")
    print("─" * 70)

    game_round = engine.start_new_round(difficulty=DifficultyLevel.BEGINNER, use_mock=True)

    # Wild guess
    wrong_guess = UserGuess(year_range=YearRange(1800, 1850))
    print(f"\nGuess: {wrong_guess.to_range()} (\"Looks old!\")")

    result = engine.submit_guess(wrong_guess)

    print(f"\n{result.get_summary()}")
    print("\nKey lesson from feedback:")
    print("  → Learned that political entities like 'USSR' have specific date ranges")

    # Round 2: Better informed
    print("\n" + "─" * 70)
    print("ROUND 2: Player recognizes some clues")
    print("─" * 70)

    game_round = engine.start_new_round(difficulty=DifficultyLevel.BEGINNER, use_mock=True)

    # More informed guess
    better_guess = UserGuess(year_range=YearRange(1920, 1960))
    print(f"\nGuess: {better_guess.to_range()} (\"Saw USSR mentioned!\")")

    result = engine.submit_guess(better_guess)

    print(f"\n{result.get_summary()}")
    print("\nImprovement:")
    print(f"  → Overlaps with answer? {result.was_accurate}")

    # Show stats
    print("\n" + "=" * 70)
    stats = engine.get_stats_summary()
    print(f"Player improvement: {stats['accuracy_rate']:.0f}% accurate over {stats['rounds_played']} rounds")
    print(f"Recommended next level: {stats['recommended_difficulty'].upper()}")


def main():
    """Run all demos."""
    print("\n" + "#" * 70)
    print("# MAP DATING GAME - COMPLETE DEMO")
    print("#" * 70)

    try:
        demo_single_round()
        demo_multiple_rounds()
        demo_difficulty_levels()
        demo_learning_progression()

        print("\n" + "#" * 70)
        print("# DEMO COMPLETE")
        print("#" * 70)

        print("\n💡 Key Takeaways:")
        print("  • Narrow correct guesses score higher than wide guesses")
        print("  • Overconfident wrong guesses are penalized")
        print("  • Difficulty scales automatically based on performance")
        print("  • Feedback teaches historical reasoning, not just dates")
        print("  • Players improve by learning to recognize entity signals")

        print("\n🎮 To play interactively, use:")
        print("  python examples/play_game.py")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
