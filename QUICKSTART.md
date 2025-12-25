# Quick Start Guide

Get Map Dater running in 5 minutes.

Map Dater has two components:
- **Backend (Python)**: OCR, entity recognition, AI visual analysis, game engine
- **Frontend (React)**: Web interface for analysis and game mode

## Installation

### Backend Setup (Python)

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

### 3. Configure Environment (Required for AI Features)

**Option A: Interactive Setup (Easiest)**
```bash
python setup_env.py
```
This script guides you through all configuration options.

**Option B: Manual Setup**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get API key from: https://console.anthropic.com
```

**Edit `.env` file:**
```ini
# Required for AI visual analysis
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional settings (see .env.example for all options)
# PREPROCESSING_UPSCALE=1.5
# OCR_CONFIDENCE_THRESHOLD=0.3
```

**Why use .env?**
- ✅ Keeps API keys secure and out of version control
- ✅ Easy to manage different configurations
- ✅ All settings documented in one place
- ✅ No need to set environment variables manually

**For detailed configuration guide:** See [ENV_SETUP.md](ENV_SETUP.md)

### Frontend Setup (React)

#### 1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Start Development Server

```bash
npm run dev
```

The frontend will start on **http://localhost:5173**

**Available Frontend Scripts:**
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

#### Frontend Features

The web interface includes three pages:

1. **Home (/)** - Overview and navigation
2. **Analyze (/analyze)** - Upload and analyze historical maps
3. **Game (/game)** - Interactive map dating game

**Note:** The frontend currently uses mock API responses. To connect to the Python backend, you'll need to set up API endpoints (see Backend Integration section below).

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

### NEW: AI-Powered Analysis with Visualization

**First:** Make sure you've configured your `.env` file (see step 3 above)

Run the enhanced analysis demo with OCR visualization and AI vision:

```bash
# Full analysis with AI and visualizations (recommended)
python examples/ai_analysis_demo.py map.jpg --mode combined

# Just OCR visualization (no API key needed)
python examples/ai_analysis_demo.py map.jpg --mode ocr

# Just AI visual analysis
python examples/ai_analysis_demo.py map.jpg --mode ai
```

The script automatically loads settings from `.env` file.

This creates visualizations in `data/output/`:
- `ocr_bboxes.png` - Shows detected text with bounding boxes
- `word_map.png` - Text-only view showing spatial layout
- `confidence_heatmap.png` - OCR quality across the image
- `ocr_summary.png` - Combined view of all visualizations

**AI Analysis Provides:**
- Printing technique detection (hand-drawn, lithography, digital, etc.)
- Typography and font analysis
- Color palette dating
- Border style characteristics
- Infrastructure detection (railroads, highways, airports)
- Detailed reasoning for all assessments

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

### NEW: With AI Visual Analysis

```python
from src.ingestion import ImagePreprocessor
from src.ocr import TextExtractor, OCRVisualizer
from src.visual_features import AIVisualAnalyzer

# Enhanced preprocessing
preprocessor = ImagePreprocessor(
    apply_deskew=True,
    apply_denoise=True,
    enhance_contrast=True,
    apply_binarization=False,
    upscale_factor=1.5  # Upscale for better OCR
)

processed = preprocessor.process('map.jpg')

# Extract and visualize text
extractor = TextExtractor()
text_blocks = extractor.extract_text(processed)

visualizer = OCRVisualizer()
visualizer.create_summary_visualization(
    processed,
    text_blocks,
    'output_summary.png'
)

# AI visual analysis
analyzer = AIVisualAnalyzer()  # Uses ANTHROPIC_API_KEY env var
visual_features = analyzer.analyze_map_features(processed)

for feature in visual_features:
    print(f"{feature.feature_type}: {feature.description}")
    print(f"  Date range: {feature.year_range}")
    print(f"  Confidence: {feature.confidence:.0%}")
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

### "ANTHROPIC_API_KEY not found"
- Make sure you've created `.env` file: `cp .env.example .env`
- Edit `.env` and add your API key
- Get API key from: https://console.anthropic.com
- Verify `.env` is in the project root directory

### "Tesseract not found"
- Make sure Tesseract is installed and in PATH
- Windows: Check `C:\Program Files\Tesseract-OCR\tesseract.exe` exists
- Test: `tesseract --version`
- Optional: Set path in `.env`: `TESSERACT_CMD=/path/to/tesseract`

