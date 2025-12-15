"""CLI interface for viewport library."""

import sys
import json
import argparse
import logging

from portrait_helper.image.viewport import Viewport, MIN_ZOOM, MAX_ZOOM

logger = logging.getLogger(__name__)


def main():
    """CLI entry point for viewport."""
    parser = argparse.ArgumentParser(description="Calculate viewport parameters")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    calc_parser = subparsers.add_parser("calculate-viewport", help="Calculate viewport parameters")
    calc_parser.add_argument(
        "--image-width",
        type=int,
        required=True,
        help="Image width in pixels",
    )
    calc_parser.add_argument(
        "--image-height",
        type=int,
        required=True,
        help="Image height in pixels",
    )
    calc_parser.add_argument(
        "--window-width",
        type=int,
        required=True,
        help="Window width in pixels",
    )
    calc_parser.add_argument(
        "--window-height",
        type=int,
        required=True,
        help="Window height in pixels",
    )
    calc_parser.add_argument(
        "--zoom",
        type=float,
        default=1.0,
        help=f"Zoom level (default: 1.0, range: {MIN_ZOOM}-{MAX_ZOOM})",
    )
    calc_parser.add_argument(
        "--pan-x",
        type=float,
        default=0.0,
        help="Horizontal pan offset (default: 0.0)",
    )
    calc_parser.add_argument(
        "--pan-y",
        type=float,
        default=0.0,
        help="Vertical pan offset (default: 0.0)",
    )
    calc_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()
    
    if args.command != "calculate-viewport":
        parser.print_help()
        sys.exit(1)

    try:
        # Create viewport
        viewport = Viewport(
            image_width=args.image_width,
            image_height=args.image_height,
            window_width=args.window_width,
            window_height=args.window_height,
        )

        # Set zoom and pan if specified
        if args.zoom != 1.0:
            viewport.set_zoom(args.zoom)
        if args.pan_x != 0.0 or args.pan_y != 0.0:
            viewport.pan(args.pan_x, args.pan_y)

        # Output results
        if args.output_format == "json":
            output_json(viewport)
            sys.exit(0)
        else:
            output_text(viewport)
            sys.exit(0)

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


def output_text(viewport: Viewport) -> None:
    """Output viewport parameters in text format.

    Args:
        viewport: Viewport object
    """
    display_width, display_height = viewport.get_display_size()
    visible_region = viewport.get_visible_region()

    print("SUCCESS")
    print(f"Zoom Level: {viewport.zoom_level}")
    print(f"Pan Offset: ({viewport.pan_offset_x:.2f}, {viewport.pan_offset_y:.2f})")
    print(f"Display Size: {display_width:.2f}x{display_height:.2f}")
    print(f"Window Size: {viewport.window_width}x{viewport.window_height}")
    print(f"Visible Region: x={visible_region['x']:.2f}, y={visible_region['y']:.2f}, "
          f"width={visible_region['width']:.2f}, height={visible_region['height']:.2f}")


def output_json(viewport: Viewport) -> None:
    """Output viewport parameters in JSON format.

    Args:
        viewport: Viewport object
    """
    display_width, display_height = viewport.get_display_size()
    visible_region = viewport.get_visible_region()

    output = {
        "status": "success",
        "zoom_level": viewport.zoom_level,
        "pan_offset": {
            "x": viewport.pan_offset_x,
            "y": viewport.pan_offset_y,
        },
        "display_width": display_width,
        "display_height": display_height,
        "window_width": viewport.window_width,
        "window_height": viewport.window_height,
        "visible_region": visible_region,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

