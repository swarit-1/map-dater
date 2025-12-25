"""
Demo of AI-powered visual analysis with OCR visualization.

This example shows:
1. Improved OCR preprocessing with visualization
2. AI-powered visual feature extraction using Claude
3. Combined analysis for enhanced dating accuracy

Configuration:
- Copy .env.example to .env and set your ANTHROPIC_API_KEY
- Or set environment variable: export ANTHROPIC_API_KEY='your-key'
"""

import sys
from pathlib import Path
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded configuration from {env_path}")
    else:
        print(f"⚠ No .env file found. Copy .env.example to .env and configure.")
except ImportError:
    print("⚠ python-dotenv not installed. Install with: pip install python-dotenv")

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from ingestion import ImagePreprocessor
from ocr import TextExtractor, OCRVisualizer
from visual_features import AIVisualAnalyzer
from entities import EntityRecognizer
from knowledge import HistoricalKnowledgeBase
from inference import DateEstimator
from explanations import ExplanationGenerator


def demo_ocr_visualization(image_path: str):
    """
    Demonstrate OCR with visualization capabilities.
    """
    print("\n" + "="*80)
    print("OCR VISUALIZATION DEMO")
    print("="*80)

    # Preprocess with improved settings
    print("\n1. Preprocessing image with enhanced settings...")
    preprocessor = ImagePreprocessor(
        apply_deskew=True,
        apply_denoise=True,
        enhance_contrast=True,
        apply_binarization=False,  # Try both True/False
        upscale_factor=1.5  # Upscale for better OCR
    )

    processed = preprocessor.process(image_path)
    print(f"   Applied: {', '.join(processed.preprocessing_applied)}")

    # Extract text
    print("\n2. Extracting text with OCR...")
    extractor = TextExtractor(confidence_threshold=0.3, psm=3)
    text_blocks = extractor.extract_text(processed)
    print(f"   Found {len(text_blocks)} text blocks")

    # Visualize
    print("\n3. Creating visualizations...")
    visualizer = OCRVisualizer(show_confidence=True)

    output_dir = Path(__file__).parent.parent / 'data' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create all visualizations
    bbox_img = visualizer.visualize_text_blocks(
        processed,
        text_blocks,
        str(output_dir / 'ocr_bboxes.png')
    )
    print(f"   ✓ Saved bounding boxes: {output_dir / 'ocr_bboxes.png'}")

    word_map = visualizer.create_word_map(
        processed,
        text_blocks,
        str(output_dir / 'word_map.png')
    )
    print(f"   ✓ Saved word map: {output_dir / 'word_map.png'}")

    heatmap = visualizer.create_heatmap(
        processed,
        text_blocks,
        str(output_dir / 'confidence_heatmap.png')
    )
    print(f"   ✓ Saved confidence heatmap: {output_dir / 'confidence_heatmap.png'}")

    summary = visualizer.create_summary_visualization(
        processed,
        text_blocks,
        str(output_dir / 'ocr_summary.png')
    )
    print(f"   ✓ Saved summary visualization: {output_dir / 'ocr_summary.png'}")

    return processed, text_blocks


def demo_ai_visual_analysis(processed_image, api_key: str = None):
    """
    Demonstrate AI-powered visual analysis.
    """
    print("\n" + "="*80)
    print("AI VISUAL ANALYSIS DEMO")
    print("="*80)

    # Check for API key (from .env or parameter)
    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("\n⚠️  ANTHROPIC_API_KEY not set. Skipping AI analysis.")
            print("   Setup instructions:")
            print("   1. Copy .env.example to .env")
            print("   2. Add your API key: ANTHROPIC_API_KEY=your-key-here")
            print("   3. Get API key from: https://console.anthropic.com")
            return []

    print("\n1. Initializing Claude vision analyzer...")
    try:
        analyzer = AIVisualAnalyzer(api_key=api_key)
    except ValueError as e:
        print(f"\n⚠️  {e}")
        return []

    print("\n2. Analyzing visual features (this may take 10-30 seconds)...")
    features = analyzer.analyze_map_features(processed_image)

    print(f"\n3. Extracted {len(features)} AI-identified features:")
    for i, feature in enumerate(features, 1):
        print(f"\n   Feature {i}: {feature.feature_type}")
        print(f"   Description: {feature.description}")
        if feature.year_range:
            print(f"   Date range: {feature.year_range.start}-{feature.year_range.end}")
        print(f"   Confidence: {feature.confidence:.2f}")
        if 'reasoning' in feature.metadata:
            print(f"   Reasoning: {feature.metadata['reasoning']}")

    return features


