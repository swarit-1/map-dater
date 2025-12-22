"""
Main pipeline orchestrator for the Map Dater system.

This module coordinates all components to analyze a map and estimate its date.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import sys

sys.path.append(str(Path(__file__).parent))

from models import DateEstimate, ProcessedImage
from ingestion import ImagePreprocessor
from ocr import TextExtractor
from entities import EntityRecognizer
from knowledge import HistoricalKnowledgeBase
from visual_features import VisualFeatureExtractor
from inference import DateEstimator
from explanations import ExplanationGenerator


class MapDaterPipeline:
    """
    End-to-end pipeline for dating historical maps.

    Coordinates:
    1. Image preprocessing
    2. Text extraction (OCR)
    3. Entity recognition
    4. Visual feature extraction
    5. Date estimation
    6. Explanation generation
    """

    def __init__(
        self,
        knowledge_base: Optional[HistoricalKnowledgeBase] = None,
        enable_visual_features: bool = False,
        verbose: bool = False
    ):
        """
        Initialize the pipeline with all components.

        Args:
            knowledge_base: Custom knowledge base (or use default)
            enable_visual_features: Whether to extract visual features
            verbose: Whether to generate verbose explanations
        """
        # Initialize components
        self.preprocessor = ImagePreprocessor(
            target_dpi=300,
            apply_deskew=True,
            apply_denoise=True,
            enhance_contrast=True
        )

        self.text_extractor = TextExtractor(
            language='eng',
            confidence_threshold=0.3,
            psm=3
        )

        self.knowledge_base = knowledge_base or HistoricalKnowledgeBase()

        self.entity_recognizer = EntityRecognizer(
            knowledge_base=self.knowledge_base
        )

        self.visual_extractor = VisualFeatureExtractor(
            enable_ml_features=enable_visual_features
        )

        self.date_estimator = DateEstimator(
            entity_weight=0.7,
            visual_weight=0.2,
            textual_weight=0.1
        )

        self.explanation_generator = ExplanationGenerator(
            verbose=verbose
        )

        self.verbose = verbose
        self.enable_visual_features = enable_visual_features

    def analyze_map(
        self,
        image_path: str,
        save_processed_image: Optional[str] = None
    ) -> DateEstimate:
        """
        Analyze a map image and estimate its creation date.

        Args:
            image_path: Path to the map image
            save_processed_image: Optional path to save preprocessed image

        Returns:
            DateEstimate with full analysis and explanation

        Raises:
            FileNotFoundError: If image doesn't exist
            ValueError: If analysis fails
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"ANALYZING MAP: {image_path}")
            print(f"{'='*60}\n")

        # Step 1: Preprocess image
        if self.verbose:
            print("Step 1: Preprocessing image...")

        processed_image = self.preprocessor.process(image_path)

        if save_processed_image:
            self.preprocessor.save_processed_image(processed_image, save_processed_image)
            if self.verbose:
                print(f"  → Saved preprocessed image to {save_processed_image}")

        # Step 2: Extract text
        if self.verbose:
            print("\nStep 2: Extracting text (OCR)...")

        text_blocks = self.text_extractor.extract_text(processed_image)

        if self.verbose:
            print(f"  → Found {len(text_blocks)} text blocks")

        # Step 3: Extract historical entities
        if self.verbose:
            print("\nStep 3: Recognizing historical entities...")

        entities = self.entity_recognizer.extract_entities(text_blocks)

        if self.verbose:
            print(f"  → Identified {len(entities)} historical entities:")
            for entity in entities[:5]:  # Show first 5
                print(f"     - {entity.canonical_name} ({entity.valid_range})")
            if len(entities) > 5:
                print(f"     ... and {len(entities) - 5} more")

        if not entities:
            raise ValueError(
                "No historical entities found. "
                "Unable to estimate date without temporal constraints."
            )

        # Step 4: Extract visual features (if enabled)
        visual_features = []
        if self.enable_visual_features:
            if self.verbose:
                print("\nStep 4: Extracting visual features...")

            visual_features = self.visual_extractor.extract_all_features(processed_image)

            if self.verbose:
                print(f"  → Extracted {len(visual_features)} visual features")
        else:
            if self.verbose:
                print("\nStep 4: Skipping visual features (disabled)")

        # Step 5: Extract year references from text
        if self.verbose:
            print("\nStep 5: Searching for year references...")

        extracted_years = self.text_extractor.find_years(text_blocks)

        if self.verbose:
            if extracted_years:
                print(f"  → Found years: {extracted_years}")
            else:
                print("  → No explicit years found")

        # Step 6: Estimate date
        if self.verbose:
            print("\nStep 6: Computing date estimate...")

        estimate = self.date_estimator.estimate_date(
            entities=entities,
            visual_features=visual_features,
            extracted_years=extracted_years
        )

        # Step 7: Generate explanation
        if self.verbose:
            print("\nStep 7: Generating explanation...")

        explanation = self.explanation_generator.generate_explanation(estimate)
        estimate.explanation = explanation

        if self.verbose:
            print(f"\n{'='*60}")
            print("ANALYSIS COMPLETE")
            print(f"{'='*60}\n")

        return estimate

    def analyze_and_print(
        self,
        image_path: str,
        save_processed_image: Optional[str] = None
    ) -> DateEstimate:
        """
        Analyze a map and print the results.

        Convenience method that analyzes and displays the explanation.

        Args:
            image_path: Path to the map image
            save_processed_image: Optional path to save preprocessed image

        Returns:
            DateEstimate with full analysis
        """
        estimate = self.analyze_map(image_path, save_processed_image)

        print("\n" + "="*60)
        print(estimate.explanation)
        print("="*60 + "\n")

        return estimate

    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the pipeline configuration.

        Returns:
            Dictionary with pipeline settings and capabilities
        """
        return {
            'components': {
                'preprocessor': 'ImagePreprocessor',
                'ocr': 'TextExtractor (Tesseract)',
                'entity_recognition': 'EntityRecognizer',
                'visual_features': 'VisualFeatureExtractor (stubbed)',
                'inference': 'DateEstimator (probabilistic)',
                'explanation': 'ExplanationGenerator'
            },
            'knowledge_base': {
                'entities': len(self.knowledge_base.all_entities()),
                'types': list(set(
                    e.entity_type
                    for e in self.knowledge_base.all_entities()
                ))
            },
            'settings': {
                'visual_features_enabled': self.enable_visual_features,
                'verbose': self.verbose
            },
            'capabilities': {
                'entity_extraction': True,
                'year_extraction': True,
                'visual_analysis': False,  # Stubbed
                'explanation_generation': True
            }
        }

    def batch_analyze(
        self,
        image_paths: list[str],
        output_dir: Optional[str] = None
    ) -> list[DateEstimate]:
        """
        Analyze multiple maps in batch.

        Args:
            image_paths: List of image paths to analyze
            output_dir: Optional directory to save processed images

        Returns:
            List of DateEstimate objects
        """
        results = []

        for i, image_path in enumerate(image_paths, 1):
            print(f"\nProcessing {i}/{len(image_paths)}: {image_path}")

            try:
                save_path = None
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                    filename = Path(image_path).stem + "_processed.png"
                    save_path = str(output_dir_path / filename)

                estimate = self.analyze_map(image_path, save_path)
                results.append(estimate)

                print(f"  ✓ Estimated: {estimate.year_range}")

            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue

        return results
