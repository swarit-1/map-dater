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
    map_image: Optional[str] = None  # Base64 encoded SVG/PNG image


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

    except ValueError as e:
        # Handle specific analysis errors (like "No historical entities found")
        error_msg = str(e)
        print(f"Analysis error: {error_msg}")
        if "No historical entities found" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Could not identify any historical features on this map. Please upload a clear image of a historical map with visible country names, borders, or other datable features."
            )
        raise HTTPException(status_code=400, detail=f"Analysis error: {error_msg}")
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
        GameRoundResponse with round info and map image
    """
    import random

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

        # Generate a random year based on difficulty
        # Beginner: Major periods with clear identifiable features (1945+)
        # Intermediate: More challenging periods (1920-1960)
        # Expert: Any period including pre-WWII
        if diff_level == DifficultyLevel.BEGINNER:
            # Post-WWII era with clear Cold War divisions
            target_year = random.choice([1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985])
        elif diff_level == DifficultyLevel.INTERMEDIATE:
            # Interwar and early Cold War
            target_year = random.choice([1920, 1925, 1930, 1935, 1950, 1955, 1990, 1995, 2000])
        else:  # Expert
            # Any era including challenging transitions
            target_year = random.choice([1914, 1918, 1922, 1938, 1945, 1949, 1989, 1991, 2010])

        # Generate a map image for this year with date hidden
        map_image_base64 = None
        description = "Examine this historical world map and guess when it was created"
        try:
            # Generate map with hidden date
            map_result = generate_map_from_date(
                str(target_year),
                output_format="svg",
                hide_date_in_title=True
            )
            if map_result and map_result.image_data:
                map_image_base64 = base64.b64encode(map_result.image_data).decode('utf-8')
        except Exception as map_error:
            print(f"Warning: Could not generate map image: {map_error}")
            # Continue without map image - frontend will show placeholder

        # Get game engine and start round with the generated year
        engine = get_game_engine()

        # Create a custom mock round with the random year
        from knowledge import HistoricalKnowledgeBase
        from models import DateEstimate, DateSignal, SignalType, YearRange
        from game.game_models import GameRound, MapMetadata

        kb = HistoricalKnowledgeBase()

        # Find entities valid for this year
        valid_entities = []
        for name in ['USSR', 'Soviet Union', 'East Germany', 'West Germany',
                     'Yugoslavia', 'Czechoslovakia', 'Ottoman Empire', 'Austria-Hungary']:
            entity = kb.find_by_name(name)
            if entity and entity.valid_range.start <= target_year <= entity.valid_range.end:
                valid_entities.append(entity)

        # Create signals from valid entities
        signals = []
        for entity in valid_entities[:5]:  # Limit to 5 signals
            signal = DateSignal(
                signal_type=SignalType.ENTITY,
                description=f"{entity.entity_type.capitalize()}: {entity.canonical_name}",
                year_range=entity.valid_range,
                confidence=0.95,
                source=f"entity:{entity.canonical_name}",
                reasoning=f"{entity.canonical_name} existed from {entity.valid_range.start} to {entity.valid_range.end}"
            )
            signals.append(signal)

        # Calculate the year range based on entity overlaps
        if valid_entities:
            range_start = max(e.valid_range.start for e in valid_entities)
            range_end = min(e.valid_range.end for e in valid_entities)
        else:
            range_start = target_year - 10
            range_end = target_year + 10

        # Create estimate
        estimate = DateEstimate(
            year_range=YearRange(range_start, range_end),
            confidence=0.85,
            signals=signals,
            explanation="Estimated based on political entities visible on map",
            most_likely_year=target_year
        )

        # Create mock metadata
        map_metadata = MapMetadata(
            map_id=f"game_{target_year}_{random.randint(1000, 9999)}",
            source="Generated Map",
            region="World",
            description=description
        )

        # Create game round
        game_round = GameRound.create(
            map_metadata=map_metadata,
            system_estimate=estimate,
            difficulty=diff_level
        )

        # Store in engine for later submission
        engine.current_round = game_round

        return GameRoundResponse(
            round_id=game_round.round_id,
            map_description=description,
            difficulty=difficulty,
            map_image=map_image_base64
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
        from models import YearRange
        if isinstance(request.guess, int):
            # Single year guess
            user_guess = UserGuess(year=request.guess)
        else:
            # Range guess
            user_guess = UserGuess(
                year_range=YearRange(start=request.guess[0], end=request.guess[1])
            )

        # Submit guess
        result = engine.submit_guess(user_guess)

        # Convert to response format
        # result.score is a ScoreBreakdown object, extract final_score
        final_score = int(result.score.final_score) if hasattr(result.score, 'final_score') else int(result.score)

        # result.feedback can be a string or list
        feedback_list = result.feedback if isinstance(result.feedback, list) else [result.feedback]

        return GameResultResponse(
            score=final_score,
            was_accurate=result.was_accurate,
            feedback=feedback_list,
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
