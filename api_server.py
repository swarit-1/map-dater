"""
FastAPI backend for Map Dater web application.

Provides REST API endpoints for:
- Map analysis (image -> date)
- Map generation (date -> image)
- Game rounds
- Guess submission
"""

import sys
import uuid
import base64
from pathlib import Path
from typing import Union, Optional, List
from tempfile import NamedTemporaryFile

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from pipeline import MapDaterPipeline
from game.game_engine import GameEngine
from game.game_models import UserGuess, DifficultyLevel
from map_generation import generate_map_from_date, MapGenerationPipeline
from map_generation.date_parser import DateParseError


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


# Map Generation Models
class MapGenerationEntity(BaseModel):
    """Entity shown on a generated map."""
    name: str
    canonical_name: str
    type: str
    valid_range: tuple[int, int]
    confidence: float


class UncertaintyFactor(BaseModel):
    """A factor contributing to map uncertainty."""
    type: str
    description: str
    severity: float
    affected_entities: list[str] = []
    recommendations: list[str] = []


class MapGenerationUncertainty(BaseModel):
    """Uncertainty assessment for a generated map."""
    uncertainty_score: float
    confidence: float
    risk_level: str
    factors: list[UncertaintyFactor]
    notes: list[str]


class MapGenerationResponse(BaseModel):
    """Response for map generation endpoint."""
    date_range: tuple[int, int]
    entities_shown: list[MapGenerationEntity]
    assumptions: list[str]
    uncertainty: MapGenerationUncertainty
    confidence: float
    risk_level: str
    image_base64: Optional[str] = None  # Base64 encoded image (if requested)
    metadata: dict = {}


class MapGenerationPreview(BaseModel):
    """Preview of what would be generated (no image)."""
    date_range: tuple[int, int]
    is_single_year: bool
    midpoint: int
    entities_count: int
    dominant_entities: list[str]
    conflicts: list[dict]
    risk_assessment: dict
    assumptions: list[str]


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


# =============================================================================
# Map Generation Endpoints (Date -> Map)
# =============================================================================

# Global map generation pipeline
map_gen_pipeline = None


def get_map_gen_pipeline() -> MapGenerationPipeline:
    """Lazy-load the map generation pipeline."""
    global map_gen_pipeline
    if map_gen_pipeline is None:
        print("Initializing Map Generation pipeline...")
        map_gen_pipeline = MapGenerationPipeline(verbose=False)
        print("Map Generation pipeline ready!")
    return map_gen_pipeline


@app.post("/generate", response_model=MapGenerationResponse)
async def generate_map(
    date: str = Query(..., description="Date or date range (e.g., '1914' or '1918-1939')"),
    include_image: bool = Query(True, description="Include base64 encoded image in response"),
    format: str = Query("svg", description="Image format: 'png' or 'svg'")
):
    """
    Generate a historical map for a given date or date range.

    This is the inverse of map analysis:
    - Map analysis: Image -> Date estimate
    - Map generation: Date -> Image

    Args:
        date: Year (e.g., "1914") or range (e.g., "1918-1939")
        include_image: Whether to include base64 image in response
        format: Output format ('png' or 'svg')

    Returns:
        MapGenerationResponse with entities, assumptions, uncertainty, and optionally image
    """
    try:
        pipeline = get_map_gen_pipeline()
        result = pipeline.generate(date, output_format=format)

        # Convert entities to response format
        entities = [
            MapGenerationEntity(
                name=e['name'],
                canonical_name=e['canonical_name'],
                type=e['type'],
                valid_range=tuple(e['valid_range']),
                confidence=e['confidence']
            )
            for e in result.entities_shown
        ]

        # Convert uncertainty factors
        factors = [
            UncertaintyFactor(
                type=f.factor_type,
                description=f.description,
                severity=f.severity,
                affected_entities=f.affected_entities,
                recommendations=f.recommendations
            )
            for f in result.uncertainty.factors
        ]

        uncertainty = MapGenerationUncertainty(
            uncertainty_score=result.uncertainty.overall_score,
            confidence=result.uncertainty.confidence,
            risk_level=result.uncertainty.risk_level,
            factors=factors,
            notes=result.uncertainty.notes
        )

        # Base64 encode image if requested
        image_base64 = None
        if include_image:
            image_base64 = base64.b64encode(result.image_data).decode('utf-8')

        return MapGenerationResponse(
            date_range=(result.date_range.start, result.date_range.end),
            entities_shown=entities,
            assumptions=result.assumptions,
            uncertainty=uncertainty,
            confidence=result.confidence,
            risk_level=result.risk_level,
            image_base64=image_base64,
            metadata=result.metadata
        )

    except DateParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error generating map: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Map generation failed: {str(e)}")


@app.get("/generate/image")
async def generate_map_image(
    date: str = Query(..., description="Date or date range (e.g., '1914' or '1918-1939')"),
    format: str = Query("svg", description="Image format: 'png' or 'svg'")
):
    """
    Generate and return just the map image.

    Returns the image directly (not JSON wrapped) for easy embedding.

    Args:
        date: Year (e.g., "1914") or range (e.g., "1918-1939")
        format: Output format ('png' or 'svg')

    Returns:
        Image file (PNG or SVG)
    """
    try:
        pipeline = get_map_gen_pipeline()
        result = pipeline.generate(date, output_format=format)

        if format.lower() == 'svg':
            return Response(
                content=result.image_data,
                media_type="image/svg+xml",
                headers={"Content-Disposition": f"inline; filename=map_{date}.svg"}
            )
        else:
            return Response(
                content=result.image_data,
                media_type="image/png",
                headers={"Content-Disposition": f"inline; filename=map_{date}.png"}
            )

    except DateParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error generating map image: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Map generation failed: {str(e)}")


@app.get("/generate/preview", response_model=MapGenerationPreview)
async def preview_map_generation(
    date: str = Query(..., description="Date or date range (e.g., '1914' or '1918-1939')")
):
    """
    Preview what would be generated without actually rendering.

    Useful for:
    - Validating date input
    - Quick uncertainty assessment
    - Understanding what entities would be shown

    Args:
        date: Year (e.g., "1914") or range (e.g., "1918-1939")

    Returns:
        MapGenerationPreview with entities and risk assessment
    """
    try:
        pipeline = get_map_gen_pipeline()
        preview = pipeline.preview(date)

        return MapGenerationPreview(
            date_range=tuple(preview['date_range']),
            is_single_year=preview['is_single_year'],
            midpoint=preview['midpoint'],
            entities_count=preview['entities_count'],
            dominant_entities=preview['dominant_entities'],
            conflicts=preview['conflicts'],
            risk_assessment=preview['risk_assessment'],
            assumptions=preview['assumptions']
        )

    except DateParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error previewing map: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@app.get("/generate/entities")
async def get_entities_for_year(
    year: int = Query(..., description="Year to query", ge=1500, le=2100)
):
    """
    Get all known entities that existed in a specific year.

    Useful for understanding what political entities the system knows about.

    Args:
        year: Year to query (1500-2100)

    Returns:
        List of entities valid in that year
    """
    try:
        pipeline = get_map_gen_pipeline()
        entities = pipeline.get_entities_for_year(year)

        return {
            "year": year,
            "entity_count": len(entities),
            "entities": entities
        }

    except Exception as e:
        print(f"Error getting entities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("Starting Map Dater API server...")
    print("API will be available at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
