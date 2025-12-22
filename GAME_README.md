# Map Dating Game

An educational gamification layer that teaches historical reasoning through interactive map dating challenges.

## Overview

The Map Dating Game transforms the map dating system into an interactive learning experience. Players:

- 🗺️ See historical maps
- 🤔 Make educated guesses about when they were created
- 📊 Get scored on accuracy
- 📚 Receive educational feedback explaining what they missed
- 📈 Track progress and improve over time

**This is NOT a trivia game** — it's a historical intuition trainer.

## Quick Start

### Play Interactively

```bash
python examples/play_game.py
```

### Run Demo (No Interaction)

```bash
python examples/game_demo.py
```

### Run Unit Tests

```bash
python -m pytest tests/unit/test_game.py -v
```

## Game Mechanics

### Scoring System

Scores are calculated based on:

1. **Base Score (0-80 points)**: How much your guess overlaps with the system's estimate
   - 100% overlap → 80 points
   - 50% overlap → 40 points
   - No overlap → 0 points

2. **Accuracy Bonus (0-20 points)**: Reward for precise correct guesses
   - Narrow guess + high overlap → bonus points
   - Wide guess → no bonus (playing it safe)

3. **Overconfidence Penalty (0-30 points)**: Punishment for narrow wrong guesses
   - Very narrow guess that misses → heavy penalty
   - Wide guess that misses → light penalty

4. **Difficulty Multiplier**:
   - Beginner: ×1.0
   - Intermediate: ×1.3
   - Expert: ×1.6

**Final Score = (Base + Bonus - Penalty) × Difficulty**

### Example Scores

| Guess | System Range | Overlap | Width | Score | Reason |
|-------|-------------|---------|-------|-------|--------|
| 1960-1980 | 1949-1990 | 100% | 20yr | 95 | Perfect overlap, reasonable width |
| 1970 | 1949-1990 | 100% | 1yr | 100 | Exact hit, very precise |
| 1900-2000 | 1949-1990 | 100% | 100yr | 75 | Correct but too safe, no bonus |
| 1800 | 1949-1990 | 0% | 1yr | 10 | Way off + overconfident penalty |
| 1930-1960 | 1949-1990 | 50% | 30yr | 45 | Partial overlap |

## Difficulty Levels

### Beginner
**Focus**: Obvious political entity clues

Maps feature:
- Clear entity names (USSR, East Germany)
- Famous name changes (Constantinople → Istanbul)
- Wide-ranging temporal constraints

**Hints Provided**: 2
**Recommended For**: First 3+ rounds

### Intermediate
**Focus**: Subtle historical details

Maps require:
- Recognizing less obvious name changes
- Combining multiple weak signals
- Understanding border evolution

**Hints Provided**: 1
**Recommended For**: After 70%+ accuracy at Beginner

### Expert
**Focus**: Visual and stylistic analysis

Maps require:
- Typography analysis (future ML feature)
- Border drawing style (future ML feature)
- Ambiguous entity clues

**Hints Provided**: 0
**Recommended For**: After 60%+ accuracy at Intermediate

## Educational Feedback

Every guess receives detailed feedback explaining:

### 1. Direction of Error
```
You guessed TOO EARLY by about 27 years.
```

### 2. Key Clues Analysis
```
KEY CLUES YOU SHOULD KNOW:
  1. ✗ Country: USSR
     Valid: 1922-1991
     This contradicts your guess.
     Why: USSR existed from 1922 to 1991

  2. ✓ City: Constantinople
     Valid: 330-1930
     This supports your guess!
     Why: Constantinople was renamed Istanbul in 1930
```

### 3. Learning Tips
```
TIP: Pay close attention to political entity names. Countries
and cities change names when borders shift or regimes change.
For example: USSR (1922-1991), Constantinople→Istanbul (1930).
```

### 4. Scoring Breakdown
```
SCORING BREAKDOWN:
  Base score (overlap): 45.2 points
  Accuracy bonus: +0.0 points
  Overconfidence penalty: -0.0 points
  Difficulty multiplier: ×1.0

  FINAL SCORE: 45/100
  📚 Keep learning!
```

## Progress Tracking

The system tracks:

- **Rounds played** at each difficulty
- **Average score** over time
- **Accuracy rate** (% of overlapping guesses)
- **Average years off**
- **Frequently missed signals** (to identify weak spots)

Progress is saved locally in `data/player_stats/{player_id}.json`.

### View Progress

```python
from game.game_engine import GameEngine

engine = GameEngine(player_id="your_name")
print(engine.get_player_progress())
```

Output:
```
==================================================
PLAYER PROGRESS REPORT
==================================================

Rounds played: 8
Average score: 67.3/100
Accuracy rate: 75.0%

Performance by difficulty:
  Beginner: 5 rounds
  Intermediate: 3 rounds

Recommended difficulty: INTERMEDIATE

Signals you frequently miss:
  • City: Leningrad (missed 2 times)
  • Country: Czechoslovakia (missed 1 times)

==================================================
```

## Architecture

```
src/
├── game/
│   ├── game_models.py        # Core data models
│   ├── game_engine.py        # Main orchestrator
│   ├── round_generator.py    # Creates game rounds
│   ├── map_sourcer.py        # Fetches maps (mock for now)
│   └── difficulty_manager.py # Difficulty progression
│
├── scoring/
│   ├── score_calculator.py   # Scoring algorithm
│   └── metrics_tracker.py    # Progress persistence
│
└── feedback/
    ├── feedback_generator.py # Educational explanations
    └── hint_engine.py        # Difficulty-based hints
```

## Python API

### Basic Game Flow

