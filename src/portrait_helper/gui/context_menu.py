"""Context menu for image viewer."""

import logging
from typing import Optional
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint

logger = logging.getLogger(__name__)


class ImageViewerContextMenu(QMenu):
    """Context menu for image viewer widget."""

    def __init__(self, parent=None):
        """Initialize context menu.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._reset_zoom_action: Optional[QAction] = None
        self._toggle_grayscale_action: Optional[QAction] = None
        self._toggle_grid_action: Optional[QAction] = None
        self._set_as_origin_action: Optional[QAction] = None
        self._setup_menu()

    def _setup_menu(self):
        """Setup menu actions."""
        # Reset Zoom action
        self._reset_zoom_action = QAction("Reset Zoom", self)
        self._reset_zoom_action.setShortcut(Qt.Key_0)  # 0 key for reset
        self.addAction(self._reset_zoom_action)

        # Add separator
        self.addSeparator()

        # Toggle Grid action
        self._toggle_grid_action = QAction("Toggle Grid", self)
        self.addAction(self._toggle_grid_action)

        # Set as (1, 1) action
        self._set_as_origin_action = QAction("Set as (1, 1)", self)
        self._set_as_origin_action.setEnabled(False)  # Disabled by default
        self.addAction(self._set_as_origin_action)

        # Add separator after set as (1, 1)
        self.addSeparator()

        # Toggle Black/White Mode action
        self._toggle_grayscale_action = QAction("Toggle Black/White Mode", self)
        self.addAction(self._toggle_grayscale_action)

        logger.debug("Context menu initialized")

    def get_reset_zoom_action(self) -> QAction:
        """Get reset zoom action.

        Returns:
            QAction for reset zoom
        """
        return self._reset_zoom_action

    def get_toggle_grayscale_action(self) -> QAction:
        """Get toggle grayscale action.

        Returns:
            QAction for toggle grayscale
        """
        return self._toggle_grayscale_action

    def get_toggle_grid_action(self) -> QAction:
        """Get toggle grid action.

        Returns:
            QAction for toggle grid
        """
        return self._toggle_grid_action

    def get_set_as_origin_action(self) -> QAction:
        """Get set as origin action.

        Returns:
            QAction for set as (1, 1)
        """
        return self._set_as_origin_action

