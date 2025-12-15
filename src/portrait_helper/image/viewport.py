"""Viewport calculations library for Portrait Helper."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Constants
MIN_ZOOM = 0.1
MAX_ZOOM = 10.0
DEFAULT_ZOOM = 1.0


class Viewport:
    """Represents the visible area and transformation state of the displayed image."""

    def __init__(
        self,
        image_width: int,
        image_height: int,
        window_width: int,
        window_height: int,
    ):
        """Initialize Viewport.

        Args:
            image_width: Original image width in pixels
            image_height: Original image height in pixels
            window_width: Current window width in pixels
            window_height: Current window height in pixels
        """
        if image_width <= 0 or image_height <= 0:
            raise ValueError("Image dimensions must be positive")
        if window_width <= 0 or window_height <= 0:
            raise ValueError("Window dimensions must be positive")

        self._image_width = image_width
        self._image_height = image_height
        self._image_aspect_ratio = image_width / image_height if image_height > 0 else 1.0

        self.zoom_level = DEFAULT_ZOOM
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.window_width = window_width
        self.window_height = window_height

        self._recalculate_display()

        logger.debug(
            f"Viewport created: image={image_width}x{image_height}, "
            f"window={window_width}x{window_height}, zoom={self.zoom_level}"
        )

    def _recalculate_display(self) -> None:
        """Recalculate display dimensions and visible region."""
        # Calculate display size maintaining aspect ratio
        window_aspect = self.window_width / self.window_height if self.window_height > 0 else 1.0

        if window_aspect > self._image_aspect_ratio:
            # Window is wider, fit to height
            self.display_height = self.window_height * self.zoom_level
            self.display_width = self.display_height * self._image_aspect_ratio
        else:
            # Window is taller, fit to width
            self.display_width = self.window_width * self.zoom_level
            self.display_height = self.display_width / self._image_aspect_ratio

        # Calculate visible region
        self.visible_region_x = -self.pan_offset_x
        self.visible_region_y = -self.pan_offset_y
        self.visible_region_width = self.display_width
        self.visible_region_height = self.display_height

    def set_zoom(
        self,
        level: float,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
    ) -> None:
        """Set zoom level, optionally centered on specific point.

        Args:
            level: Zoom level (0.1 to 10.0)
            center_x: X coordinate to center zoom on (optional)
            center_y: Y coordinate to center zoom on (optional)

        Raises:
            ValueError: If zoom level is out of bounds
        """
        if level < MIN_ZOOM or level > MAX_ZOOM:
            raise ValueError(f"Zoom level must be between {MIN_ZOOM} and {MAX_ZOOM}")

        old_zoom = self.zoom_level
        self.zoom_level = level

        # Adjust pan to maintain center point if specified
        if center_x is not None and center_y is not None:
            zoom_factor = level / old_zoom if old_zoom > 0 else 1.0
            self.pan_offset_x = center_x - (center_x - self.pan_offset_x) * zoom_factor
            self.pan_offset_y = center_y - (center_y - self.pan_offset_y) * zoom_factor

        self._recalculate_display()
        self.constrain_pan()

        logger.debug(f"Zoom set to {level}, center=({center_x}, {center_y})")

    def zoom_in(
        self,
        factor: float = 1.2,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
    ) -> None:
        """Increase zoom level.

        Args:
            factor: Zoom multiplier (default: 1.2)
            center_x: X coordinate to center zoom on (optional)
            center_y: Y coordinate to center zoom on (optional)
        """
        new_zoom = min(self.zoom_level * factor, MAX_ZOOM)
        self.set_zoom(new_zoom, center_x, center_y)

    def zoom_out(
        self,
        factor: float = 0.8,
        center_x: Optional[float] = None,
        center_y: Optional[float] = None,
    ) -> None:
        """Decrease zoom level.

        Args:
            factor: Zoom divisor (default: 0.8)
            center_x: X coordinate to center zoom on (optional)
            center_y: Y coordinate to center zoom on (optional)
        """
        new_zoom = max(self.zoom_level * factor, MIN_ZOOM)
        self.set_zoom(new_zoom, center_x, center_y)

    def pan(self, delta_x: float, delta_y: float) -> None:
        """Pan viewport by offset.

        Args:
            delta_x: Horizontal pan offset
            delta_y: Vertical pan offset
        """
        self.pan_offset_x += delta_x
        self.pan_offset_y += delta_y
        self.constrain_pan()
        self._recalculate_display()

        logger.debug(f"Pan: offset=({self.pan_offset_x}, {self.pan_offset_y})")

    def reset_zoom(self) -> None:
        """Reset zoom to fit-to-window (1.0) and center image."""
        self.zoom_level = DEFAULT_ZOOM
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self._recalculate_display()

        logger.debug("Zoom reset to fit-to-window")

    def resize_window(self, width: int, height: int) -> None:
        """Update window dimensions and recalculate viewport.

        Args:
            width: New window width
            height: New window height
        """
        if width <= 0 or height <= 0:
            raise ValueError("Window dimensions must be positive")

        self.window_width = width
        self.window_height = height
        self._recalculate_display()
        self.constrain_pan()

        logger.debug(f"Window resized to {width}x{height}")

    def get_display_size(self) -> tuple[float, float]:
        """Get calculated display size (width, height) in pixels.

        Returns:
            Tuple of (display_width, display_height)
        """
        return (self.display_width, self.display_height)

    def get_visible_region(self) -> dict:
        """Get visible region coordinates.

        Returns:
            Dictionary with x, y, width, height of visible region
        """
        return {
            "x": self.visible_region_x,
            "y": self.visible_region_y,
            "width": self.visible_region_width,
            "height": self.visible_region_height,
        }

    def constrain_pan(self) -> None:
        """Ensure pan offsets are within image boundaries at current zoom level."""
        # Calculate maximum pan offsets based on zoom and image size
        max_pan_x = max(0, (self.display_width - self.window_width) / 2)
        max_pan_y = max(0, (self.display_height - self.window_height) / 2)

        self.pan_offset_x = max(-max_pan_x, min(max_pan_x, self.pan_offset_x))
        self.pan_offset_y = max(-max_pan_y, min(max_pan_y, self.pan_offset_y))

