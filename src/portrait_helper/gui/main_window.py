"""Main application window for Portrait Helper."""

import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QMenu,
    QFileDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QInputDialog,
    QApplication,
    QDockWidget,
)
from PySide6.QtCore import Qt, QUrl, QBuffer
from PySide6.QtGui import QKeySequence, QShortcut, QPainter, QImage, QPixmap, QPen, QColor
from typing import Optional, Tuple

from portrait_helper.image.loader import load_from_file, load_from_url, ImageLoadError
from portrait_helper.gui.image_viewer import ImageViewer
from portrait_helper.grid.config import GridConfiguration
from portrait_helper.grid.overlay import GridOverlay
from portrait_helper.gui.grid_config import GridConfigPanel
from portrait_helper.gui.context_menu import ImageViewerContextMenu

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Portrait Helper")
        self.setMinimumSize(400, 300)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create image viewer
        self.image_viewer = ImageViewer()
        layout.addWidget(self.image_viewer)

        # Create grid configuration and overlay
        self.grid_config = GridConfiguration(visible=False)
        self.grid_overlay = GridOverlay(self.grid_config)
        self.image_viewer.set_grid_overlay(self.grid_overlay)

        # Grid offset for coordinate display (0-indexed coordinates that should be treated as (1,1))
        self.grid_offset: Optional[Tuple[int, int]] = None

        # Create status bar
        self._create_status_bar()

        # Create grid configuration panel dock
        self._create_grid_panel()

        # Create context menu
        self._create_context_menu()

        # Create menu bar
        self._create_menu_bar()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Connect cursor position signal
        self.image_viewer.cursor_position_changed.connect(self._on_cursor_position_changed)

        logger.info("Main window initialized")

    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        load_action = file_menu.addAction("&Load Image...", self.load_image_from_file)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        export_action = file_menu.addAction("&Export Image...", self.export_image)
        export_action.setShortcut(QKeySequence("Ctrl+S"))

        # Edit menu (for future use)
        edit_menu = menubar.addMenu("&Edit")

        # View menu
        view_menu = menubar.addMenu("&View")
        self.grid_panel_action = view_menu.addAction("&Grid Panel", self._toggle_grid_panel)
        self.grid_panel_action.setCheckable(True)
        self.grid_panel_action.setShortcut(QKeySequence("Ctrl+,"))
        view_menu.addAction("Toggle &Grid", self._toggle_grid_visibility).setShortcut(QKeySequence("Ctrl+G"))
        view_menu.addAction("Reset &Zoom", self._reset_zoom).setShortcut(QKeySequence("0"))
        view_menu.addAction("Toggle &Black/White", self._toggle_grayscale).setShortcut(QKeySequence("Ctrl+B"))

        # Help menu (for future use)
        help_menu = menubar.addMenu("&Help")

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for all menu functions.
        
        All shortcuts use QKeySequence which automatically handles platform differences:
        - Windows/Linux: Ctrl+Key
        - macOS: Cmd+Key (automatically converted)
        """
        # File menu shortcuts
        # Ctrl+O: Load Image (set in menu)
        
        # View menu shortcuts (all set in menu for consistency)
        # Ctrl+, (Cmd+, on macOS): Toggle Grid Panel (set in menu)
        # Ctrl+G: Toggle Grid (set in menu)
        # 0: Reset Zoom (set in menu)
        # Ctrl+B: Toggle Black/White (set in menu)
        
        # Special shortcuts handled in keyPressEvent
        # Ctrl+V (Cmd+V on macOS): URL paste from clipboard
        # ESC: Exit application
        # +: Increase grid subdivisions (also toggles grid on if hidden)
        # -: Decrease grid subdivisions (also toggles grid on if hidden)
        
        # All shortcuts are platform-aware via QKeySequence
        logger.debug("Keyboard shortcuts configured")

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Handle ESC: Exit application
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
            return
        
        # Handle +: Increase grid subdivisions (also toggle grid on if hidden)
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self._increase_grid_subdivisions()
            event.accept()
            return
        
        # Handle -: Decrease grid subdivisions (also toggle grid on if hidden)
        if event.key() == Qt.Key_Minus:
            self._decrease_grid_subdivisions()
            event.accept()
            return
        
        # Handle Ctrl+V (Cmd+V on macOS) for URL paste
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            # Check if clipboard contains URL
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text and (text.startswith("http://") or text.startswith("https://")):
                self.load_image_from_url(text)
                event.accept()
                return

        super().keyPressEvent(event)

    def load_image_from_file(self):
        """Load image from file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)",
        )

        if file_path:
            try:
                logger.info(f"Loading image from file: {file_path}")
                image = load_from_file(file_path)
                self.image_viewer.set_image(image)
                # Reset grid offset when new image is loaded
                self.grid_offset = None
                self.grid_config.origin_cell = None
                # Update grid cell size for new image
                self._update_grid_for_image()
                # Update monochrome checkbox (reset to unchecked, enable if image loaded)
                self._update_monochrome_checkbox()
                self.grid_panel.set_monochrome_enabled(True)
                # Update action state
                self._update_set_as_origin_action_state()
                logger.info("Image loaded successfully")
            except FileNotFoundError as e:
                self._show_error("File Not Found", f"The file could not be found:\n{str(e)}")
            except ImageLoadError as e:
                self._show_error("Image Load Error", f"Failed to load image:\n{str(e)}")
            except Exception as e:
                self._show_error("Error", f"An error occurred:\n{str(e)}")
                logger.error(f"Error loading image: {e}", exc_info=True)

    def load_image_from_url(self, url: str = None):
        """Load image from URL.

        Args:
            url: URL to load (if None, prompts user)
        """
        if url is None:
            url, ok = QInputDialog.getText(
                self,
                "Load Image from URL",
                "Enter image URL:",
            )
            if not ok or not url:
                return

        try:
            logger.info(f"Loading image from URL: {url}")
            image = load_from_url(url)
            self.image_viewer.set_image(image)
            # Reset grid offset when new image is loaded
            self.grid_offset = None
            self.grid_config.origin_cell = None
            # Update grid cell size for new image
            self._update_grid_for_image()
            # Update monochrome checkbox (reset to unchecked, enable if image loaded)
            self._update_monochrome_checkbox()
            self.grid_panel.set_monochrome_enabled(True)
            # Update action state
            self._update_set_as_origin_action_state()
            logger.info("Image loaded successfully from URL")
        except Exception as e:
            self._show_error("Network Error", f"Failed to load image from URL:\n{str(e)}")
            logger.error(f"Error loading image from URL: {e}", exc_info=True)

    def _show_error(self, title: str, message: str):
        """Display error message dialog.

        Args:
            title: Error dialog title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def resizeEvent(self, event):
        """Handle window resize event.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        # Image viewer will handle aspect ratio preservation
        if self.image_viewer.has_image():
            self.image_viewer.update_display()

    def _create_context_menu(self):
        """Create context menu for image viewer with all available options."""
        context_menu = ImageViewerContextMenu(self)
        context_menu.get_reset_zoom_action().triggered.connect(self._reset_zoom)
        context_menu.get_toggle_grid_action().triggered.connect(self._toggle_grid_visibility)
        context_menu.get_set_as_origin_action().triggered.connect(self._on_set_as_origin)
        context_menu.get_toggle_grayscale_action().triggered.connect(self._toggle_grayscale)
        self.image_viewer.set_context_menu(context_menu)
        # Store reference to context menu for action state updates
        self._context_menu = context_menu
        # Set initial action state
        self._update_set_as_origin_action_state()

    def _create_status_bar(self):
        """Create status bar at bottom of window."""
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
        self.status_bar = status_bar

    def _create_grid_panel(self):
        """Create grid configuration panel dock."""
        self.grid_panel = GridConfigPanel(self.grid_config)
        self.grid_panel.config_changed.connect(self._on_grid_config_changed)
        self.grid_panel.monochrome_changed.connect(self._on_monochrome_changed)

        dock = QDockWidget("Grid Configuration", self)
        dock.setWidget(self.grid_panel)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(False)  # Hidden by default

        self.grid_dock = dock
        
        # Initially disable monochrome checkbox (no image loaded yet)
        self.grid_panel.set_monochrome_enabled(False)

    def _toggle_grid_panel(self):
        """Toggle grid configuration panel visibility."""
        visible = not self.grid_dock.isVisible()
        self.grid_dock.setVisible(visible)
        self.grid_panel_action.setChecked(visible)

    def _toggle_grid_visibility(self):
        """Toggle grid visibility."""
        self.grid_config.toggle_visible()
        # Update checkbox in grid panel to reflect the change
        self.grid_panel._update_ui()
        self.image_viewer.update()
        # Reset offset when grid is disabled
        if not self.grid_config.visible:
            self.grid_offset = None
            self.grid_config.origin_cell = None
            # Trigger repaint to remove label
            self.image_viewer.update()
        # Update action state
        self._update_set_as_origin_action_state()
        logger.debug(f"Grid visibility toggled: {self.grid_config.visible}")

    def _update_grid_for_image(self):
        """Update grid cell size when image is loaded."""
        if self.image_viewer.has_image() and self.image_viewer._viewport:
            display_width, display_height = self.image_viewer._viewport.get_display_size()
            self.grid_config.calculate_cell_size(
                viewport_width=display_width, viewport_height=display_height
            )

    def _reset_zoom(self):
        """Reset zoom to fit-to-window."""
        self.image_viewer.reset_zoom()

    def _on_grid_config_changed(self):
        """Handle grid configuration changes."""
        # Update grid cell size if image is loaded
        self._update_grid_for_image()
        # Trigger repaint
        self.image_viewer.update()
        # Reset offset when grid is disabled
        if not self.grid_config.visible:
            self.grid_offset = None
            self.grid_config.origin_cell = None
        # Update action state
        self._update_set_as_origin_action_state()

    def _toggle_grayscale(self):
        """Toggle black/white (grayscale) filter."""
        self.image_viewer.toggle_grayscale()
        # Update checkbox in grid panel to reflect the change
        if hasattr(self, 'grid_panel'):
            self._update_monochrome_checkbox()

    def _on_monochrome_changed(self, enabled: bool):
        """Handle monochrome checkbox change from grid panel.

        Args:
            enabled: Whether monochrome should be enabled
        """
        if not self.image_viewer.has_image():
            logger.warning("Cannot set monochrome: no image loaded")
            return
        
        # Set grayscale to the desired state (not toggle)
        self.image_viewer.set_grayscale(enabled)
        logger.debug(f"Monochrome changed via checkbox: {enabled}")

    def _update_monochrome_checkbox(self):
        """Update monochrome checkbox state to match current grayscale state."""
        if hasattr(self, 'grid_panel'):
            current_state = self.image_viewer.is_grayscale_enabled()
            self.grid_panel.set_monochrome_state(current_state)

    def _increase_grid_subdivisions(self):
        """Increase grid subdivisions (more separations). Also toggles grid on if hidden."""
        if not self.grid_config.visible:
            self.grid_config.toggle_visible()
            # Update checkbox in grid panel to reflect the change
            if hasattr(self, 'grid_panel'):
                self.grid_panel._update_ui()
        
        self.grid_config.increase_size()
        # Update grid cell size for new subdivision count
        self._update_grid_for_image()
        # Trigger repaint
        self.image_viewer.update()
        # Update action state (grid visibility may have changed)
        self._update_set_as_origin_action_state()
        logger.debug(f"Grid subdivisions increased: {self.grid_config.subdivision_count}")

    def _decrease_grid_subdivisions(self):
        """Decrease grid subdivisions (fewer separations). Also toggles grid on if hidden."""
        if not self.grid_config.visible:
            self.grid_config.toggle_visible()
            # Update checkbox in grid panel to reflect the change
            if hasattr(self, 'grid_panel'):
                self.grid_panel._update_ui()
        
        self.grid_config.decrease_size()
        # Update grid cell size for new subdivision count
        self._update_grid_for_image()
        # Trigger repaint
        self.image_viewer.update()
        # Update action state (grid visibility may have changed)
        self._update_set_as_origin_action_state()
        logger.debug(f"Grid subdivisions decreased: {self.grid_config.subdivision_count}")

    def export_image(self):
        """Export image with current settings (grid, monochrome, etc.) to file."""
        if not self.image_viewer.has_image():
            self._show_error("No Image", "Please load an image before exporting.")
            return

        # Open file dialog for save path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)",
        )

        if not file_path:
            return

        try:
            # Get current filtered image (with monochrome applied if enabled)
            if self.image_viewer._filter_state:
                pil_image = self.image_viewer._filter_state.get_current_image()
                if pil_image is None:
                    pil_image = self.image_viewer._image.get_pixel_data()
            else:
                pil_image = self.image_viewer._image.get_pixel_data()

            # Convert PIL Image to QImage
            qimage = self.image_viewer._pil_to_qimage(pil_image)
            pixmap = QPixmap.fromImage(qimage)

            # If grid is visible, render it on top
            if self.grid_config.visible:
                # Create a painter to draw on the pixmap
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)

                # Calculate grid cell size for full image dimensions
                image_width = pil_image.width
                image_height = pil_image.height
                self.grid_config.calculate_cell_size(
                    viewport_width=image_width,
                    viewport_height=image_height
                )

                # Render grid overlay on the full image (viewport is the entire image)
                self.grid_overlay.render(
                    painter,
                    viewport_x=0,
                    viewport_y=0,
                    viewport_width=image_width,
                    viewport_height=image_height,
                )
                painter.end()

            # Convert QPixmap back to PIL Image for saving
            # Use QBuffer to convert QPixmap to PIL Image
            from io import BytesIO
            from PIL import Image as PILImage
            
            # Save QPixmap to QBuffer as PNG (lossless)
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            pixmap.save(buffer, "PNG")
            buffer.close()
            
            # Get bytes from buffer and load with PIL
            image_data = buffer.data()
            pil_export = PILImage.open(BytesIO(image_data))
            # Convert to RGB if needed (handles RGBA from PNG)
            if pil_export.mode != "RGB":
                pil_export = pil_export.convert("RGB")

            # Save the image
            pil_export.save(file_path)
            logger.info(f"Image exported successfully to: {file_path}")
            
        except Exception as e:
            self._show_error("Export Error", f"Failed to export image:\n{str(e)}")
            logger.error(f"Error exporting image: {e}", exc_info=True)

    def _update_set_as_origin_action_state(self):
        """Update the enabled state of the 'set as (1, 1)' action based on grid visibility and image state."""
        if hasattr(self, '_context_menu'):
            action = self._context_menu.get_set_as_origin_action()
            # Enable only when grid overlay exists, grid is visible, and image is loaded
            enabled = (
                self.image_viewer._grid_overlay is not None
                and self.grid_config.visible
                and self.image_viewer.has_image()
            )
            action.setEnabled(enabled)

    def _on_set_as_origin(self):
        """Handle 'set as (1, 1)' action - store the grid coordinates of the clicked square as offset."""
        # Get the last context menu position
        position = self.image_viewer.get_last_context_menu_position()
        if position is None:
            logger.warning("Cannot set origin: no context menu position available")
            return

        # Get grid coordinates at that position
        grid_coords = self.image_viewer._get_grid_coordinates_from_position(position)
        if grid_coords[0] is None or grid_coords[1] is None:
            logger.warning("Cannot set origin: position is outside grid bounds")
            return

        # Store the offset (0-indexed coordinates that should be treated as (1,1))
        self.grid_offset = grid_coords
        # Store in grid config for label rendering
        self.grid_config.origin_cell = grid_coords
        # Trigger repaint to show the label
        self.image_viewer.update()
        logger.info(f"Grid origin set to: {grid_coords[0] + 1}, {grid_coords[1] + 1} (0-indexed: {grid_coords})")

    def _on_cursor_position_changed(self, grid_x: int, grid_y: int, percent_x: float, percent_y: float):
        """Handle cursor position change and update status bar.

        Args:
            grid_x: Grid X coordinate (0-indexed, -1 if outside image)
            grid_y: Grid Y coordinate (0-indexed, -1 if outside image)
            percent_x: X position percentage within grid cell (0-100)
            percent_y: Y position percentage within grid cell (0-100)
        """
        if grid_x < 0 or grid_y < 0:
            self.status_bar.showMessage("Ready")
        else:
            # Apply offset if set
            if self.grid_offset is not None:
                # Subtract the offset from the grid coordinates
                adjusted_x = grid_x - self.grid_offset[0]
                adjusted_y = grid_y - self.grid_offset[1]
                # Ensure coordinates don't go below 1 (minimum display is 1,1)
                display_x = max(1, adjusted_x + 1)
                display_y = max(1, adjusted_y + 1)
            else:
                # Show 1-indexed coordinates without offset
                display_x = grid_x + 1
                display_y = grid_y + 1
            
            status_text = f"Grid: ({display_x}, {display_y}) | Position: ({percent_x:.1f}%, {percent_y:.1f}%)"
            self.status_bar.showMessage(status_text)

