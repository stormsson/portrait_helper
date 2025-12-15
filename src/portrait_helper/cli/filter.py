"""CLI interface for image filter library."""

import sys
import json
import argparse
import logging
from pathlib import Path

from portrait_helper.image.loader import load_from_file, load_from_url, ImageLoadError
from portrait_helper.image.filter import FilterState

logger = logging.getLogger(__name__)


def main():
    """CLI entry point for image filter."""
    parser = argparse.ArgumentParser(description="Apply filters to images")
    parser.add_argument(
        "input_image",
        help="Input image file path or URL",
    )
    parser.add_argument(
        "--filter-type",
        choices=["grayscale"],
        default="grayscale",
        help="Filter type to apply (default: grayscale)",
    )
    parser.add_argument(
        "--output",
        help="Output image file path (if not specified, outputs metadata only)",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for metadata (default: text)",
    )

    args = parser.parse_args()

    try:
        # Load input image
        source = args.input_image
        is_url = source.startswith("http://") or source.startswith("https://")

        if is_url:
            image = load_from_url(source)
        else:
            image = load_from_file(source)

        # Create filter state
        filter_state = FilterState(original_pixel_data=image.get_pixel_data())

        # Apply filter
        if args.filter_type == "grayscale":
            filter_state.toggle_grayscale()
            filtered_image = filter_state.get_current_image()
        else:
            print(f"ERROR: Unknown filter type: {args.filter_type}", file=sys.stderr)
            sys.exit(1)

        # Save output if specified
        if args.output:
            output_path = Path(args.output)
            filtered_image.save(str(output_path))
            logger.info(f"Filtered image saved to {output_path}")

        # Output results
        if args.output_format == "json":
            output_json(image, filter_state, args.filter_type, args.output)
            sys.exit(0)
        else:
            output_text(image, filter_state, args.filter_type, args.output)
            sys.exit(0)

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ImageLoadError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        logger.error(f"Error applying filter: {e}", exc_info=True)
        sys.exit(4)


def output_text(image: "Image", filter_state: FilterState, filter_type: str, output_path: str = None) -> None:
    """Output filter metadata in text format.

    Args:
        image: Original image object
        filter_state: FilterState object with applied filter
        filter_type: Type of filter applied
        output_path: Path to output file if saved
    """
    print("SUCCESS")
    print(f"Filter: {filter_type}")
    print(f"Original Width: {image.width}")
    print(f"Original Height: {image.height}")
    print(f"Original Format: {image.format}")
    
    filtered_image = filter_state.get_current_image()
    if filtered_image:
        print(f"Filtered Width: {filtered_image.width}")
        print(f"Filtered Height: {filtered_image.height}")
        print(f"Filtered Mode: {filtered_image.mode}")
    
    if output_path:
        print(f"Output: {output_path}")


def output_json(image: "Image", filter_state: FilterState, filter_type: str, output_path: str = None) -> None:
    """Output filter metadata in JSON format.

    Args:
        image: Original image object
        filter_state: FilterState object with applied filter
        filter_type: Type of filter applied
        output_path: Path to output file if saved
    """
    filtered_image = filter_state.get_current_image()
    output = {
        "status": "success",
        "filter_type": filter_type,
        "original": {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "aspect_ratio": image.aspect_ratio,
        },
        "filtered": {
            "width": filtered_image.width if filtered_image else None,
            "height": filtered_image.height if filtered_image else None,
            "mode": filtered_image.mode if filtered_image else None,
        },
    }
    if output_path:
        output["output_path"] = output_path
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

