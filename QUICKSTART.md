# Quick Start Guide

Get Map Dater running in 5 minutes.

## Installation

### 1. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location
- Add to PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Immediate Testing (No Map Required)

### Run the Demo

```bash
python examples/demo.py
```

This will show you:
- Knowledge base queries
- Date estimation from entities
- Explanation generation
- JSON export

**Expected output:**
```
============================================================
KNOWLEDGE BASE DEMO
============================================================

Total entities: 30+

Sample countries:
  - Soviet Union: 1922-1991
  - East Germany: 1949-1990
  ...

ESTIMATED DATE: 1949-1990
Most likely year: 1970
Confidence: 87% (high)
```

## Testing with Mock Maps

### Create Test Maps

```bash
python examples/create_mock_map.py
```

This creates three test maps in `data/sample_maps/`:
- `mock_map_cold_war.png` - Shows USSR, East/West Germany (1949-1990)
- `mock_map_post_ww1.png` - Shows Czechoslovakia, Constantinople (1918-1930)
- `mock_map_modern.png` - Shows Czech Republic, Russia, Istanbul (1995+)

### Analyze a Mock Map

```bash
python main.py data/sample_maps/mock_map_cold_war.png
```

**Expected output:**
```
ESTIMATED DATE: 1949-1990
Most likely year: 1970
Confidence: 87% (high)

EVIDENCE SUMMARY:
  - 2 historical entities

DETAILED EVIDENCE:
  1. → East Germany
     Range: 1949-1990 (confidence: 95%)
     Reasoning: East Germany existed from 1949 to 1990

  2. → USSR
     Range: 1922-1991 (confidence: 95%)
     Reasoning: USSR existed from 1922 to 1991
```

## Analyzing Real Maps

### Basic Usage

```bash
python main.py path/to/your/map.jpg
```

### Save Preprocessed Image

```bash
python main.py map.jpg --save-processed cleaned.png
```

### Get JSON Output

```bash
python main.py map.jpg --json > results.json
```

### Verbose Mode (See All Steps)

```bash
python main.py map.jpg --verbose
```

## Python API Usage

### Simple Example

```python
from src.pipeline import MapDaterPipeline

# Initialize
pipeline = MapDaterPipeline()

# Analyze
estimate = pipeline.analyze_map('map.jpg')

# Results
print(f"Date: {estimate.year_range}")
print(f"Confidence: {estimate.confidence:.0%}")
print(estimate.explanation)
```

### With Custom Knowledge Base

```python
from src.pipeline import MapDaterPipeline
from src.knowledge import HistoricalKnowledgeBase

# Load custom entities
kb = HistoricalKnowledgeBase()
kb.load_from_json('my_entities.json')

# Use custom KB
pipeline = MapDaterPipeline(knowledge_base=kb)
estimate = pipeline.analyze_map('map.jpg')
```

## Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/unit/test_models.py -v

# With coverage
python -m pytest tests/ --cov=src
```

## Troubleshooting

### "Tesseract not found"
- Make sure Tesseract is installed and in PATH
- Windows: Check `C:\Program Files\Tesseract-OCR\tesseract.exe` exists
- Test: `tesseract --version`

### "No entities found"
- OCR may not be extracting text
- Try `--save-processed` to see cleaned image
- Check image quality (needs to be readable)
- Verify text is in English

### "Conflicting signals"
- Map may show entities from different eras (anachronistic)
- This is intentionally detected as unusual
- Check if map is a historical map (depicting past eras)

### Poor Accuracy
- Knowledge base may not contain relevant entities
- See `examples/expand_knowledge_base.py` to add more
- Visual features not yet implemented (stubbed)

## Next Steps

1. **Expand Knowledge Base** - Add entities for your region/era
   ```bash
   python examples/expand_knowledge_base.py
   ```

2. **Read Documentation**
   - `README.md` - Full system documentation
   - `CONTRIBUTING.md` - How to extend the system
   - `src/visual_features/feature_extractor.py` - ML extension points

3. **Try Batch Processing**
   ```python
   pipeline = MapDaterPipeline()
   results = pipeline.batch_analyze(['map1.jpg', 'map2.jpg'])
   ```

## Getting Help

- Check `README.md` for detailed documentation
- See examples in `examples/` directory
- Open an issue on GitHub

## What This System Does

✅ Extracts text from map images (OCR)
✅ Identifies historical entities (countries, cities)
✅ Estimates creation date from entity validity
✅ Generates human-readable explanations
✅ Detects anachronistic/conflicting entities

## What This System Doesn't Do (Yet)

❌ Visual style analysis (stubbed - ready for ML models)
❌ Non-English text
❌ Ancient maps (pre-1500s)
❌ Distinguish reproductions from originals

See `CONTRIBUTING.md` for how to add these features.
