# Map Dater - Historical Map Dating System

A serious, explainable system for estimating when historical maps were created by analyzing their visual and textual features.

## Overview

Map Dater is a backend system designed for digital humanities, museums, and archival research. It provides:

- **Automated date estimation** from map images
- **Explainable AI** - every estimate comes with clear reasoning
- **Modular architecture** - easy to extend with better models
- **Probabilistic inference** - handles uncertainty and conflicting signals
- **Museum-grade quality** - designed for academic and professional use

## Key Features

### Current Capabilities

✅ **Enhanced OCR** - Advanced text extraction with adaptive preprocessing, upscaling, and binarization
✅ **OCR Visualization** - Debug tools showing detected text, word maps, and confidence heatmaps
✅ **AI-Powered Visual Analysis** 🤖 - Uses Claude's vision API to analyze maps for:
   - Printing techniques (hand-drawn, lithography, offset, digital)
   - Typography and font characteristics
   - Color palettes and printing quality
   - Border and decoration styles
   - Infrastructure presence (railroads, highways, etc.)
   - Cartographic conventions and style
✅ **Historical Entity Recognition** - Identifies countries, cities, regions with temporal validity
✅ **Knowledge Base** - 30+ historical entities with precise date ranges
✅ **Probabilistic Date Estimation** - Combines OCR, AI vision, and entity signals
✅ **Explanation Generation** - Human-readable justifications for all estimates
✅ **Signal Conflict Detection** - Identifies anachronistic or composite maps
✅ **Interactive Game Mode** 🎮 - Educational gamification layer for learning historical reasoning (See [GAME_README.md](GAME_README.md))

### Future Extensions

🔜 **Custom ML Models** - Train specialized classifiers on historical map datasets
🔜 **Multi-language OCR** - Support for non-Latin scripts
🔜 **Batch Processing** - Analyze entire archival collections

## Architecture

### Backend (Python)

```
src/
├── ingestion/          # Image preprocessing (deskew, denoise, contrast)
├── ocr/               # Text extraction and normalization + visualization
├── entities/          # Historical entity recognition
├── knowledge/         # Historical knowledge base
├── visual_features/   # AI-powered visual analysis with Claude
├── inference/         # Probabilistic date estimation
├── explanations/      # Human-readable explanation generation
├── game/              # Game mode logic and scoring
├── feedback/          # Hint and feedback generation
└── pipeline.py        # End-to-end orchestrator
```

### Frontend (React/TypeScript)

