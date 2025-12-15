"""CLI interface for grid overlay library."""

import sys
import json
import argparse
import logging

from portrait_helper.grid.config import GridConfiguration, MIN_SUBDIVISIONS, MAX_SUBDIVISIONS

logger = logging.getLogger(__name__)


def main():
    """CLI entry point for grid overlay."""
    parser = argparse.ArgumentParser(description="Calculate grid overlay parameters")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    calc_parser = subparsers.add_parser("calculate-grid", help="Calculate grid parameters")
    calc_parser.add_argument(
        "--subdivision-count",
        type=int,
        default=3,
        help=f"Number of grid subdivisions (default: 3, range: {MIN_SUBDIVISIONS}-{MAX_SUBDIVISIONS})",
    )
    calc_parser.add_argument(
        "--viewport-width",
        type=float,
        required=True,
        help="Viewport width in pixels",
    )
    calc_parser.add_argument(
        "--viewport-height",
        type=float,
        required=True,
        help="Viewport height in pixels",
    )
    calc_parser.add_argument(
        "--color",
        type=str,
        default="255,255,255",
        help="Grid line color as RGB (default: 255,255,255)",
    )
    calc_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()
    
    if args.command != "calculate-grid":
        parser.print_help()
        sys.exit(1)

    try:
        # Parse color
        color_parts = [int(x.strip()) for x in args.color.split(",")]
        if len(color_parts) == 3:
            color = tuple(color_parts)
        elif len(color_parts) == 4:
            color = tuple(color_parts)
        else:
            raise ValueError("Color must be RGB (3 values) or RGBA (4 values)")

        # Create grid configuration
        config = GridConfiguration(
            visible=True,
            subdivision_count=args.subdivision_count,
            color=color,
        )

        # Calculate cell size
        config.calculate_cell_size(
            viewport_width=args.viewport_width,
            viewport_height=args.viewport_height,
        )

        # Output results
        if args.output_format == "json":
            output_json(config, args.viewport_width, args.viewport_height)
            sys.exit(0)
        else:
            output_text(config, args.viewport_width, args.viewport_height)
            sys.exit(0)

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


def output_text(config: GridConfiguration, viewport_width: float, viewport_height: float) -> None:
    """Output grid parameters in text format.

    Args:
        config: GridConfiguration object
        viewport_width: Viewport width
        viewport_height: Viewport height
    """
    print("SUCCESS")
    print(f"Subdivision Count: {config.subdivision_count}")
    print(f"Cell Size: {config.cell_size:.2f} pixels")
    print(f"Viewport: {viewport_width:.0f}x{viewport_height:.0f}")
    print(f"Color: {config.color}")
    print(f"Line Width: {config.line_width}")
    print(f"Opacity: {config.opacity}")


def output_json(config: GridConfiguration, viewport_width: float, viewport_height: float) -> None:
    """Output grid parameters in JSON format.

    Args:
        config: GridConfiguration object
        viewport_width: Viewport width
        viewport_height: Viewport height
    """
    output = {
        "status": "success",
        "subdivision_count": config.subdivision_count,
        "cell_size": config.cell_size,
        "viewport": {
            "width": viewport_width,
            "height": viewport_height,
        },
        "color": list(config.color),
        "line_width": config.line_width,
        "opacity": config.opacity,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

