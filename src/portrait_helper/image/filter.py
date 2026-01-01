"""Image filter library for Portrait Helper."""

import logging
from typing import Optional
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


class FilterState:
    """Represents the current image filter state."""

    def __init__(
        self,
        original_pixel_data: Optional[PILImage.Image] = None,
        grayscale_enabled: bool = False,
    ):
        """Initialize FilterState.

        Args:
            original_pixel_data: Original image data (preserved for toggle)
            grayscale_enabled: Whether black/white filter is active
        """
        self.grayscale_enabled = grayscale_enabled
        self.original_pixel_data = original_pixel_data
        self.filtered_pixel_data: Optional[PILImage.Image] = None

        if original_pixel_data is not None:
            logger.debug("FilterState created with original image data")
        else:
            logger.debug("FilterState created without image data")

    def apply_grayscale_filter(self, image: PILImage.Image) -> PILImage.Image:
        """Apply grayscale filter to image.

        Args:
            image: PIL Image to convert to grayscale

        Returns:
            Grayscale PIL Image
        """
        if image.mode == "L":
            # Already grayscale
            return image.copy()

        grayscale = image.convert("L")
        logger.debug("Grayscale filter applied")
        return grayscale

    def toggle_grayscale(self) -> None:
        """Toggle grayscale filter on/off."""
        if self.original_pixel_data is None:
            raise ValueError("No original image data available")

        if self.grayscale_enabled:
            # Disable: restore original (keep cache for reuse)
            self.grayscale_enabled = False
            logger.debug("Grayscale filter disabled, restored original")
        else:
            # Enable: apply filter and cache
            if self.filtered_pixel_data is None:
                self.filtered_pixel_data = self.apply_grayscale_filter(self.original_pixel_data)
            self.grayscale_enabled = True
            logger.debug("Grayscale filter enabled")

    def set_grayscale(self, enabled: bool) -> None:
        """Set grayscale filter to specific state.

        Args:
            enabled: True to enable grayscale, False to disable
        """
        if self.original_pixel_data is None:
            raise ValueError("No original image data available")

        if enabled == self.grayscale_enabled:
            # Already in the desired state, no change needed
            return

        if enabled:
            # Enable: apply filter and cache
            if self.filtered_pixel_data is None:
                self.filtered_pixel_data = self.apply_grayscale_filter(self.original_pixel_data)
            self.grayscale_enabled = True
            logger.debug("Grayscale filter enabled")
        else:
            # Disable: restore original (keep cache for reuse)
            self.grayscale_enabled = False
            logger.debug("Grayscale filter disabled, restored original")

    def get_current_image(self) -> Optional[PILImage.Image]:
        """Get current image (original or filtered based on state).

        Returns:
            PIL Image (original or filtered)
        """
        if self.grayscale_enabled:
            return self.filtered_pixel_data
        return self.original_pixel_data

