"""
Unit tests for game components.
"""

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from models import YearRange
from game.game_models import UserGuess, DifficultyLevel, PlayerStats, ScoreBreakdown
from game.round_generator import RoundGenerator
from scoring.score_calculator import ScoreCalculator


class TestUserGuess(unittest.TestCase):
    """Test UserGuess functionality."""

    def test_point_guess(self):
        """Test single-year guess."""
        guess = UserGuess(year=1950)

        self.assertTrue(guess.is_point_guess())
        self.assertEqual(guess.get_width(), 0)

        guess_range = guess.to_range()
        self.assertEqual(guess_range.start, 1950)
        self.assertEqual(guess_range.end, 1950)

    def test_range_guess(self):
        """Test year range guess."""
        guess = UserGuess(year_range=YearRange(1940, 1960))

        self.assertFalse(guess.is_point_guess())
        self.assertEqual(guess.get_width(), 20)

        guess_range = guess.to_range()
        self.assertEqual(guess_range.start, 1940)
        self.assertEqual(guess_range.end, 1960)

    def test_invalid_guess(self):
        """Test that invalid guesses raise errors."""
        # No guess provided
        with self.assertRaises(ValueError):
            UserGuess()

        # Both types provided
        with self.assertRaises(ValueError):
            UserGuess(year=1950, year_range=YearRange(1940, 1960))


class TestScoreCalculator(unittest.TestCase):
    """Test score calculation logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ScoreCalculator()
        self.round_gen = RoundGenerator()

    def test_perfect_guess(self):
        """Test scoring for a perfect guess."""
        # Create a mock round
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        # Guess the exact answer
        answer_range = game_round.get_answer_range()
        guess = UserGuess(year_range=answer_range)

        score = self.calculator.calculate_score(guess, game_round)

        # Should get high base score (100% overlap)
        self.assertEqual(score.overlap_percentage, 100.0)
        self.assertEqual(score.years_off, 0)
        self.assertGreater(score.final_score, 70)

    def test_partial_overlap(self):
        """Test scoring for partial overlap."""
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        # Answer is 1949-1990, guess 1960-1980 (partial overlap)
        guess = UserGuess(year_range=YearRange(1960, 1980))

        score = self.calculator.calculate_score(guess, game_round)

        # Should have some overlap
        self.assertGreater(score.overlap_percentage, 0)
        self.assertGreater(score.final_score, 0)

    def test_complete_miss(self):
        """Test scoring for a complete miss."""
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        # Answer is 1949-1990, guess 1800-1850 (no overlap)
        guess = UserGuess(year_range=YearRange(1800, 1850))

        score = self.calculator.calculate_score(guess, game_round)

        # Should have no overlap
        self.assertEqual(score.overlap_percentage, 0.0)
        self.assertGreater(score.years_off, 0)

    def test_narrow_correct_guess_bonus(self):
        """Test that narrow correct guesses get bonuses."""
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        # Narrow guess within answer range
        most_likely = game_round.system_estimate.most_likely_year
        narrow_guess = UserGuess(year_range=YearRange(most_likely - 2, most_likely + 2))

        # Wide guess
        wide_guess = UserGuess(year_range=YearRange(1900, 2000))

        narrow_score = self.calculator.calculate_score(narrow_guess, game_round)
        wide_score = self.calculator.calculate_score(wide_guess, game_round)

        # Narrow guess should get accuracy bonus
        self.assertGreater(narrow_score.accuracy_bonus, 0)
        self.assertGreater(narrow_score.final_score, wide_score.final_score)

    def test_overconfident_penalty(self):
        """Test penalty for narrow wrong guesses."""
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        # Very narrow guess that's wrong (1800)
        overconfident_guess = UserGuess(year=1800)

        score = self.calculator.calculate_score(overconfident_guess, game_round)

        # Should have confidence penalty
        self.assertGreater(score.confidence_penalty, 0)

    def test_accuracy_detection(self):
        """Test accurate/exact detection."""
        game_round = self.round_gen.create_mock_round(DifficultyLevel.BEGINNER)

        answer_range = game_round.get_answer_range()
        most_likely = game_round.system_estimate.most_likely_year

        # Accurate guess (overlaps)
        accurate_guess = UserGuess(year_range=YearRange(
            answer_range.start,
            answer_range.end
        ))
        self.assertTrue(self.calculator.is_accurate(accurate_guess, game_round))

        # Exact guess (within 5 years of most likely)
        exact_guess = UserGuess(year=most_likely)
        self.assertTrue(self.calculator.is_exact(exact_guess, game_round))

        # Inaccurate guess (no overlap)
        inaccurate_guess = UserGuess(year=1800)
        self.assertFalse(self.calculator.is_accurate(inaccurate_guess, game_round))


class TestPlayerStats(unittest.TestCase):
    """Test player statistics."""

    def test_initial_stats(self):
        """Test initial player stats."""
        stats = PlayerStats(player_id="test_player")

        self.assertEqual(stats.rounds_played, 0)
        self.assertEqual(stats.get_average_score(), 0.0)
        self.assertEqual(stats.get_accuracy_rate(), 0.0)

    def test_difficulty_progression(self):
        """Test difficulty recommendation."""
        stats = PlayerStats(player_id="test_player")

        # Should start at beginner
        self.assertEqual(stats.get_suggested_difficulty(), DifficultyLevel.BEGINNER)

        # After 3 good rounds, should recommend intermediate
        stats.rounds_played = 3
        stats.beginner_rounds = 3
        stats.accurate_guesses = 3
        stats.total_score = 210  # Avg 70

        self.assertEqual(stats.get_suggested_difficulty(), DifficultyLevel.INTERMEDIATE)


class TestRoundGenerator(unittest.TestCase):
    """Test game round generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = RoundGenerator()

    def test_mock_round_generation(self):
        """Test creating mock rounds."""
        # Beginner round
        beginner_round = self.generator.create_mock_round(DifficultyLevel.BEGINNER)
        self.assertIsNotNone(beginner_round)
        self.assertEqual(beginner_round.difficulty, DifficultyLevel.BEGINNER)
        self.assertGreater(len(beginner_round.get_key_signals()), 0)

        # Intermediate round
        intermediate_round = self.generator.create_mock_round(DifficultyLevel.INTERMEDIATE)
        self.assertEqual(intermediate_round.difficulty, DifficultyLevel.INTERMEDIATE)

        # Expert round
        expert_round = self.generator.create_mock_round(DifficultyLevel.EXPERT)
        self.assertEqual(expert_round.difficulty, DifficultyLevel.EXPERT)

    def test_round_has_answer(self):
        """Test that rounds have valid answers."""
        game_round = self.generator.create_mock_round(DifficultyLevel.BEGINNER)

        answer_range = game_round.get_answer_range()
        self.assertIsNotNone(answer_range)
        self.assertGreater(answer_range.end, answer_range.start)

        confidence = game_round.get_confidence()
        self.assertGreater(confidence, 0)
        self.assertLessEqual(confidence, 1.0)


if __name__ == '__main__':
    unittest.main()
