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

✅ **Text Extraction (OCR)** - Extracts and normalizes text from map images using Tesseract
✅ **Historical Entity Recognition** - Identifies countries, cities, regions with temporal validity
✅ **Knowledge Base** - 30+ historical entities with precise date ranges
✅ **Probabilistic Date Estimation** - Combines multiple signals with confidence weighting
✅ **Explanation Generation** - Human-readable justifications for all estimates
✅ **Signal Conflict Detection** - Identifies anachronistic or composite maps
✅ **Interactive Game Mode** 🎮 - Educational gamification layer for learning historical reasoning (See [GAME_README.md](GAME_README.md))

### Future Extensions

🔜 **Visual Feature Analysis** (stubbed) - Border styles, typography, color palettes
🔜 **ML-based Dating** - Train classifiers on printing techniques and cartographic styles
🔜 **Infrastructure Detection** - Railroads, highways, airports as temporal markers

## Architecture

```
src/
├── ingestion/          # Image preprocessing (deskew, denoise, contrast)
├── ocr/               # Text extraction and normalization
├── entities/          # Historical entity recognition
├── knowledge/         # Historical knowledge base
├── visual_features/   # Visual analysis (stubbed for ML models)
├── inference/         # Probabilistic date estimation
├── explanations/      # Human-readable explanation generation
└── pipeline.py        # End-to-end orchestrator
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR**
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Run the Demo (No Image Required)

```bash
python examples/demo.py
```

This demonstrates the system using mock data:
- Knowledge base queries
- Date estimation from entities
- Conflict detection
- Explanation generation

### Create Mock Maps for Testing

```bash
python examples/create_mock_map.py
```

This generates test map images in `data/sample_maps/`.

### Analyze a Real Map

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

### Play the Interactive Game 🎮

Turn learning into a game! Test your historical knowledge and improve over time.

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

- **Text-only dating** - Visual features not yet implemented
- **Western maps bias** - Knowledge base focuses on 20th century Europe
- **OCR quality dependent** - Poor scans may miss critical text
- **No style analysis** - Can't distinguish hand-drawn vs. digital yet

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

### Phase 2: Visual Analysis 🔜
- 🔜 Border style classifier
- 🔜 Typography analysis
- 🔜 Color palette dating
- 🔜 Projection detection

### Phase 3: Advanced Features
- Geographic entity disambiguation
- Multi-language OCR
- Comparative dating (similarity to known maps)
- Confidence calibration with ground truth

## Contributing

This is a research tool designed for extension. Key areas for contribution:

1. **Expand Knowledge Base** - Add more entities, especially non-Western
2. **Improve OCR** - Better handling of historical fonts
3. **Visual Features** - Implement ML models for stub methods
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
