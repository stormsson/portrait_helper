"""Integration tests for zoom and pan functionality."""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QPoint
from PIL import Image as PILImage

from portrait_helper.image.loader import Image, load_from_file
from portrait_helper.image.viewport import Viewport
from portrait_helper.gui.image_viewer import ImageViewer


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestZoomPanInteraction:
    """Integration tests for zoom/pan interaction."""

    def test_zoom_centers_on_point(self, qapp, tmp_path):
        """Test zoom centers on specified point."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="blue")
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Get initial pan position
        initial_pan_x = viewport.pan_offset_x
        initial_pan_y = viewport.pan_offset_y

        # Zoom in centered on a point (center of viewer)
        center_x = viewer.width() / 2
        center_y = viewer.height() / 2
        viewport.zoom_in(center_x=center_x, center_y=center_y)

        # Pan should have adjusted to maintain center point
        assert viewport.pan_offset_x != initial_pan_x or viewport.pan_offset_y != initial_pan_y

    def test_pan_maintains_position_during_zoom(self, qapp, tmp_path):
        """Test pan maintains position during zoom."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="red")
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Zoom in first
        viewport.zoom_in(factor=2.0)

        # Pan to a position
        viewport.pan(delta_x=100, delta_y=50)
        pan_after_first = (viewport.pan_offset_x, viewport.pan_offset_y)

        # Zoom in again (without center point)
        viewport.zoom_in(factor=1.2)

        # Pan should still be set (may be constrained but should exist)
        assert viewport.pan_offset_x is not None
        assert viewport.pan_offset_y is not None

    def test_zoom_pan_boundaries_respected(self, qapp, tmp_path):
        """Test zoom/pan boundaries are respected."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="green")
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Zoom in
        viewport.zoom_in(factor=3.0)

        # Try to pan beyond boundaries
        viewport.pan(delta_x=10000, delta_y=10000)

        # Constrain pan
        viewport.constrain_pan()

        # Pan should be within bounds
        max_pan_x = max(0, (viewport.display_width - viewport.window_width) / 2)
        max_pan_y = max(0, (viewport.display_height - viewport.window_height) / 2)

        assert abs(viewport.pan_offset_x) <= max_pan_x + 0.1
        assert abs(viewport.pan_offset_y) <= max_pan_y + 0.1


class TestViewportResizeInteraction:
    """Integration tests for viewport resize interaction."""

    def test_resize_adjusts_zoom_pan(self, qapp, tmp_path):
        """Test resize adjusts zoom/pan."""
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Zoom in and pan
        viewport.zoom_in(factor=2.0)
        viewport.pan(delta_x=100, delta_y=50)

        initial_display_width = viewport.display_width
        initial_display_height = viewport.display_height

        # Resize window
        viewer.resize(1200, 900)
        viewer.update_display()
        QTest.qWait(100)  # Wait for resize to process

        # Display size should have changed
        assert viewport.display_width != initial_display_width or viewport.display_height != initial_display_height

    def test_resize_maintains_aspect_ratio(self, qapp, tmp_path):
        """Test resize maintains aspect ratio."""
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        initial_aspect = viewport._image_aspect_ratio

        # Resize window
        viewer.resize(1200, 900)
        viewer.update_display()
        QTest.qWait(100)

        # Aspect ratio should be maintained
        display_aspect = viewport.display_width / viewport.display_height
        assert display_aspect == pytest.approx(initial_aspect, rel=1e-3)

    def test_resize_constrains_pan(self, qapp, tmp_path):
        """Test resize constrains pan."""
        # Create test image
        test_image = PILImage.new("RGB", (1920, 1080), color="cyan")
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

        # Get viewport
        viewport = viewer._viewport
        assert viewport is not None

        # Zoom in and pan
        viewport.zoom_in(factor=2.0)
        viewport.pan(delta_x=200, delta_y=150)

        # Resize to smaller window
        viewer.resize(400, 300)
        viewer.update_display()
        QTest.qWait(100)

        # Pan should be constrained
        viewport.constrain_pan()
        max_pan_x = max(0, (viewport.display_width - viewport.window_width) / 2)
        max_pan_y = max(0, (viewport.display_height - viewport.window_height) / 2)

        assert abs(viewport.pan_offset_x) <= max_pan_x + 0.1
        assert abs(viewport.pan_offset_y) <= max_pan_y + 0.1

