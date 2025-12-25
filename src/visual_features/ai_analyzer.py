"""
AI-powered visual analysis using Claude's vision capabilities.

This module uses the Anthropic Claude API to analyze map images
and extract visual features that indicate the map's creation period.
"""

import base64
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys
import json
import re
import os

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from dotenv import load_dotenv
    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed

import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from models import ProcessedImage, VisualFeature, YearRange


class AIVisualAnalyzer:
    """
    Uses Claude's vision API to analyze historical maps.

    Capable of detecting:
    - Printing techniques (hand-drawn, lithography, offset, digital)
    - Cartographic styles and conventions
    - Typography and font characteristics
    - Color palettes and quality
    - Infrastructure presence (railroads, highways, etc.)
    - Border and decoration styles
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize the AI visual analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY from .env)
            model: Claude model to use (defaults to CLAUDE_MODEL from .env or claude-3-5-sonnet-20241022)
            max_tokens: Maximum tokens for response (defaults to CLAUDE_MAX_TOKENS from .env or 4096)
        """
        if anthropic is None:
            raise ImportError(
                "anthropic package required for AI analysis. "
                "Install with: pip install anthropic"
            )

        # Load configuration from .env if not provided
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. "
                    "Set it in .env file or pass as parameter. "
                    "See .env.example for setup instructions."
                )

        if model is None:
            model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')

        if max_tokens is None:
            max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '4096'))

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def _encode_image(self, processed_image: ProcessedImage) -> str:
        """
        Encode image as base64 for API.

        Args:
            processed_image: Processed map image

        Returns:
            Base64 encoded image string
        """
        import cv2

        # Convert to PNG bytes
        _, buffer = cv2.imencode('.png', processed_image.image_data)
        image_bytes = buffer.tobytes()

        # Encode to base64
        return base64.b64encode(image_bytes).decode('utf-8')

    def analyze_map_features(
        self,
        processed_image: ProcessedImage,
        focus_areas: Optional[List[str]] = None
    ) -> List[VisualFeature]:
        """
        Analyze visual features using AI vision.

        Args:
            processed_image: Preprocessed map image
            focus_areas: Optional list of specific features to analyze
                        (e.g., ['typography', 'borders', 'colors'])

        Returns:
            List of extracted visual features with date constraints
        """
        # Encode image
        image_b64 = self._encode_image(processed_image)

        # Build prompt
        prompt = self._build_analysis_prompt(focus_areas)

        # Call Claude API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Parse response
            response_text = message.content[0].text
            features = self._parse_response(response_text)

            return features

        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            return []

    def _build_analysis_prompt(self, focus_areas: Optional[List[str]] = None) -> str:
        """
        Build the analysis prompt for Claude.

        Args:
            focus_areas: Optional specific areas to focus on

        Returns:
            Formatted prompt string
        """
        base_prompt = """You are a historical cartography expert analyzing a map image.
Your task is to identify visual features that help date when this map was created.

Analyze the following aspects and provide date constraints for each:

1. **Printing Technique**:
   - Hand-drawn (pre-1800s typically)
   - Lithography (1800s-1950s)
   - Offset printing (1900s-1980s)
   - Digital printing (1980s+)

2. **Typography & Fonts**:
   - Hand-lettering style
   - Mechanical typesetting
   - Digital fonts
   - Font characteristics that indicate era

3. **Color Palette**:
   - Black and white vs color
   - Number of colors (process limitations by era)
   - Color registration quality
   - Digital vs analog color characteristics

4. **Border & Decoration Style**:
   - Ornate decorative borders (common pre-1900)
   - Simple mechanical borders (1900-1950)
   - Minimal modern borders (1950+)

5. **Cartographic Style**:
   - Projection type and accuracy
   - Level of geographic detail
   - Symbology conventions

6. **Infrastructure & Features**:
   - Railroads (expansion patterns)
   - Highway systems
   - Airports
   - Other temporal markers

For each feature you identify, provide:
- Feature type (typography, border_style, color_palette, printing_technique, infrastructure, etc.)
- Description of what you observe
- Estimated year range (start_year to end_year)
- Confidence level (0.0 to 1.0)
- Reasoning for your assessment

Format your response as JSON:
```json
{
  "features": [
    {
      "feature_type": "typography",
      "description": "Digital sans-serif font, likely Arial or Helvetica",
      "year_range": {"start": 1985, "end": 2025},
      "confidence": 0.85,
      "reasoning": "Digital fonts became common after desktop publishing emerged in mid-1980s"
    },
    ...
  ]
}
```

Be specific and technical in your observations. Focus on evidence-based dating."""

        if focus_areas:
            base_prompt += f"\n\nFocus particularly on these areas: {', '.join(focus_areas)}"

        return base_prompt

    def _parse_response(self, response_text: str) -> List[VisualFeature]:
        """
        Parse Claude's JSON response into VisualFeature objects.

        Args:
            response_text: Raw response from Claude

        Returns:
            List of VisualFeature objects
        """
        features = []

        try:
            # Extract JSON from response (might be wrapped in markdown)
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to parse entire response as JSON
                json_str = response_text

            data = json.loads(json_str)

            for feature_data in data.get('features', []):
                year_range = None
                if 'year_range' in feature_data:
                    yr = feature_data['year_range']
                    year_range = YearRange(
                        start=yr.get('start'),
                        end=yr.get('end')
                    )

                feature = VisualFeature(
                    feature_type=feature_data.get('feature_type', 'unknown'),
                    description=feature_data.get('description', ''),
                    confidence=feature_data.get('confidence', 0.5),
                    year_range=year_range,
                    metadata={
                        'reasoning': feature_data.get('reasoning', ''),
                        'source': 'claude_vision_api'
                    }
                )

                features.append(feature)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to parse AI response: {e}")
            print(f"Response was: {response_text[:500]}")

        return features

    def analyze_specific_region(
        self,
        processed_image: ProcessedImage,
        x: int, y: int, width: int, height: int,
        question: str
    ) -> str:
        """
        Analyze a specific region of the map with a custom question.

        Useful for targeted analysis of particular features.

        Args:
            processed_image: Preprocessed map image
            x, y, width, height: Region coordinates
            question: Specific question to ask about this region

        Returns:
            AI's analysis response
        """
        # Crop to region
        import cv2
        region = processed_image.image_data[y:y+height, x:x+width]

        # Create temporary ProcessedImage for region
        from models import ProcessedImage as PI
        region_image = PI(
            image_data=region,
            original_path=processed_image.original_path,
            width=width,
            height=height,
            preprocessing_applied=processed_image.preprocessing_applied
        )

        # Encode
        image_b64 = self._encode_image(region_image)

        # Query
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": question
                            }
                        ],
                    }
                ],
            )

            return message.content[0].text

        except Exception as e:
            return f"Error: {e}"

    def get_quick_dating_estimate(
        self,
        processed_image: ProcessedImage
    ) -> Dict[str, Any]:
        """
        Get a quick date estimate from AI without detailed feature extraction.

        Faster than full analysis, suitable for initial screening.

        Args:
            processed_image: Preprocessed map image

        Returns:
            Dictionary with estimated date range and confidence
        """
        image_b64 = self._encode_image(processed_image)

        prompt = """Look at this historical map. Based on visual characteristics like:
- Printing technique
- Typography style
- Color usage
- Overall aesthetic

Provide a quick estimate of when this map was likely created.

Respond in JSON format:
```json
{
  "estimated_start_year": 1950,
  "estimated_end_year": 1980,
  "confidence": 0.7,
  "key_indicators": ["offset printing", "mid-century typography", "limited color palette"],
  "reasoning": "Brief explanation"
}
```"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            response_text = message.content[0].text

            # Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(response_text)

        except Exception as e:
            return {
                "error": str(e),
                "estimated_start_year": None,
                "estimated_end_year": None,
                "confidence": 0.0
            }
