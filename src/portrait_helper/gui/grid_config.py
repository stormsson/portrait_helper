"""Grid configuration panel widget for Portrait Helper."""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QPushButton,
    QLabel,
    QColorDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from portrait_helper.grid.config import GridConfiguration, MIN_SUBDIVISIONS, MAX_SUBDIVISIONS

logger = logging.getLogger(__name__)


class GridConfigPanel(QWidget):
    """Widget for configuring grid overlay settings."""

    # Signal emitted when grid configuration changes
    config_changed = Signal()

    def __init__(self, config: GridConfiguration, parent=None):
        """Initialize grid configuration panel.

        Args:
            config: GridConfiguration instance to control
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._update_ui()

        logger.debug("GridConfigPanel initialized")

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Show/Hide checkbox
        self.visible_checkbox = QCheckBox("Show Grid")
        self.visible_checkbox.stateChanged.connect(self._on_visible_changed)
        layout.addWidget(self.visible_checkbox)

        # Size controls
        size_layout = QHBoxLayout()
        size_label = QLabel("Grid Size:")
        size_layout.addWidget(size_label)

        self.decrease_button = QPushButton("-")
        self.decrease_button.setMaximumWidth(30)
        self.decrease_button.clicked.connect(self._on_decrease_size)
        size_layout.addWidget(self.decrease_button)

        self.size_label = QLabel()
        self.size_label.setMinimumWidth(50)
        self.size_label.setAlignment(Qt.AlignCenter)
        size_layout.addWidget(self.size_label)

        self.increase_button = QPushButton("+")
        self.increase_button.setMaximumWidth(30)
        self.increase_button.clicked.connect(self._on_increase_size)
        size_layout.addWidget(self.increase_button)

        size_layout.addStretch()
        layout.addLayout(size_layout)

        # Color picker
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        color_layout.addWidget(color_label)

        self.color_button = QPushButton()
        self.color_button.setMaximumWidth(50)
        self.color_button.clicked.connect(self._on_color_picker)
        color_layout.addWidget(self.color_button)

        color_layout.addStretch()
        layout.addLayout(color_layout)

        layout.addStretch()

    def _update_ui(self):
        """Update UI to reflect current configuration."""
        # Update visibility checkbox (block signals to prevent feedback loop)
        self.visible_checkbox.blockSignals(True)
        self.visible_checkbox.setChecked(self.config.visible)
        self.visible_checkbox.blockSignals(False)

        # Update size label
        self.size_label.setText(str(self.config.subdivision_count))

        # Update button states
        self.decrease_button.setEnabled(
            self.config.subdivision_count > MIN_SUBDIVISIONS
        )
        self.increase_button.setEnabled(
            self.config.subdivision_count < MAX_SUBDIVISIONS
        )

        # Update color button
        self._update_color_button()

    def _update_color_button(self):
        """Update color button appearance."""
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

        # Set button background color
        self.color_button.setStyleSheet(
            f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
        )

    def _on_visible_changed(self, state: int):
        """Handle visibility checkbox change.

        Args:
            state: Checkbox state (Qt.Checked or Qt.Unchecked)
        """
        self.config.toggle_visible()
        self.config_changed.emit()
        logger.debug(f"Grid visibility changed: {self.config.visible}")

    def _on_increase_size(self):
        """Handle increase size button click."""
        self.config.increase_size()
        self._update_ui()
        self.config_changed.emit()
        logger.debug(f"Grid size increased: {self.config.subdivision_count}")

    def _on_decrease_size(self):
        """Handle decrease size button click."""
        self.config.decrease_size()
        self._update_ui()
        self.config_changed.emit()
        logger.debug(f"Grid size decreased: {self.config.subdivision_count}")

    def _on_color_picker(self):
        """Handle color picker button click."""
        # Get current color
        if len(self.config.color) == 3:
            current_color = QColor(
                self.config.color[0],
                self.config.color[1],
                self.config.color[2],
            )
        else:  # RGBA
            current_color = QColor(
                self.config.color[0],
                self.config.color[1],
                self.config.color[2],
                self.config.color[3],
            )

        # Open color dialog
        color = QColorDialog.getColor(current_color, self, "Select Grid Color")
        if color.isValid():
            # Update configuration
            if color.alpha() == 255:
                # Opaque color, use RGB
                self.config.set_color((color.red(), color.green(), color.blue()))
            else:
                # Transparent color, use RGBA
                self.config.set_color(
                    (color.red(), color.green(), color.blue(), color.alpha())
                )
            self._update_color_button()
            self.config_changed.emit()
            logger.debug(f"Grid color changed: {self.config.color}")

