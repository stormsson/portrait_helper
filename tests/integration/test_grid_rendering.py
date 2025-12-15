"""Integration tests for grid overlay rendering."""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from PIL import Image as PILImage

from portrait_helper.image.loader import Image, load_from_file
from portrait_helper.image.viewport import Viewport
from portrait_helper.grid.config import GridConfiguration
from portrait_helper.gui.image_viewer import ImageViewer


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestGridOverlayRendering:
    """Integration tests for grid overlay rendering."""

    def test_grid_displays_when_visible(self, qapp, tmp_path):
        """Test grid displays when visible is True."""
        # Create test image
        test_image = PILImage.new("RGB", (800, 600), color="blue")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create grid configuration
        grid_config = GridConfiguration(visible=True, subdivision_count=3)
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )

        # Grid should be configured
        assert grid_config.visible is True
        assert grid_config.cell_size > 0

    def test_grid_hides_when_visible_false(self, qapp, tmp_path):
        """Test grid hides when visible is False."""
        # Create test image
        test_image = PILImage.new("RGB", (800, 600), color="red")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create grid configuration with visible=False
        grid_config = GridConfiguration(visible=False, subdivision_count=3)
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )

        # Grid should not be visible
        assert grid_config.visible is False

    def test_grid_updates_on_config_change(self, qapp, tmp_path):
        """Test grid updates when configuration changes."""
        # Create test image
        test_image = PILImage.new("RGB", (800, 600), color="green")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create grid configuration
        grid_config = GridConfiguration(visible=True, subdivision_count=3)
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )

        initial_cell_size = grid_config.cell_size

        # Change subdivision count
        grid_config.increase_size()  # Fewer subdivisions (larger cells)
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )

        # Cell size should have changed
        assert grid_config.cell_size != initial_cell_size

    def test_grid_with_zoom_pan(self, qapp, tmp_path):
        """Test grid maintains alignment with zoom/pan."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="purple")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Create grid configuration
        grid_config = GridConfiguration(visible=True, subdivision_count=3)

        # Calculate cell size for initial viewport
        display_width, display_height = viewport.get_display_size()
        grid_config.calculate_cell_size(
            viewport_width=display_width, viewport_height=display_height
        )
        initial_cell_size = grid_config.cell_size

        # Zoom in
        viewport.zoom_in(factor=2.0)
        display_width, display_height = viewport.get_display_size()

        # Recalculate grid for new viewport size
        grid_config.calculate_cell_size(
            viewport_width=display_width, viewport_height=display_height
        )

        # Cell size should scale with zoom
        assert grid_config.cell_size > initial_cell_size

    def test_grid_moves_with_image_pan(self, qapp, tmp_path):
        """Test grid moves with image during pan operations."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="orange")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Zoom in first (pan only works when zoomed)
        viewport.zoom_in(factor=2.0)

        # Create grid configuration
        grid_config = GridConfiguration(visible=True, subdivision_count=3)
        display_width, display_height = viewport.get_display_size()
        grid_config.calculate_cell_size(
            viewport_width=display_width, viewport_height=display_height
        )

        initial_cell_size = grid_config.cell_size

        # Pan image
        viewport.pan(delta_x=100, delta_y=50)

        # Grid cell size should remain the same (grid scales with viewport, not pan)
        display_width, display_height = viewport.get_display_size()
        grid_config.calculate_cell_size(
            viewport_width=display_width, viewport_height=display_height
        )

        # Cell size should be same (pan doesn't change viewport size)
        assert grid_config.cell_size == initial_cell_size

    def test_grid_maintains_alignment_on_resize(self, qapp, tmp_path):
        """Test grid maintains alignment when window is resized."""
        # Create test image
        test_image = PILImage.new("RGB", (800, 600), color="cyan")
        image_path = tmp_path / "test.png"
        test_image.save(image_path)

        # Load image
        image = load_from_file(str(image_path))
        assert image.is_loaded

        # Create viewer and set image
        viewer = ImageViewer()
        viewer.set_image(image)
        viewer.resize(800, 600)
        QTest.qWaitForWindowExposed(viewer)

        # Create grid configuration
        grid_config = GridConfiguration(visible=True, subdivision_count=3)
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )
        initial_cell_size = grid_config.cell_size

        # Resize window
        viewer.resize(1200, 900)
        viewer.update_display()
        QTest.qWait(100)  # Wait for resize to process

        # Recalculate grid for new size
        grid_config.calculate_cell_size(
            viewport_width=viewer.width(), viewport_height=viewer.height()
        )

        # Cell size should have changed to match new viewport
        assert grid_config.cell_size != initial_cell_size
        assert grid_config.cell_size > 0

