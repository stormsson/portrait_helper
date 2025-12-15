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
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut

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

        # Create grid configuration panel dock
        self._create_grid_panel()

        # Create context menu
        self._create_context_menu()

        # Create menu bar
        self._create_menu_bar()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        logger.info("Main window initialized")

    def _create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        load_action = file_menu.addAction("&Load Image...", self.load_image_from_file)
        load_action.setShortcut(QKeySequence("Ctrl+O"))

        # Edit menu (for future use)
        edit_menu = menubar.addMenu("&Edit")

        # View menu
        view_menu = menubar.addMenu("&View")
        self.grid_panel_action = view_menu.addAction("&Grid Panel", self._toggle_grid_panel)
        self.grid_panel_action.setCheckable(True)
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
                # Update grid cell size for new image
                self._update_grid_for_image()
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
            # Update grid cell size for new image
            self._update_grid_for_image()
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
        context_menu.get_toggle_grayscale_action().triggered.connect(self._toggle_grayscale)
        self.image_viewer.set_context_menu(context_menu)

    def _create_grid_panel(self):
        """Create grid configuration panel dock."""
        self.grid_panel = GridConfigPanel(self.grid_config)
        self.grid_panel.config_changed.connect(self._on_grid_config_changed)

        dock = QDockWidget("Grid Configuration", self)
        dock.setWidget(self.grid_panel)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(False)  # Hidden by default

        self.grid_dock = dock

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

    def _toggle_grayscale(self):
        """Toggle black/white (grayscale) filter."""
        self.image_viewer.toggle_grayscale()

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
        logger.debug(f"Grid subdivisions decreased: {self.grid_config.subdivision_count}")

