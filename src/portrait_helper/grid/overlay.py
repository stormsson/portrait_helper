"""Grid overlay rendering library for Portrait Helper."""

import logging
import math
from typing import List, Tuple
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import QRectF

from portrait_helper.grid.config import GridConfiguration

logger = logging.getLogger(__name__)


class GridOverlay:
    """Renders grid overlay on top of images."""

    def __init__(self, config: GridConfiguration):
        """Initialize GridOverlay.

        Args:
            config: GridConfiguration instance
        """
        self.config = config
        logger.debug("GridOverlay created")

    def calculate_grid_lines(
        self,
        viewport_x: float,
        viewport_y: float,
        viewport_width: float,
        viewport_height: float,
    ) -> Tuple[List[float], List[float]]:
        """Calculate grid line positions.

        Args:
            viewport_x: X position of viewport (image display position)
            viewport_y: Y position of viewport (image display position)
            viewport_width: Width of viewport (image display width)
            viewport_height: Height of viewport (image display height)

        Returns:
            Tuple of (vertical_lines, horizontal_lines) - lists of line positions
        """
        if not self.config.visible:
            return ([], [])

        # Calculate cell size based on viewport dimensions
        # Grid cells are always square, use smaller dimension to determine cell size
        min_dimension = min(viewport_width, viewport_height)
        cell_size = min_dimension / self.config.subdivision_count

        # Calculate vertical lines (x positions) - cover full width
        # Number of cells needed to cover the width
        num_vertical_cells = math.ceil(viewport_width / cell_size)
        vertical_lines = []
        for i in range(num_vertical_cells + 1):
            x = viewport_x + (i * cell_size)
            vertical_lines.append(x)

        # Calculate horizontal lines (y positions) - cover full height
        # Number of cells needed to cover the height
        num_horizontal_cells = math.ceil(viewport_height / cell_size)
        horizontal_lines = []
        for i in range(num_horizontal_cells + 1):
            y = viewport_y + (i * cell_size)
            horizontal_lines.append(y)

        logger.debug(
            f"Grid lines calculated: {len(vertical_lines)} vertical, "
            f"{len(horizontal_lines)} horizontal, cell_size={cell_size}, "
            f"viewport={viewport_width}x{viewport_height}"
        )

        return (vertical_lines, horizontal_lines)

    def render(
        self,
        painter: QPainter,
        viewport_x: float,
        viewport_y: float,
        viewport_width: float,
        viewport_height: float,
    ) -> None:
        """Render grid overlay.

        Args:
            painter: QPainter instance
            viewport_x: X position of viewport (image display position)
            viewport_y: Y position of viewport (image display position)
            viewport_width: Width of viewport (image display width)
            viewport_height: Height of viewport (image display height)
        """
        if not self.config.visible:
            return

        # Calculate grid lines
        vertical_lines, horizontal_lines = self.calculate_grid_lines(
            viewport_x, viewport_y, viewport_width, viewport_height
        )

        # Set up painter
        painter.save()

        # Convert color tuple to QColor
        if len(self.config.color) == 3:
            color = QColor(
                self.config.color[0],
                self.config.color[1],
                self.config.color[2],
            )
        else:  # RGBA
            color = QColor(
                self.config.color[0],
                self.config.color[1],
                self.config.color[2],
                self.config.color[3],
            )

        # Apply opacity
        color.setAlphaF(self.config.opacity)

        # Set pen for grid lines
        from PySide6.QtGui import QPen
        from PySide6.QtCore import Qt

        pen = QPen(color)
        pen.setWidthF(self.config.line_width)
        painter.setPen(pen)

        # Draw vertical lines
        for x in vertical_lines:
            painter.drawLine(
                int(x),
                int(viewport_y),
                int(x),
                int(viewport_y + viewport_height),
            )

        # Draw horizontal lines
        for y in horizontal_lines:
            painter.drawLine(
                int(viewport_x),
                int(y),
                int(viewport_x + viewport_width),
                int(y),
            )

        painter.restore()

        logger.debug(
            f"Grid rendered: {len(vertical_lines)} vertical lines, "
            f"{len(horizontal_lines)} horizontal lines"
        )

    def ensure_square_cells(
        self,
        viewport_width: float,
        viewport_height: float,
    ) -> Tuple[float, float]:
        """Ensure grid cells are always square.

        Args:
            viewport_width: Viewport width
            viewport_height: Viewport height

        Returns:
            Tuple of (effective_width, effective_height) for square grid
        """
        # Grid cells are always square, use smaller dimension
        min_dimension = min(viewport_width, viewport_height)

        # Return square dimensions
        return (min_dimension, min_dimension)

