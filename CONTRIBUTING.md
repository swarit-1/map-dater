# Contributing to Map Dater

Thank you for your interest in contributing to Map Dater! This document provides guidelines for extending the system.

## Extension Points

### 1. Expanding the Knowledge Base

The easiest and most valuable contribution is adding historical entities.

**Add entities programmatically:**

```python
from knowledge import HistoricalKnowledgeBase
from models import HistoricalEntity, YearRange

kb = HistoricalKnowledgeBase()

entity = HistoricalEntity(
    name="Persia",
    canonical_name="Persia",
    entity_type="country",
    valid_range=YearRange(550, 1935),  # BC dates not supported yet
    alternative_names=["Persian Empire"]
)

kb.add_entity(entity)
kb.save_to_json('data/knowledge_base/my_entities.json')
```

**Entity Types:**
- `country` - Nation states, empires
- `city` - Cities with historical name changes
- `region` - Geographic regions (e.g., "Prussia", "Anatolia")
- `empire` - Multi-national empires
- `territory` - Colonies, mandates, protectorates

**Important Guidelines:**
- Use precise date ranges (start of existence to end)
- For cities, only add if the name changed
- Include all common alternative spellings
- Use canonical English names where possible

### 2. Implementing Visual Features

The `visual_features/` module is fully stubbed with clear extension points.

**Current stubs:**
- `_extract_border_style()` - Line drawing techniques
- `_extract_color_palette()` - Printing technology
- `_extract_typography()` - Font and lettering style
- `_extract_projection_hints()` - Map projection type
- `_extract_infrastructure()` - Railroads, highways, etc.

**To implement a feature:**

```python
# src/visual_features/feature_extractor.py

def _extract_border_style(self, processed_image):
    """Implement border style analysis."""

    # 1. Load your trained model
    model = load_model('models/border_classifier.pkl')

    # 2. Extract features from image
    features = extract_edge_features(processed_image.image_data)

    # 3. Make prediction
    prediction = model.predict(features)

    # 4. Map prediction to year range
    style_ranges = {
        'hand_drawn': YearRange(1500, 1900),
        'mechanical': YearRange(1900, 1980),
        'digital': YearRange(1980, 2100)
    }

    # 5. Return VisualFeature
    return [VisualFeature(
        feature_type='border_style',
        description=f'Border style: {prediction.label}',
        confidence=prediction.confidence,
        year_range=style_ranges[prediction.label],
        metadata={'model_version': '1.0'}
    )]
```

**Training Data Needed:**
- Labeled maps with ground truth dates
- Diverse geographic regions
- Various production techniques

### 3. Improving OCR Accuracy

Current limitations:
- Historical fonts may not OCR well
- Non-Latin scripts not supported
- Gothic/Fraktur fonts need special handling

**Areas for improvement:**
- Pre-trained OCR models for historical fonts
- Multi-language support (see `ocr/text_extractor.py`)
- Post-processing for common map-specific terms

### 4. Adding Signal Types

To add a new type of dating signal:

1. **Add to SignalType enum** (`src/models.py`):
```python
class SignalType(Enum):
    ENTITY = "entity"
    VISUAL = "visual"
    CARTOGRAPHIC = "cartographic"
    TEXTUAL = "textual"
    METADATA = "metadata"  # NEW
```

2. **Create extraction logic**:
```python
# In date_estimator.py
def _create_signals_from_metadata(self, metadata):
    """Extract signals from image metadata (EXIF, etc.)."""
    # Implementation
    pass
```

3. **Update explanation generator** to handle new type

### 5. Knowledge Base Formats

The knowledge base supports JSON import/export:

```json
[
  {
    "name": "Siam",
    "canonical_name": "Siam",
    "entity_type": "country",
    "valid_range": [1350, 1939],
    "alternative_names": ["Kingdom of Siam"],
    "context": {
      "renamed_to": "Thailand",
      "rename_year": 1939
    }
  }
]
```

## Code Style

- **Type hints** for all function signatures
- **Docstrings** in Google style
- **Black** formatting (line length 100)
- **Tests** for new features

## Testing

Add tests for new features:

```python
# tests/unit/test_my_feature.py
import unittest
from my_module import MyFeature

class TestMyFeature(unittest.TestCase):
    def test_basic_functionality(self):
        feature = MyFeature()
        result = feature.process()
        self.assertIsNotNone(result)
```

Run tests:
```bash
python -m pytest tests/unit/test_my_feature.py -v
```

## Areas of Need

### High Priority
1. **Non-Western entities** - Most KB entries are European
2. **City name database** - Only major cities included
3. **Colonial territories** - Need better coverage
4. **Visual feature models** - All stubs need implementation

### Medium Priority
1. **Multi-language OCR** - Currently English only
2. **Date format parsing** - Extract dates from various formats
3. **Scale/projection analysis** - Could be temporal indicators
4. **Performance optimization** - Speed up large batches

### Research Questions
1. **How to handle uncertainty better?** - Bayesian approaches?
2. **Can we detect forgeries/reproductions?** - Distinguishing signals
3. **What visual features are most diagnostic?** - Need empirical study
4. **How to calibrate confidence scores?** - Need ground truth data

## Submitting Contributions

1. Fork the repository
2. Create a feature branch
3. Add your changes with tests
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## Questions?

Open an issue on GitHub with:
- Clear description of what you want to add
- Why it's valuable
- Any implementation questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
