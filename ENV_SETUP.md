# Environment Configuration Guide

This guide explains how to set up your `.env` file for Map Dater.

## Quick Setup

### Option 1: Interactive Setup (Recommended)

```bash
python setup_env.py
```

This interactive script will guide you through configuring all settings.

### Option 2: Manual Setup

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env
# or
code .env
```

## Required Settings

### ANTHROPIC_API_KEY

**Purpose:** Enables AI-powered visual analysis using Claude's vision capabilities.

**How to get:**
1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Navigate to API Keys section
3. Create a new API key
4. Copy and paste into `.env`

```ini
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Without this key:**
- ✅ OCR and entity recognition still work
- ❌ AI visual analysis features disabled
- ❌ Cannot analyze printing techniques, typography, etc.

## Optional Settings

### Preprocessing Options

#### PREPROCESSING_UPSCALE
**Default:** `1.0` (no scaling)
**Recommended:** `1.5` to `2.0` for better OCR

Upscales images before OCR processing. Higher values improve text detection on low-resolution maps but increase processing time.

```ini
PREPROCESSING_UPSCALE=1.5
```

**When to use:**
- ✅ Low-resolution scans
- ✅ Small text on maps
- ❌ Already high-quality images (wastes time)

#### PREPROCESSING_BINARIZATION
**Default:** `false`
**Try:** `true` if OCR is missing text

Converts image to high-contrast black and white.

```ini
PREPROCESSING_BINARIZATION=true
```

**When to use:**
- ✅ Faded or low-contrast maps
- ✅ Maps with background noise
- ❌ Color maps where color analysis matters

#### Other Preprocessing Options

```ini
PREPROCESSING_DESKEW=true      # Fix rotation (default: true)
PREPROCESSING_DENOISE=true     # Remove noise (default: true)
PREPROCESSING_CONTRAST=true    # Enhance contrast (default: true)
```

### OCR Options

#### OCR_CONFIDENCE_THRESHOLD
**Default:** `0.3`
**Range:** `0.0` to `1.0`

Minimum confidence score to accept OCR text.

```ini
OCR_CONFIDENCE_THRESHOLD=0.3
```

**Lower values (0.1-0.2):**
- ✅ More text detected
- ❌ More false positives

**Higher values (0.5-0.7):**
- ✅ More accurate text
- ❌ May miss some text

#### OCR_LANGUAGE
**Default:** `eng`
**Examples:** `eng+fra`, `deu`, `spa`

Tesseract language code(s). Use `+` for multiple languages.

```ini
OCR_LANGUAGE=eng+fra+deu
```

**Available languages:** See [Tesseract documentation](https://github.com/tesseract-ocr/tessdata)

#### TESSERACT_CMD
**Default:** Auto-detected
**Use when:** Tesseract not in PATH

Path to Tesseract executable.

```ini
# Windows
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Linux/Mac (usually not needed)
TESSERACT_CMD=/usr/local/bin/tesseract
```

### Claude API Options

#### CLAUDE_MODEL
**Default:** `claude-3-5-sonnet-20241022`
**Alternatives:** `claude-3-opus-20240229`, `claude-3-haiku-20240307`

Which Claude model to use for visual analysis.

```ini
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**Model comparison:**
- **Sonnet (default):** Best balance of quality and cost
- **Opus:** Highest quality, most expensive
- **Haiku:** Fastest and cheapest, lower quality

#### CLAUDE_MAX_TOKENS
**Default:** `4096`
**Range:** `1024` to `8192`

Maximum response length from Claude.

```ini
CLAUDE_MAX_TOKENS=4096
```

### Output Options

#### OUTPUT_DIR
**Default:** `data/output`

Where to save visualization images.

```ini
OUTPUT_DIR=results/visualizations
```

#### VERBOSE
**Default:** `false`

Enable detailed logging during processing.

```ini
VERBOSE=true
```

#### SAVE_PREPROCESSED
**Default:** `false`

Automatically save preprocessed images.

```ini
SAVE_PREPROCESSED=true
```

## Example Configurations

### For Historical Researchers

High quality analysis, don't mind slower processing:

```ini
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
PREPROCESSING_UPSCALE=2.0
OCR_CONFIDENCE_THRESHOLD=0.4
VERBOSE=true
SAVE_PREPROCESSED=true
```

### For Quick Testing

Faster processing, good enough results:

```ini
ANTHROPIC_API_KEY=your_key_here
PREPROCESSING_UPSCALE=1.0
OCR_CONFIDENCE_THRESHOLD=0.3
VERBOSE=false
```

### For Difficult/Faded Maps

Maximum preprocessing to extract text:

```ini
ANTHROPIC_API_KEY=your_key_here
PREPROCESSING_UPSCALE=2.0
PREPROCESSING_BINARIZATION=true
PREPROCESSING_CONTRAST=true
OCR_CONFIDENCE_THRESHOLD=0.2
```

## Security Best Practices

### ✅ DO:
- Keep `.env` file local (it's in `.gitignore`)
- Use different API keys for development and production
- Rotate API keys periodically
- Set API usage limits in Anthropic console

### ❌ DON'T:
- Commit `.env` to version control
- Share your `.env` file with others
- Hard-code API keys in scripts
- Use the same key across multiple projects

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

**Check:**
1. `.env` file exists in project root
2. Key is spelled correctly: `ANTHROPIC_API_KEY`
3. No quotes around the key value
4. No spaces around the `=` sign

**Correct:**
```ini
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Incorrect:**
```ini
ANTHROPIC_API_KEY = "sk-ant-api03-..."  # No quotes or spaces!
```

### "python-dotenv not installed"

```bash
pip install python-dotenv
```

### Changes not taking effect

**Solution:** Restart the Python script after modifying `.env`

Environment variables are loaded when the script starts, not continuously.

## Getting Help

- Full example: See `.env.example`
- Interactive setup: Run `python setup_env.py`
- Documentation: See `README.md` and `QUICKSTART.md`