```python
from game.game_engine import GameEngine
from game.game_models import UserGuess
from models import YearRange

# Initialize
engine = GameEngine(player_id="alice")

# Start a round
game_round = engine.start_new_round(use_mock=True)

print(f"Map: {game_round.map_metadata.description}")
print(f"Difficulty: {game_round.difficulty.value}")

# User makes a guess
guess = UserGuess(year_range=YearRange(1960, 1980))

# Submit and get results
result = engine.submit_guess(guess)

print(f"Score: {result.score.final_score}/100")
print(result.feedback)
```

### Programmatic Scoring

```python
from scoring.score_calculator import ScoreCalculator
from game.game_models import UserGuess
from models import YearRange

calculator = ScoreCalculator()

# Assuming you have a game_round
guess = UserGuess(year=1950)
score = calculator.calculate_score(guess, game_round)

print(f"Base: {score.base_score}")
print(f"Bonus: {score.accuracy_bonus}")
print(f"Penalty: {score.confidence_penalty}")
print(f"Final: {score.final_score}")
```

### Custom Feedback

```python
from feedback.feedback_generator import FeedbackGenerator
from game.game_models import DifficultyLevel

# Verbose feedback for beginners
feedback_gen = FeedbackGenerator(difficulty=DifficultyLevel.BEGINNER)
feedback = feedback_gen.generate_feedback(guess, game_round, score)

print(feedback)

# Or get a short summary
short = feedback_gen.generate_short_feedback(guess, game_round, score)
print(short)
```

## Design Philosophy

### Educational First
Every score comes with an explanation. Players should understand:
- **What they got right** (reinforcement)
- **What they missed** (learning opportunity)
- **Why it matters** (historical context)

### No Trivia
The game doesn't test memorized dates. Instead, it teaches:
- How to recognize temporal clues
- How to reason about historical evidence
- How to weigh conflicting signals

### Explainable AI
The system's estimate is the "answer", but it's not treated as absolute truth:
- Show confidence scores
- Explain which signals contributed
- Acknowledge when the system is uncertain

### Fair Scoring
Scoring rewards skill, not luck:
- Narrow correct guesses score higher (precision)
- Wide wrong guesses avoid harsh penalties (caution)
- Narrow wrong guesses are penalized (overconfidence)
- Difficulty multipliers reward challenges

## Future Enhancements

### Near-Term (Ready for Implementation)
- ✅ All core game mechanics implemented
- 🔜 Real map sourcing from archives
- 🔜 Time-based scoring (speed bonuses)
- 🔜 Multiplayer leaderboards
- 🔜 Achievement system

### Long-Term (Requires ML Models)
- Visual style hints for expert mode
- Typography-based dating
- Border style analysis
- Adaptive difficulty based on weak spots

## Map Sourcing

### Current: Mock Maps
The system uses generated test maps with known entity clues.

### Future: Real Archives
Designed for integration with:
- **Library of Congress** Maps Collection
- **David Rumsey** Map Collection
- **British Library** Historical Maps

Interface is stubbed in `game/map_sourcer.py`.

## Testing

### Unit Tests

```bash
# Test game mechanics
python -m pytest tests/unit/test_game.py -v

# Test scoring
python -m pytest tests/unit/test_game.py::TestScoreCalculator -v

# Test progression
python -m pytest tests/unit/test_game.py::TestPlayerStats -v
```

### Integration Test

```bash
# Full game flow demo
python examples/game_demo.py
```

## Data Storage

Player stats are stored locally as JSON:

```json
{
  "player_id": "alice",
  "rounds_played": 8,
  "total_score": 538.4,
  "accurate_guesses": 6,
  "exact_guesses": 2,
  "beginner_rounds": 5,
  "intermediate_rounds": 3,
  "expert_rounds": 0,
  "avg_years_off": 15.3,
  "frequently_missed_signals": {
    "City: Leningrad": 2,
    "Country: Czechoslovakia": 1
  }
}
```

Location: `data/player_stats/{player_id}.json`

Easy to migrate to database (Postgres, MongoDB, etc.) later.

## Examples

### Demo Scenarios

See `examples/game_demo.py` for:
- Single round demo
- Multiple rounds with progression
- Different difficulty levels
- Learning progression

### Interactive Play

`examples/play_game.py` provides a full CLI game interface:
- Player registration
- Round generation
- Interactive guessing
- Progress tracking
- Difficulty recommendations

## Contributing

To extend the game system:

### 1. Add New Scoring Factors

Edit `scoring/score_calculator.py`:

```python
def _calculate_custom_bonus(self, ...):
    # Add your scoring logic
    return bonus_points
```

### 2. Add New Feedback Types

Edit `feedback/feedback_generator.py`:

```python
def _generate_custom_tip(self, game_round):
    # Add your educational content
    return tip_text
```

### 3. Add Real Map Sources

Implement in `game/map_sourcer.py`:

```python
def fetch_from_library_of_congress(self, query):
    # Integrate with LOC API
    # Return List[MapMetadata]
```

## FAQ

**Q: Is this a trivia game?**
A: No. It's a historical reasoning trainer. You're learning to recognize clues, not memorize dates.

**Q: Why doesn't my exact guess always get 100 points?**
A: The system's estimate is probabilistic. Even if you guess correctly, the system might be uncertain, affecting confidence weighting.

**Q: How does difficulty progression work?**
A: Automatic. After 3 beginner rounds with 70%+ accuracy and 60+ avg score, you're promoted to intermediate.

**Q: Can I use my own maps?**
A: Yes! Use `RoundGenerator.generate_round_from_local_file(path)`.

**Q: Where are my stats stored?**
A: Locally in `data/player_stats/{your_name}.json`. Easy to delete or export.

**Q: Can I integrate this with a web app?**
A: Yes! The game engine is backend-only. Add Flask/FastAPI for a web interface.

## License

Same as main project.

---

**Ready to play?**

```bash
python examples/play_game.py
```
