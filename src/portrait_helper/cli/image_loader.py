"""CLI interface for image loading library."""

import sys
import json
import argparse
import logging
from pathlib import Path

from portrait_helper.image.loader import load_from_file, load_from_url, ImageLoadError

logger = logging.getLogger(__name__)


def main():
    """CLI entry point for image loader."""
    parser = argparse.ArgumentParser(description="Load images from file or URL")
    parser.add_argument(
        "source",
        help="File path or URL to image",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    try:
        # Determine if source is URL or file path
        source = args.source
        is_url = source.startswith("http://") or source.startswith("https://")

        if is_url:
            image = load_from_url(source)
        else:
            image = load_from_file(source)

        # Output results
        if args.output_format == "json":
            output_json(image)
            sys.exit(0)
        else:
            output_text(image)
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
        print(f"ERROR: Network error: {e}", file=sys.stderr)
        sys.exit(4)


def output_text(image: "Image") -> None:
    """Output image metadata in text format.

    Args:
        image: Image object to output
    """
    print("SUCCESS")
    print(f"Width: {image.width}")
    print(f"Height: {image.height}")
    print(f"Format: {image.format}")
    print(f"Aspect Ratio: {image.aspect_ratio:.4f}")
    if image.source_path:
        print(f"Path: {image.source_path}")
    elif image.source_url:
        print(f"URL: {image.source_url}")


def output_json(image: "Image") -> None:
    """Output image metadata in JSON format.

    Args:
        image: Image object to output
    """
    metadata = image.get_metadata()
    output = {
        "status": "success",
        "width": metadata["width"],
        "height": metadata["height"],
        "format": metadata["format"],
        "aspect_ratio": metadata["aspect_ratio"],
        "source": metadata["source"],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