```
frontend/
├── src/
│   ├── pages/          # Home, Analyze, Game pages
│   ├── components/     # Reusable React components
│   ├── api/            # API client (currently mock data)
│   ├── styles/         # Tailwind CSS configuration
│   └── utils/          # Helper functions
├── public/             # Static assets
└── package.json        # Dependencies and scripts
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR**
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`
3. **Anthropic API Key** (for AI visual analysis)
   - Sign up at [console.anthropic.com](https://console.anthropic.com)
   - Get your API key from the dashboard

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `anthropic` - For AI-powered visual analysis with Claude
- `python-dotenv` - For environment variable management
- `opencv-python` - Enhanced image preprocessing
- `pytesseract` - OCR capabilities

### Configure Environment

**Option 1: Interactive Setup (Recommended)**
```bash
python setup_env.py
```

**Option 2: Manual Setup**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your-key-here
```

The `.env` file contains all configuration options:
- **Required:** `ANTHROPIC_API_KEY` - For AI visual analysis
- **Optional:** OCR settings, preprocessing options, output paths
- See [ENV_SETUP.md](ENV_SETUP.md) for detailed configuration guide
- See `.env.example` for all available options with documentation

## Quick Start

### Backend (Command Line)

#### Run the Demo (No Image Required)

```bash
python examples/demo.py
```

This demonstrates the system using mock data:
- Knowledge base queries
- Date estimation from entities
- Conflict detection
- Explanation generation

#### Create Mock Maps for Testing

```bash
python examples/create_mock_map.py
```

This generates test map images in `data/sample_maps/`.

#### Analyze a Real Map

```python
from src.pipeline import MapDaterPipeline

# Initialize pipeline
pipeline = MapDaterPipeline(verbose=True)

# Analyze a map
estimate = pipeline.analyze_and_print('path/to/map.jpg')

# Access results
print(f"Year range: {estimate.year_range}")
print(f"Confidence: {estimate.confidence}")
print(f"Most likely year: {estimate.most_likely_year}")
```

### Frontend (Web Interface)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Open your browser to **http://localhost:5173**

**Frontend Pages:**
- `/` - Home page with navigation
- `/analyze` - Upload and analyze maps
- `/game` - Interactive map dating game

### Try AI-Powered Analysis 🤖

Leverage Claude's vision capabilities for advanced visual analysis:

```bash
# First time setup: Configure your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your-key-here

# Run AI analysis demo
python examples/ai_analysis_demo.py path/to/map.jpg

# OCR visualization only
python examples/ai_analysis_demo.py path/to/map.jpg --mode ocr

# AI visual analysis only
python examples/ai_analysis_demo.py path/to/map.jpg --mode ai

# Combined analysis (recommended)
python examples/ai_analysis_demo.py path/to/map.jpg --mode combined
```

**New AI Capabilities:**
- Analyzes printing techniques and identifies era-specific characteristics
- Detects typography styles and font technologies
- Evaluates color palettes and printing quality
- Identifies infrastructure and temporal markers
- Provides detailed reasoning for all visual assessments

**OCR Visualizations:**
- Bounding boxes around detected text
- Word maps showing spatial text layout
- Confidence heatmaps for OCR quality
- Summary views combining all visualizations

### Play the Interactive Game 🎮

Turn learning into a game! Test your historical knowledge and improve over time.

**Option 1: Web Interface (Recommended)**
```bash
cd frontend
npm run dev
# Navigate to http://localhost:5173/game
```

**Option 2: Command Line**
```bash
# Interactive game mode
python examples/play_game.py

# Or watch a demo
python examples/game_demo.py
```

**Features:**
- Guess when maps were created
- Get scored on accuracy
- Receive educational feedback
- Track progress and difficulty progression
- Learn to recognize historical clues

See [GAME_README.md](GAME_README.md) for complete game documentation.

## Example Output

```
ESTIMATED DATE: 1949-1990
Most likely year: 1970
Confidence: 87% (high)

EVIDENCE SUMMARY:
  - 2 historical entities
  - 1 textual reference

DETAILED EVIDENCE:
  1. → East Germany
     Range: 1949-1990 (confidence: 95%)
     Reasoning: East Germany existed from 1949 to 1990

  2. → USSR
     Range: 1922-1991 (confidence: 95%)
     Reasoning: USSR existed from 1922 to 1991

  3. 📝 Year reference: 1975
     Range: 1965-1985 (confidence: 60%)
     Reasoning: Text contains year 1975

CONFIDENCE ANALYSIS:
  ✓ Narrow range: 41 year window
  ✓ Multiple entities (2) provide cross-validation
  ✓ High-confidence signals
```

## How It Works

### 1. Image Preprocessing

Maps are preprocessed to optimize OCR:
- **Deskewing** - Correct rotation
- **Denoising** - Remove scan artifacts
- **Contrast enhancement** - Improve text readability

### 2. Text Extraction

Tesseract OCR extracts all text with:
- Bounding box coordinates
- Confidence scores
- Text normalization (case, punctuation, common OCR errors)

### 3. Entity Recognition

Extracted text is matched against a knowledge base of historical entities:

| Entity | Type | Valid Range | Notes |
|--------|------|-------------|-------|
| USSR | country | 1922-1991 | Multiple alternative names |
| Constantinople | city | 330-1930 | Renamed to Istanbul |
| East Germany | country | 1949-1990 | German Democratic Republic |
| Leningrad | city | 1924-1991 | St. Petersburg renamed |

### 4. Date Estimation

A probabilistic inference engine combines signals:

- **Entity constraints** (high confidence) - Entities must have existed
- **Year references** (medium confidence) - Years found in text
- **Visual features** (variable confidence) - Stubbed for future ML models

The system computes:
- **Temporal intersection** - Years when all entities coexisted
- **Weighted voting** - More constraining signals have more influence
- **Confidence score** - Based on signal agreement and range narrowness

### 5. Explanation Generation

Every estimate includes:
- **Evidence list** - All contributing signals with reasoning
- **Confidence analysis** - Why the confidence is high/low
- **Caveats** - Limitations and potential issues
- **JSON export** - Machine-readable format for APIs

## Extending the System

### Adding New Entities

```python
from knowledge import HistoricalKnowledgeBase
from models import HistoricalEntity, YearRange

kb = HistoricalKnowledgeBase()

# Add a new entity
entity = HistoricalEntity(
    name="Siam",
    canonical_name="Siam",
    entity_type="country",
    valid_range=YearRange(1350, 1939),
    alternative_names=["Kingdom of Siam"]
)

kb.add_entity(entity)

# Or load from JSON
kb.load_from_json('my_entities.json')
```

### Implementing Visual Features

The `visual_features/` module is designed for easy extension:

```python
from visual_features import VisualFeatureExtractor
from models import VisualFeature, YearRange

class MyCustomExtractor(VisualFeatureExtractor):
    def _extract_border_style(self, image):
        # Replace stub with real ML model
        prediction = my_model.predict(image)

        return [VisualFeature(
            feature_type='border_style',
            description=f'Detected {prediction.style}',
            confidence=prediction.confidence,
            year_range=YearRange(prediction.start, prediction.end)
        )]
```

See `src/visual_features/feature_extractor.py` for full extension guide.

## Testing

Run unit tests:

```bash
python -m pytest tests/unit/
```

Run a specific test:

```bash
python -m pytest tests/unit/test_models.py -v
```

## Use Cases

### Digital Humanities
- Date undated archival materials
- Verify claimed publication dates
- Identify anachronistic maps

### Museums
- Catalog map collections
- Generate provenance documentation
- Educational exhibits with explanations

### Cartographic Research
- Track evolution of geographic knowledge
- Study naming conventions over time
- Analyze cartographic production techniques

## Design Principles

1. **Explainability First** - Every estimate must be justifiable
2. **Uncertainty is OK** - Wide ranges are better than false precision
3. **Modular Architecture** - Easy to swap components or add features
4. **No Hallucination** - Never invent dates without evidence
5. **Museum-Grade** - Suitable for professional archival work

## Limitations

### Current Limitations

- **API costs** - AI visual analysis requires Claude API credits
- **Western maps bias** - Knowledge base focuses on 20th century Europe
- **OCR language** - Currently optimized for English text
- **Processing time** - AI analysis takes 10-30 seconds per map

### Known Edge Cases

- **Composite maps** - Show entities from different eras (will be flagged)
- **Historical maps** - Maps depicting earlier eras (use textual clues)
- **Reproductions** - Modern reproductions of old maps (hard to distinguish)

## Roadmap

### Phase 1: Core System ✅
- ✅ Image preprocessing
- ✅ OCR and text extraction
- ✅ Entity recognition
- ✅ Knowledge base
- ✅ Probabilistic inference
- ✅ Explanation generation

### Phase 2: Visual Analysis ✅
- ✅ AI-powered visual feature extraction
- ✅ Printing technique detection
- ✅ Typography analysis
- ✅ Color palette dating
- ✅ Infrastructure detection
- ✅ OCR visualization and debugging tools

### Phase 3: Advanced Features
- Geographic entity disambiguation
- Multi-language OCR
- Comparative dating (similarity to known maps)
- Confidence calibration with ground truth

## Documentation

- **[README.md](README.md)** - Main documentation (you are here)
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[ENV_SETUP.md](ENV_SETUP.md)** - Detailed environment configuration guide
- **[GAME_README.md](GAME_README.md)** - Interactive game mode documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to extend the system
- **[GAMIFICATION_SUMMARY.md](GAMIFICATION_SUMMARY.md)** - Gamification features

## Contributing

This is a research tool designed for extension. Key areas for contribution:

1. **Expand Knowledge Base** - Add more entities, especially non-Western
2. **Improve OCR** - Better handling of historical fonts
3. **Visual Features** - Enhance AI analysis prompts
4. **Ground Truth Data** - Collect dated maps for validation

## Citation

If you use this system in research, please cite:

```
Map Dater: A Probabilistic System for Dating Historical Maps
[Your Name], 2024
```

## License

[Specify license]

## Acknowledgments

Built with:
- **Tesseract OCR** - Text extraction
- **OpenCV** - Image preprocessing
- **Python** - Core implementation

## Contact

[Your contact information]

---

**Remember**: This is a research tool. Always verify estimates with domain expertise before making claims about historical materials.
