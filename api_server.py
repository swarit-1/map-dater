"""
FastAPI backend for Map Dater web application.

Provides REST API endpoints for:
- Map analysis
- Game rounds
- Guess submission
"""

import sys
import uuid
from pathlib import Path
from typing import Union
from tempfile import NamedTemporaryFile

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pipeline import MapDaterPipeline
from game.game_engine import GameEngine
from game.game_models import UserGuess, DifficultyLevel


# Pydantic models for request/response
class Evidence(BaseModel):
    label: str
    valid_range: tuple[int, int]
    explanation: str


class DateEstimateResponse(BaseModel):
    date_range: tuple[int, int]
    most_likely_year: int
    confidence: float
    evidence: list[Evidence]


class GameRoundResponse(BaseModel):
    round_id: str
    map_description: str
    difficulty: str


class GameSubmitRequest(BaseModel):
    round_id: str
    guess: Union[int, tuple[int, int]]


class GameResultResponse(BaseModel):
    score: int
    was_accurate: bool
    feedback: list[str]
    system_estimate: dict[str, Union[tuple[int, int], int]] = Field(
        ...,
        description="System estimate with 'range' and 'most_likely' keys"
    )


# Create FastAPI app
app = FastAPI(
    title="Map Dater API",
    description="API for historical map dating and game functionality",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
pipeline = None
game_engines = {}  # Store game engines per session


def get_pipeline() -> MapDaterPipeline:
    """Lazy-load the pipeline to avoid slow startup."""
    global pipeline
    if pipeline is None:
        print("Initializing Map Dater pipeline...")
        pipeline = MapDaterPipeline(verbose=False)
        print("Pipeline ready!")
    return pipeline


def get_game_engine(session_id: str = "default") -> GameEngine:
    """Get or create a game engine for a session."""
    if session_id not in game_engines:
        game_engines[session_id] = GameEngine(
            player_id=session_id,
            storage_dir=None  # In-memory for now
        )
    return game_engines[session_id]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Map Dater API",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=DateEstimateResponse)
async def analyze_map(file: UploadFile = File(...)):
    """
    Analyze a map image and return date estimate.

    Args:
        file: Uploaded image file

    Returns:
        DateEstimateResponse with date range, confidence, and evidence
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save uploaded file temporarily
    try:
        with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Analyze the map
        pipe = get_pipeline()
        estimate = pipe.analyze_map(tmp_path)

        # Clean up temp file
        Path(tmp_path).unlink()

        # Convert to response format
        evidence_list = [
            Evidence(
                label=signal.description,
                valid_range=(signal.year_range.start, signal.year_range.end),
                explanation=signal.reasoning
            )
            for signal in estimate.signals[:5]  # Top 5 signals
        ]

        return DateEstimateResponse(
            date_range=(estimate.year_range.start, estimate.year_range.end),
            most_likely_year=estimate.most_likely_year,
            confidence=estimate.confidence,
            evidence=evidence_list
        )

    except Exception as e:
        print(f"Error analyzing map: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/game/start", response_model=GameRoundResponse)
async def start_game_round(difficulty: str = "beginner"):
    """
    Start a new game round.

    Args:
        difficulty: One of 'beginner', 'intermediate', 'expert'

    Returns:
        GameRoundResponse with round info
    """
    try:
        # Convert difficulty string to enum
        difficulty_map = {
            "beginner": DifficultyLevel.BEGINNER,
            "intermediate": DifficultyLevel.INTERMEDIATE,
            "expert": DifficultyLevel.EXPERT
        }

        if difficulty not in difficulty_map:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid difficulty. Must be one of: {list(difficulty_map.keys())}"
            )

        diff_level = difficulty_map[difficulty]

        # Get game engine and start round
        engine = get_game_engine()
        game_round = engine.start_new_round(difficulty=diff_level, use_mock=True)

        # Get description from metadata
        description = "Cold War era political map showing divided Europe"
        if hasattr(game_round, "map_metadata") and game_round.map_metadata and game_round.map_metadata.description:
            description = game_round.map_metadata.description

        return GameRoundResponse(
            round_id=game_round.round_id,
            map_description=description,
            difficulty=difficulty
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting game round: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start round: {str(e)}")


@app.post("/game/submit", response_model=GameResultResponse)
async def submit_game_guess(request: GameSubmitRequest):
    """
    Submit a guess for a game round.

    Args:
        request: Contains round_id and guess (year or range)

    Returns:
        GameResultResponse with score and feedback
    """
    try:
        # Get game engine
        engine = get_game_engine()

        # Create user guess
        if isinstance(request.guess, int):
            # Single year guess
            user_guess = UserGuess(
                is_single_year=True,
                single_year=request.guess,
                year_range=None
            )
        else:
            # Range guess
            from models import YearRange
            user_guess = UserGuess(
                is_single_year=False,
                single_year=None,
                year_range=YearRange(start=request.guess[0], end=request.guess[1])
            )

        # Submit guess
        result = engine.submit_guess(user_guess)

        # Convert to response format
        return GameResultResponse(
            score=result.score,
            was_accurate=result.was_accurate,
            feedback=result.feedback,
            system_estimate={
                "range": (
                    result.system_estimate.year_range.start,
                    result.system_estimate.year_range.end
                ),
                "most_likely": result.system_estimate.most_likely_year
            }
        )

    except Exception as e:
        print(f"Error submitting guess: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to submit guess: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("Starting Map Dater API server...")
    print("API will be available at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
