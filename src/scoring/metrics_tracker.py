"""
Progress and metrics tracking for players.

Stores player statistics locally (JSON file).
Designed for easy migration to database later.
"""

import json
from typing import Optional, Dict
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from game.game_models import PlayerStats, GameResult


class MetricsTracker:
    """
    Tracks and persists player performance metrics.

    Current: Local JSON storage
    Future: Database backend
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize metrics tracker.

        Args:
            storage_dir: Directory for storing player data
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path(__file__).parent.parent.parent / 'data' / 'player_stats'

        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_player_file(self, player_id: str) -> Path:
        """Get path to player's stats file."""
        return self.storage_dir / f"{player_id}.json"

    def load_player_stats(self, player_id: str) -> PlayerStats:
        """
        Load player statistics from storage.

        Args:
            player_id: Player identifier

        Returns:
            PlayerStats (new if player not found)
        """
        stats_file = self._get_player_file(player_id)

        if not stats_file.exists():
            return PlayerStats(player_id=player_id)

        try:
            with open(stats_file, 'r') as f:
                data = json.load(f)

            return PlayerStats(
                player_id=data['player_id'],
                rounds_played=data['rounds_played'],
                total_score=data['total_score'],
                accurate_guesses=data['accurate_guesses'],
                exact_guesses=data['exact_guesses'],
                beginner_rounds=data['beginner_rounds'],
                intermediate_rounds=data['intermediate_rounds'],
                expert_rounds=data['expert_rounds'],
                avg_years_off=data['avg_years_off'],
                frequently_missed_signals=data.get('frequently_missed_signals', {})
            )
        except Exception as e:
            print(f"Warning: Could not load player stats: {e}")
            return PlayerStats(player_id=player_id)

    def save_player_stats(self, stats: PlayerStats):
        """
        Save player statistics to storage.

        Args:
            stats: PlayerStats to save
        """
        stats_file = self._get_player_file(stats.player_id)

        data = {
            'player_id': stats.player_id,
            'rounds_played': stats.rounds_played,
            'total_score': stats.total_score,
            'accurate_guesses': stats.accurate_guesses,
            'exact_guesses': stats.exact_guesses,
            'beginner_rounds': stats.beginner_rounds,
            'intermediate_rounds': stats.intermediate_rounds,
            'expert_rounds': stats.expert_rounds,
            'avg_years_off': stats.avg_years_off,
            'frequently_missed_signals': stats.frequently_missed_signals
        }

        with open(stats_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_game_result(self, player_id: str, result: GameResult):
        """
        Record a game result and update player stats.

        Args:
            player_id: Player identifier
            result: GameResult to record
        """
        # Load current stats
        stats = self.load_player_stats(player_id)

        # Update with new result
        stats.update_with_result(result)

        # Save updated stats
        self.save_player_stats(stats)

    def get_leaderboard(self, limit: int = 10) -> list:
        """
        Get top players by average score.

        Args:
            limit: Maximum number of players to return

        Returns:
            List of (player_id, avg_score, rounds_played) tuples
        """
        players = []

        for stats_file in self.storage_dir.glob("*.json"):
            player_id = stats_file.stem
            stats = self.load_player_stats(player_id)

            if stats.rounds_played >= 3:  # Minimum rounds for leaderboard
                players.append((
                    player_id,
                    stats.get_average_score(),
                    stats.rounds_played
                ))

        # Sort by average score
        players.sort(key=lambda x: x[1], reverse=True)

        return players[:limit]

    def get_all_players(self) -> list:
        """
        Get all player IDs.

        Returns:
            List of player IDs
        """
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def delete_player_stats(self, player_id: str):
        """
        Delete a player's statistics.

        Args:
            player_id: Player identifier
        """
        stats_file = self._get_player_file(player_id)
        if stats_file.exists():
            stats_file.unlink()

    def export_stats_to_csv(self, output_path: str):
        """
        Export all player statistics to CSV.

        Useful for analysis or backup.

        Args:
            output_path: Path to output CSV file
        """
        import csv

        players = self.get_all_players()

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'player_id',
                'rounds_played',
                'avg_score',
                'accuracy_rate',
                'exact_rate',
                'avg_years_off',
                'beginner_rounds',
                'intermediate_rounds',
                'expert_rounds'
            ])

            # Data
            for player_id in players:
                stats = self.load_player_stats(player_id)

                exact_rate = (stats.exact_guesses / stats.rounds_played * 100
                             if stats.rounds_played > 0 else 0)

                writer.writerow([
                    player_id,
                    stats.rounds_played,
                    f"{stats.get_average_score():.1f}",
                    f"{stats.get_accuracy_rate():.1f}",
                    f"{exact_rate:.1f}",
                    f"{stats.avg_years_off:.1f}",
                    stats.beginner_rounds,
                    stats.intermediate_rounds,
                    stats.expert_rounds
                ])
