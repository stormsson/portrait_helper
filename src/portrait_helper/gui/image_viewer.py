"""Image viewer widget for Portrait Helper."""

import logging
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QImage, QWheelEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF, QPoint
from PIL import Image as PILImage

from portrait_helper.image.loader import Image
from portrait_helper.image.viewport import Viewport
from portrait_helper.image.filter import FilterState
from portrait_helper.grid.overlay import GridOverlay
from portrait_helper.gui.context_menu import ImageViewerContextMenu

logger = logging.getLogger(__name__)


class ImageViewer(QWidget):
    """Widget for displaying images with aspect ratio preservation."""

    def __init__(self, parent=None):
        """Initialize image viewer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._image: Optional[Image] = None
        self._viewport: Optional[Viewport] = None
        self._filter_state: Optional[FilterState] = None
        self._grid_overlay: Optional[GridOverlay] = None
        self._panning = False
        self._last_pan_point: Optional[QPointF] = None
        self._context_menu: Optional[ImageViewerContextMenu] = None
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)  # Enable mouse tracking for panning
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        logger.debug("ImageViewer initialized")

    def set_image(self, image: Image):
        """Set image to display.

        Args:
            image: Image object to display
        """
        self._image = image

        # Create viewport for image
        if image.is_loaded:
            self._viewport = Viewport(
                image_width=image.width,
                image_height=image.height,
                window_width=self.width(),
                window_height=self.height(),
            )
            # Create filter state with original image data
            self._filter_state = FilterState(original_pixel_data=image.get_pixel_data())
            logger.info(f"Image set: {image.width}x{image.height}")
        else:
            logger.warning("Attempted to set unloaded image")
            self._filter_state = None

        self.update()

    def has_image(self) -> bool:
        """Check if image is loaded.

        Returns:
            True if image is loaded, False otherwise
        """
        return self._image is not None and self._image.is_loaded

    def set_grid_overlay(self, grid_overlay: GridOverlay):
        """Set grid overlay to render.

        Args:
            grid_overlay: GridOverlay instance
        """
        self._grid_overlay = grid_overlay
        self.update()
        logger.debug("Grid overlay set")

    def update_display(self):
        """Update display after resize or other changes."""
        if self._image and self._viewport:
            self._viewport.resize_window(self.width(), self.height())
            # Update grid cell size if grid overlay is set
            if self._grid_overlay:
                display_width, display_height = self._viewport.get_display_size()
                self._grid_overlay.config.calculate_cell_size(
                    viewport_width=display_width, viewport_height=display_height
                )
        self.update()

    def paintEvent(self, event):
        """Paint image on widget.

        Args:
            event: Paint event
        """
        if not self.has_image() or self._viewport is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get display size from viewport
        display_width, display_height = self._viewport.get_display_size()

        # Calculate position to center image (accounting for pan offset)
        x = (self.width() - display_width) / 2 + self._viewport.pan_offset_x
        y = (self.height() - display_height) / 2 + self._viewport.pan_offset_y

        # Get current image (original or filtered based on filter state)
        if self._filter_state:
            pil_image = self._filter_state.get_current_image()
            if pil_image is None:
                # Fallback to original if filter state has no image
                pil_image = self._image.get_pixel_data()
        else:
            pil_image = self._image.get_pixel_data()
        
        # Convert PIL Image to QPixmap
        qimage = self._pil_to_qimage(pil_image)

        # Scale image to display size
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(
            int(display_width),
            int(display_height),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Draw image centered
        painter.drawPixmap(int(x), int(y), scaled_pixmap)

        # Draw grid overlay if configured
        if self._grid_overlay:
            self._grid_overlay.render(
                painter,
                viewport_x=x,
                viewport_y=y,
                viewport_width=display_width,
                viewport_height=display_height,
            )

    def _pil_to_qimage(self, pil_image) -> QImage:
        """Convert PIL Image to QImage.

        Args:
            pil_image: PIL Image object

        Returns:
            QImage object
        """
        # Try PIL.ImageQt first if available (handles format-specific conversions automatically)
        try:
            from PIL import ImageQt
            if hasattr(ImageQt, "toqimage"):
                # PIL.ImageQt handles WebP and other formats correctly
                qimage = ImageQt.toqimage(pil_image)
                if not qimage.isNull():
                    logger.debug("Converted PIL image to QImage using PIL.ImageQt")
                    return qimage
        except ImportError:
            # PIL.ImageQt not available, fall back to manual conversion
            pass
        except Exception as e:
            # If ImageQt fails, fall back to manual conversion
            logger.debug(f"PIL.ImageQt conversion failed: {e}, using manual conversion")

        # Manual conversion with explicit stride calculation
        # Ensure image is in RGB mode for consistent conversion
        if pil_image.mode not in ("RGB", "RGBA", "L"):
            pil_image = pil_image.convert("RGB")

        # Convert PIL image to bytes in format QImage expects
        if pil_image.mode == "RGB":
            # QImage expects RGB888 format with tightly-packed bytes
            # Calculate expected bytes: width * height * 3 (RGB = 3 bytes per pixel)
            bytes_img = pil_image.tobytes("raw", "RGB")
            expected_bytes = pil_image.size[0] * pil_image.size[1] * 3
            
            # Verify bytes length matches expected (ensures no padding/stride issues)
            if len(bytes_img) != expected_bytes:
                logger.warning(
                    f"Bytes length mismatch: expected {expected_bytes}, got {len(bytes_img)}. "
                    f"Image size: {pil_image.size}, mode: {pil_image.mode}"
                )
                # Recreate image to ensure tight packing
                rgb_image = pil_image.convert("RGB")
                bytes_img = rgb_image.tobytes("raw", "RGB")
            
            # Create QImage with explicit stride (bytes per line = width * 3)
            stride = pil_image.size[0] * 3
            qimage = QImage(bytes_img, pil_image.size[0], pil_image.size[1], stride, QImage.Format.Format_RGB888)
            
        elif pil_image.mode == "RGBA":
            # QImage expects RGBA8888 format with tightly-packed bytes
            bytes_img = pil_image.tobytes("raw", "RGBA")
            expected_bytes = pil_image.size[0] * pil_image.size[1] * 4
            
            # Verify bytes length matches expected
            if len(bytes_img) != expected_bytes:
                logger.warning(
                    f"RGBA bytes length mismatch: expected {expected_bytes}, got {len(bytes_img)}"
                )
                rgba_image = pil_image.convert("RGBA")
                bytes_img = rgba_image.tobytes("raw", "RGBA")
            
            # Create QImage with explicit stride (bytes per line = width * 4)
            stride = pil_image.size[0] * 4
            qimage = QImage(bytes_img, pil_image.size[0], pil_image.size[1], stride, QImage.Format.Format_RGBA8888)
            
        elif pil_image.mode == "L":
            # Convert grayscale to RGB
            rgb_image = pil_image.convert("RGB")
            bytes_img = rgb_image.tobytes("raw", "RGB")
            stride = rgb_image.size[0] * 3
            qimage = QImage(bytes_img, rgb_image.size[0], rgb_image.size[1], stride, QImage.Format.Format_RGB888)
        else:
            # Convert other modes to RGB
            rgb_image = pil_image.convert("RGB")
            bytes_img = rgb_image.tobytes("raw", "RGB")
            stride = rgb_image.size[0] * 3
            qimage = QImage(bytes_img, rgb_image.size[0], rgb_image.size[1], stride, QImage.Format.Format_RGB888)

        return qimage

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel events for zooming.

        Args:
            event: Wheel event
        """
        if not self.has_image() or self._viewport is None:
            super().wheelEvent(event)
            return

        # Zoom in or out based on wheel delta
        # Don't pass center coordinates - this will zoom without adjusting pan
        # Reduced sensitivity: 20% of original (1.2 → 1.02, 0.8 → 0.98)
        delta = event.angleDelta().y()
        if delta > 0:
            self._viewport.zoom_in(factor=1.02)
        elif delta < 0:
            self._viewport.zoom_out(factor=0.98)

        # Update grid if present
        if self._grid_overlay:
            display_width, display_height = self._viewport.get_display_size()
            self._grid_overlay.config.calculate_cell_size(
                viewport_width=display_width, viewport_height=display_height
            )

        self.update()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for panning.

        Args:
            event: Mouse event
        """
        if not self.has_image() or self._viewport is None:
            super().mousePressEvent(event)
            return

        # Start panning if left button pressed
        if event.button() == Qt.LeftButton:
            self._panning = True
            self._last_pan_point = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for panning.

        Args:
            event: Mouse event
        """
        if not self.has_image() or self._viewport is None:
            super().mouseMoveEvent(event)
            return

        if self._panning and self._last_pan_point is not None:
            # Calculate pan delta
            delta_x = event.position().x() - self._last_pan_point.x()
            delta_y = event.position().y() - self._last_pan_point.y()

            # Pan viewport
            self._viewport.pan(delta_x=delta_x, delta_y=delta_y)

            # Update last pan point
            self._last_pan_point = event.position()

            # Update grid if present
            if self._grid_overlay:
                display_width, display_height = self._viewport.get_display_size()
                self._grid_overlay.config.calculate_cell_size(
                    viewport_width=display_width, viewport_height=display_height
                )

            self.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events for panning.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton and self._panning:
            self._panning = False
            self._last_pan_point = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def enterEvent(self, event) -> None:
        """Handle mouse enter events."""
        if self.has_image() and self._viewport is not None:
            self.setCursor(Qt.OpenHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Handle mouse leave events."""
        if not self._panning:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def set_context_menu(self, context_menu: ImageViewerContextMenu) -> None:
        """Set context menu for image viewer.

        Args:
            context_menu: ImageViewerContextMenu instance
        """
        self._context_menu = context_menu

    def _show_context_menu(self, position: QPoint) -> None:
        """Show context menu at position.

        Args:
            position: Position to show menu
        """
        if self._context_menu:
            self._context_menu.exec(self.mapToGlobal(position))

    def reset_zoom(self) -> None:
        """Reset zoom to fit-to-window."""
        if self._viewport:
            self._viewport.reset_zoom()
            # Update grid if present
            if self._grid_overlay:
                display_width, display_height = self._viewport.get_display_size()
                self._grid_overlay.config.calculate_cell_size(
                    viewport_width=display_width, viewport_height=display_height
                )
            self.update()
            logger.debug("Zoom reset to fit-to-window")

    def toggle_grayscale(self) -> None:
        """Toggle grayscale filter while preserving viewport state."""
        if self._filter_state:
            # Capture viewport state before toggle
            zoom_before = self._viewport.zoom_level if self._viewport else None
            pan_x_before = self._viewport.pan_offset_x if self._viewport else None
            pan_y_before = self._viewport.pan_offset_y if self._viewport else None
            
            # Toggle filter
            self._filter_state.toggle_grayscale()
            
            # Verify viewport state is preserved (should be unchanged)
            if self._viewport:
                assert self._viewport.zoom_level == zoom_before, "Viewport zoom should be preserved"
                assert self._viewport.pan_offset_x == pan_x_before, "Viewport pan_x should be preserved"
                assert self._viewport.pan_offset_y == pan_y_before, "Viewport pan_y should be preserved"
            
            self.update()
            logger.debug(f"Grayscale filter toggled: {self._filter_state.grayscale_enabled}")
        else:
            logger.warning("Cannot toggle grayscale: no filter state available")