### "No entities found"
- OCR may not be extracting text
- Try `--save-processed` to see cleaned image
- Check image quality (needs to be readable)
- Verify text is in English

### "Conflicting signals"
- Map may show entities from different eras (anachronistic)
- This is intentionally detected as unusual
- Check if map is a historical map (depicting past eras)

### Poor OCR Quality
- Try preprocessing with different settings:
  ```python
  preprocessor = ImagePreprocessor(
      apply_binarization=True,  # Try black/white conversion
      upscale_factor=2.0        # Upscale 2x for better OCR
  )
  ```
- Use OCR visualization to debug: `--mode ocr`
- Check `data/output/confidence_heatmap.png` for problem areas

### Poor Accuracy
- Knowledge base may not contain relevant entities
- See `examples/expand_knowledge_base.py` to add more
- Enable AI visual analysis for better results (requires API key)

## Quick Start Summary

### Backend Only (Command Line)
```bash
# 1. Install and configure
pip install -r requirements.txt
python setup_env.py

# 2. Run analysis
python examples/ai_analysis_demo.py map.jpg --mode combined
```

### Frontend Only (Web Interface)
```bash
# 1. Install frontend
cd frontend
npm install

# 2. Start dev server
npm run dev

# 3. Open browser to http://localhost:5173
```

### Both (Full Stack)
```bash
# Terminal 1: Backend
python -m src.api.server  # (when implemented)

# Terminal 2: Frontend
cd frontend && npm run dev
```

## Next Steps

1. **Try the Web Interface**
   ```bash
   cd frontend
   npm run dev
   # Open http://localhost:5173
   ```

2. **Expand Knowledge Base** - Add entities for your region/era
   ```bash
   python examples/expand_knowledge_base.py
   ```

3. **Read Documentation**
   - `README.md` - Full system documentation
   - `ENV_SETUP.md` - Configuration guide
   - `CONTRIBUTING.md` - How to extend the system
   - `GAME_README.md` - Game mode details

4. **Try Batch Processing**
   ```python
   pipeline = MapDaterPipeline()
   results = pipeline.batch_analyze(['map1.jpg', 'map2.jpg'])
   ```

## Getting Help

- Check `README.md` for detailed documentation
- See examples in `examples/` directory
- Open an issue on GitHub

## Backend Integration (Optional)

The frontend is designed to work with the Python backend but currently uses mock data for demonstration.

### Running Both Backend and Frontend

**Terminal 1 - Backend API Server:**
```bash
# Create a simple Flask/FastAPI server (example)
# See examples/ directory for server implementation
python -m src.api.server
```

**Terminal 2 - Frontend Development:**
```bash
cd frontend
npm run dev
```

### Current Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Frontend       │         │  Python Backend  │
│  (React/Vite)   │ ─────>  │  (OCR + AI)      │
│  Port: 5173     │  HTTP   │  Port: 8000      │
└─────────────────┘         └──────────────────┘
```

**Frontend Stack:**
- React 19 + TypeScript
- Vite 7 (build tool)
- React Router 7 (routing)
- Tailwind CSS 3.4 (styling)

**Backend Stack:**
- Python 3.8+
- Tesseract OCR
- Claude API (AI vision)
- OpenCV (preprocessing)

## What This System Does

### Backend Features
✅ **Enhanced OCR** - Advanced text extraction with adaptive preprocessing
✅ **OCR Visualization** - Debug tools showing text detection quality
✅ **AI Visual Analysis** - Analyzes printing techniques, typography, colors, borders
✅ **Entity Recognition** - Identifies historical countries, cities, regions
✅ **Date Estimation** - Combines OCR, AI vision, and entity signals
✅ **Explanations** - Human-readable justifications with confidence levels
✅ **Conflict Detection** - Identifies anachronistic/conflicting entities
✅ **Game Mode** - Educational gamification for learning

### Frontend Features
✅ **Web Interface** - User-friendly React application
✅ **Map Upload** - Drag-and-drop map analysis
✅ **Visual Results** - Interactive date estimates with evidence
✅ **Game Mode UI** - Engaging interface for the dating game
✅ **Responsive Design** - Works on desktop and mobile

## What This System Doesn't Do (Yet)

❌ Live backend connection (currently uses mock data in frontend)
❌ Multi-language OCR (currently English-optimized)
❌ Ancient maps (pre-1500s)
❌ Distinguish reproductions from originals
❌ Real-time processing (AI analysis takes 10-30 seconds)

See `CONTRIBUTING.md` for how to add these features.
