"""
Main entry point for the Map Dater system.

Usage:
    python main.py path/to/map.jpg
    python main.py path/to/map.jpg --save-processed output.png
    python main.py --demo
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from pipeline import MapDaterPipeline


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Map Dater - Estimate when a historical map was created',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py map.jpg
  python main.py map.jpg --verbose
  python main.py map.jpg --save-processed cleaned.png
  python main.py --demo

For more information, see README.md
        """
    )

    parser.add_argument(
        'image_path',
        nargs='?',
        help='Path to the map image to analyze'
    )

    parser.add_argument(
        '--save-processed',
        metavar='PATH',
        help='Save the preprocessed image to this path'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed processing steps'
    )

    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run the demo instead of analyzing an image'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Run demo if requested
    if args.demo:
        print("Running demo...\n")
        from examples.demo import main as demo_main
        demo_main()
        return

    # Require image path if not demo
    if not args.image_path:
        parser.print_help()
        print("\nError: Either provide an image path or use --demo")
        sys.exit(1)

    # Check if image exists
    if not Path(args.image_path).exists():
        print(f"Error: Image not found: {args.image_path}")
        sys.exit(1)

    # Initialize pipeline
    print("Initializing Map Dater pipeline...")
    pipeline = MapDaterPipeline(verbose=args.verbose)

    # Analyze the map
    try:
        estimate = pipeline.analyze_map(
            args.image_path,
            save_processed_image=args.save_processed
        )

        # Output results
        if args.json:
            import json
            from explanations import ExplanationGenerator

            explainer = ExplanationGenerator()
            result = explainer.generate_json_explanation(estimate)
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "="*60)
            print(estimate.explanation)
            print("="*60 + "\n")

    except Exception as e:
        print(f"\nError analyzing map: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
