"""
Text extraction from map images using OCR.

Supports multiple OCR engines and includes text normalization.
"""

import re
from typing import List, Optional
from pathlib import Path
import sys

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from models import TextBlock, BoundingBox, ProcessedImage


class TextExtractor:
    """
    Extracts and normalizes text from map images.

    Uses Tesseract OCR with specialized configuration for historical maps.
    """

    # Common OCR errors in historical maps
    OCR_CORRECTIONS = {
        'l': '1',  # Common in years
        'O': '0',
        'S': '5',
        'I': '1',
        'Z': '2',
    }

    # Historical name variations
    HISTORICAL_SYNONYMS = {
        'constantinople': 'istanbul',
        'bombay': 'mumbai',
        'madras': 'chennai',
        'calcutta': 'kolkata',
        'leningrad': 'st. petersburg',
        'petrograd': 'st. petersburg',
        'peking': 'beijing',
        'siam': 'thailand',
        'persia': 'iran',
        'ceylon': 'sri lanka',
    }

    def __init__(
        self,
        language: str = 'eng',
        confidence_threshold: float = 0.3,
        psm: int = 3  # Page segmentation mode
    ):
        """
        Initialize the text extractor.

        Args:
            language: OCR language (tesseract language code)
            confidence_threshold: Minimum confidence to accept text
            psm: Tesseract page segmentation mode
                 3 = Fully automatic page segmentation (default)
                 6 = Uniform block of text
                 11 = Sparse text
        """
        if pytesseract is None:
            raise ImportError(
                "pytesseract and Pillow are required for OCR. "
                "Install with: pip install pytesseract Pillow"
            )

        self.language = language
        self.confidence_threshold = confidence_threshold
        self.psm = psm

    def extract_text(self, processed_image: ProcessedImage) -> List[TextBlock]:
        """
        Extract all text blocks from a processed image.

        Args:
            processed_image: Preprocessed map image

        Returns:
            List of TextBlock objects with locations and confidence scores
        """
        # Convert numpy array to PIL Image
        image = Image.fromarray(processed_image.image_data)

        # Configure tesseract
        custom_config = f'--psm {self.psm} --oem 3'

        # Get detailed data including bounding boxes
        data = pytesseract.image_to_data(
            image,
            lang=self.language,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )

        text_blocks = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = float(data['conf'][i])

            # Skip empty text or low confidence
            if not text or conf < self.confidence_threshold * 100:
                continue

            bbox = BoundingBox(
                x=data['left'][i],
                y=data['top'][i],
                width=data['width'][i],
                height=data['height'][i]
            )

            normalized = self.normalize_text(text)

            text_block = TextBlock(
                text=text,
                bbox=bbox,
                confidence=conf / 100.0,  # Normalize to 0-1
                normalized_text=normalized
            )

            text_blocks.append(text_block)

        return text_blocks

    def normalize_text(self, text: str) -> str:
        """
        Normalize extracted text for entity matching.

        Handles:
        - Case normalization
        - Punctuation removal
        - Common OCR errors
        - Whitespace normalization

        Args:
            text: Raw OCR text

        Returns:
            Normalized text
        """
        # Convert to lowercase
        normalized = text.lower()

        # Remove common punctuation that OCR might misread
        normalized = re.sub(r'[,\.\:\;\!\?\"\']', '', normalized)

        # Normalize whitespace
        normalized = ' '.join(normalized.split())

        # Apply OCR corrections (conservative - only on isolated characters)
        # This helps with years like "l945" -> "1945"
        words = normalized.split()
        corrected_words = []
        for word in words:
            # Check if word looks like a year with OCR errors
            if len(word) == 4 and any(c.isdigit() for c in word):
                corrected = self._correct_year(word)
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)

        normalized = ' '.join(corrected_words)

        return normalized

    def _correct_year(self, text: str) -> str:
        """
        Attempt to correct OCR errors in year-like text.

        Args:
            text: Text that looks like a year

        Returns:
            Corrected year string
        """
        corrected = list(text)
        for i, char in enumerate(corrected):
            if char in self.OCR_CORRECTIONS:
                corrected[i] = self.OCR_CORRECTIONS[char]

        return ''.join(corrected)

    def extract_full_text(self, processed_image: ProcessedImage) -> str:
        """
        Extract all text as a single string (no bounding boxes).

        Useful for quick text analysis.

        Args:
            processed_image: Preprocessed map image

        Returns:
            Full extracted text
        """
        image = Image.fromarray(processed_image.image_data)
        text = pytesseract.image_to_string(image, lang=self.language)
        return text.strip()

    def find_years(self, text_blocks: List[TextBlock]) -> List[int]:
        """
        Extract all year-like numbers from text blocks.

        Looks for 4-digit numbers that could be years (1000-2100).

        Args:
            text_blocks: List of extracted text blocks

        Returns:
            List of potential years
        """
        years = []
        year_pattern = re.compile(r'\b(1[0-9]{3}|20[0-9]{2}|2100)\b')

        for block in text_blocks:
            matches = year_pattern.findall(block.normalized_text)
            years.extend(int(year) for year in matches)

        return sorted(set(years))
