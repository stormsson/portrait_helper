"""Grid configuration library for Portrait Helper."""

import logging
from typing import Union, Tuple

logger = logging.getLogger(__name__)

# Constants
MIN_SUBDIVISIONS = 2
MAX_SUBDIVISIONS = 50
DEFAULT_SUBDIVISIONS = 3
DEFAULT_LINE_WIDTH = 1.0
DEFAULT_OPACITY = 1.0


class GridConfiguration:
    """Represents the grid overlay settings."""

    def __init__(
        self,
        visible: bool = False,
        subdivision_count: int = DEFAULT_SUBDIVISIONS,
        color: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = (255, 255, 255),
        line_width: float = DEFAULT_LINE_WIDTH,
        opacity: float = DEFAULT_OPACITY,
    ):
        """Initialize GridConfiguration.

        Args:
            visible: Whether grid is currently displayed
            subdivision_count: Number of grid subdivisions (e.g., 3 = 3x3 grid)
            color: Grid line color (RGB or RGBA tuple)
            line_width: Grid line width in pixels
            opacity: Grid opacity (0.0 to 1.0)
        """
        self.visible = visible
        self.subdivision_count = subdivision_count
        self.color = color
        self.line_width = line_width
        self.opacity = opacity
        self._cell_size = 0.0  # Will be calculated based on viewport

        self._validate()

        logger.debug(
            f"GridConfiguration created: visible={visible}, "
            f"subdivisions={subdivision_count}, color={color}"
        )

    def _validate(self) -> None:
        """Validate configuration values."""
        if not (MIN_SUBDIVISIONS <= self.subdivision_count <= MAX_SUBDIVISIONS):
            raise ValueError(
                f"Subdivision count must be between {MIN_SUBDIVISIONS} and {MAX_SUBDIVISIONS}"
            )
        if self.line_width <= 0:
            raise ValueError("Line width must be positive")
        if not (0.0 <= self.opacity <= 1.0):
            raise ValueError("Opacity must be between 0.0 and 1.0")
        if len(self.color) not in (3, 4):
            raise ValueError("Color must be RGB or RGBA tuple")

    def toggle_visible(self) -> None:
        """Toggle grid visibility."""
        self.visible = not self.visible
        logger.debug(f"Grid visibility toggled: {self.visible}")

    def increase_size(self) -> None:
        """Increase grid size (fewer subdivisions)."""
        if self.subdivision_count < MAX_SUBDIVISIONS:
            self.subdivision_count += 1
            self._validate()
            logger.debug(f"Grid size increased: subdivisions={self.subdivision_count}")

    def decrease_size(self) -> None:
        """Decrease grid size (more subdivisions)."""
        if self.subdivision_count > MIN_SUBDIVISIONS:
            self.subdivision_count -= 1
            self._validate()
            logger.debug(f"Grid size decreased: subdivisions={self.subdivision_count}")

    def set_color(self, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]) -> None:
        """Set grid line color.

        Args:
            color: RGB or RGBA tuple
        """
        if len(color) not in (3, 4):
            raise ValueError("Color must be RGB or RGBA tuple")
        self.color = color
        logger.debug(f"Grid color set to {color}")

    @property
    def cell_size(self) -> float:
        """Get calculated cell size in pixels."""
        return self._cell_size

    def calculate_cell_size(self, viewport_width: float, viewport_height: float) -> None:
        """Calculate cell size based on viewport dimensions.

        Args:
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
        """
        # Grid cells are always square, use smaller dimension
        min_dimension = min(viewport_width, viewport_height)
        self._cell_size = min_dimension / self.subdivision_count

        logger.debug(
            f"Cell size calculated: {self._cell_size} "
            f"(viewport={viewport_width}x{viewport_height}, subdivisions={self.subdivision_count})"
        )