def demo_combined_analysis(image_path: str, api_key: str = None):
    """
    Demonstrate combined OCR + AI analysis for enhanced dating.
    """
    print("\n" + "="*80)
    print("COMBINED ANALYSIS DEMO")
    print("="*80)

    # Preprocessing
    print("\n1. Preprocessing...")
    preprocessor = ImagePreprocessor(
        apply_deskew=True,
        apply_denoise=True,
        enhance_contrast=True,
        upscale_factor=1.5
    )
    processed = preprocessor.process(image_path)

    # OCR
    print("\n2. Extracting text...")
    extractor = TextExtractor(confidence_threshold=0.3)
    text_blocks = extractor.extract_text(processed)
    print(f"   Found {len(text_blocks)} text blocks")

    # Entity recognition
    print("\n3. Recognizing historical entities...")
    kb = HistoricalKnowledgeBase()
    recognizer = EntityRecognizer(kb)
    entities = recognizer.extract_entities(text_blocks)
    print(f"   Identified {len(entities)} entities")

    # AI visual analysis
    visual_features = []
    if api_key or os.getenv('ANTHROPIC_API_KEY'):
        print("\n4. AI visual analysis...")
        try:
            analyzer = AIVisualAnalyzer(api_key=api_key)
            visual_features = analyzer.analyze_map_features(processed)
            print(f"   Extracted {len(visual_features)} visual features")
        except ValueError as e:
            print(f"\n4. Skipping AI analysis: {e}")
    else:
        print("\n4. Skipping AI analysis (no API key)")
        print("   Configure .env file with ANTHROPIC_API_KEY to enable")

    # Find years
    years = extractor.find_years(text_blocks)

    # Combine for final estimate
    print("\n5. Computing final date estimate...")
    estimator = DateEstimator(
        entity_weight=0.5,
        visual_weight=0.3,
        textual_weight=0.2
    )

    estimate = estimator.estimate_date(
        entities=entities,
        visual_features=visual_features,
        extracted_years=years
    )

    # Generate explanation
    explainer = ExplanationGenerator(verbose=True)
    explanation = explainer.generate_explanation(estimate)

    print("\n" + "="*80)
    print("FINAL ANALYSIS RESULT")
    print("="*80)
    print(explanation)


def main():
    """Main demo entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Demo AI-powered map analysis with OCR visualization'
    )
    parser.add_argument(
        'image_path',
        nargs='?',
        help='Path to map image (or use sample map)'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (overrides .env and ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--mode',
        choices=['ocr', 'ai', 'combined'],
        default='combined',
        help='Demo mode: ocr, ai, or combined (default: combined)'
    )

    args = parser.parse_args()

    # Find image
    if args.image_path:
        image_path = args.image_path
    else:
        # Try to use a sample map
        sample_dir = Path(__file__).parent.parent / 'data' / 'sample_maps'
        if sample_dir.exists():
            samples = list(sample_dir.glob('*.png')) + list(sample_dir.glob('*.jpg'))
            if samples:
                image_path = str(samples[0])
                print(f"Using sample map: {image_path}")
            else:
                print("Error: No sample maps found. Please provide an image path.")
                return
        else:
            print("Error: No image path provided and no samples found.")
            print("Usage: python ai_analysis_demo.py <image_path>")
            return

    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        return

    # Run requested demo
    if args.mode == 'ocr':
        demo_ocr_visualization(image_path)

    elif args.mode == 'ai':
        preprocessor = ImagePreprocessor()
        processed = preprocessor.process(image_path)
        demo_ai_visual_analysis(processed, args.api_key)

    else:  # combined
        demo_combined_analysis(image_path, args.api_key)

    print("\n" + "="*80)
    print("Demo complete! Check data/output/ for visualization results.")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
