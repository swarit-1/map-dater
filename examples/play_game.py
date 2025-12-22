"""
Interactive Map Dating Game

Play the map dating game interactively from the command line.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'src'))

from game.game_engine import GameEngine
from game.game_models import UserGuess, DifficultyLevel
from models import YearRange


def get_player_id() -> str:
    """Get or create player ID."""
    print("Welcome to the Map Dating Game!")
    print("-" * 50)

    player_id = input("\nEnter your player name (or press Enter for 'player1'): ").strip()

    if not player_id:
        player_id = "player1"

    return player_id


def get_user_guess() -> UserGuess:
    """
    Get a guess from the user.

    Returns:
        UserGuess object
    """
    print("\nHow would you like to guess?")
    print("  1. Single year (e.g., 1945)")
    print("  2. Year range (e.g., 1940-1950)")

    choice = input("\nChoice (1 or 2): ").strip()

    if choice == "1":
        while True:
            try:
                year = int(input("Enter year: ").strip())
                return UserGuess(year=year)
            except ValueError:
                print("Invalid year. Please enter a number.")

    else:
        while True:
            try:
                range_input = input("Enter year range (e.g., 1940-1950): ").strip()
                parts = range_input.split("-")

                if len(parts) != 2:
                    print("Invalid format. Use: START-END")
                    continue

                start = int(parts[0].strip())
                end = int(parts[1].strip())

                return UserGuess(year_range=YearRange(start, end))

            except ValueError:
                print("Invalid input. Please use format: 1940-1950")


def play_round(engine: GameEngine):
    """
    Play a single round.

    Args:
        engine: Game engine
    """
    print("\n" + "=" * 70)
    print("NEW ROUND")
    print("=" * 70)

    # Start round
    recommended_diff = engine.get_recommended_difficulty()
    print(f"\nRecommended difficulty: {recommended_diff.value.upper()}")

    use_recommended = input("Use recommended difficulty? (y/n, default=y): ").strip().lower()

    if use_recommended in ['n', 'no']:
        print("\nChoose difficulty:")
        print("  1. Beginner (obvious political clues)")
        print("  2. Intermediate (subtle name changes)")
        print("  3. Expert (visual analysis required)")

        diff_choice = input("Choice (1/2/3): ").strip()

        diff_map = {
            "1": DifficultyLevel.BEGINNER,
            "2": DifficultyLevel.INTERMEDIATE,
            "3": DifficultyLevel.EXPERT
        }

        difficulty = diff_map.get(diff_choice, recommended_diff)
    else:
        difficulty = recommended_diff

    # Generate round
    print("\nGenerating round...")
    game_round = engine.start_new_round(difficulty=difficulty, use_mock=True)

    print(f"\n📍 MAP INFORMATION:")
    print(f"  Region: {game_round.map_metadata.region}")
    print(f"  Description: {game_round.map_metadata.description}")
    print(f"  Difficulty: {game_round.difficulty.value.upper()}")

    # Show hints for beginners
    if difficulty == DifficultyLevel.BEGINNER:
        print("\n💡 HINTS:")
        print("  • Look for political entity names (countries, cities)")
        print("  • Many countries changed names in the 20th century")
        print("  • USSR (1922-1991), East Germany (1949-1990), etc.")

    # Get user guess
    print("\n" + "-" * 70)
    print("Examine the clues and make your guess!")
    print("-" * 70)

    guess = get_user_guess()

    # Submit guess
    print("\nProcessing your guess...")
    result = engine.submit_guess(guess)

    # Show results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n{result.get_summary()}\n")

    print(result.feedback)

    # Ask if they want to see stats
    print("\n" + "-" * 70)
    show_stats = input("\nShow progress stats? (y/n, default=n): ").strip().lower()

    if show_stats in ['y', 'yes']:
        print("\n" + engine.get_player_progress())


def main():
    """Main game loop."""
    print("\n" + "=" * 70)
    print("  MAP DATING GAME  ".center(70))
    print("=" * 70)
    print("\nGuess when historical maps were created!")
    print("Learn to recognize temporal clues and improve over time.")

    # Get player ID
    player_id = get_player_id()

    # Initialize game engine
    engine = GameEngine(player_id=player_id)

    # Show existing stats if player has played before
    if engine.player_stats.rounds_played > 0:
        print(f"\nWelcome back, {player_id}!")
        print(f"You've played {engine.player_stats.rounds_played} rounds.")
        print(f"Average score: {engine.player_stats.get_average_score():.1f}/100")
        print(f"Accuracy: {engine.player_stats.get_accuracy_rate():.1f}%")

    # Game loop
    while True:
        try:
            play_round(engine)

            # Ask to continue
            print("\n" + "=" * 70)
            continue_game = input("\nPlay another round? (y/n, default=y): ").strip().lower()

            if continue_game in ['n', 'no']:
                break

        except KeyboardInterrupt:
            print("\n\nGame interrupted.")
            break

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

            retry = input("\nTry another round? (y/n): ").strip().lower()
            if retry not in ['y', 'yes']:
                break

    # Final stats
    print("\n" + "=" * 70)
    print("FINAL STATS")
    print("=" * 70)

    stats = engine.get_stats_summary()
    print(f"\nPlayer: {stats['player_id']}")
    print(f"Rounds played: {stats['rounds_played']}")
    print(f"Average score: {stats['average_score']:.1f}/100")
    print(f"Accuracy rate: {stats['accuracy_rate']:.1f}%")

    print("\nThanks for playing!")
    print("Your progress has been saved.")


if __name__ == '__main__':
    main()
