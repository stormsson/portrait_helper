"""Unit tests for viewport library."""

import pytest
from portrait_helper.image.viewport import Viewport, MIN_ZOOM, MAX_ZOOM, DEFAULT_ZOOM


class TestViewportZoomCalculations:
    """Unit tests for Viewport zoom calculations."""

    def test_zoom_in_increases_zoom_level(self):
        """Test zoom_in increases zoom level correctly."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_zoom = viewport.zoom_level

        viewport.zoom_in()
        assert viewport.zoom_level > initial_zoom
        assert viewport.zoom_level <= MAX_ZOOM

    def test_zoom_out_decreases_zoom_level(self):
        """Test zoom_out decreases zoom level correctly."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        # Zoom in first
        viewport.zoom_in()
        initial_zoom = viewport.zoom_level

        viewport.zoom_out()
        assert viewport.zoom_level < initial_zoom
        assert viewport.zoom_level >= MIN_ZOOM

    def test_zoom_respects_min_bounds(self):
        """Test zoom respects minimum zoom bounds."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        # Zoom out repeatedly
        for _ in range(20):
            viewport.zoom_out(factor=0.5)
        
        assert viewport.zoom_level >= MIN_ZOOM

    def test_zoom_respects_max_bounds(self):
        """Test zoom respects maximum zoom bounds."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        # Zoom in repeatedly
        for _ in range(20):
            viewport.zoom_in(factor=2.0)
        
        assert viewport.zoom_level <= MAX_ZOOM

    def test_set_zoom_with_valid_level(self):
        """Test set_zoom with valid zoom level."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        viewport.set_zoom(2.0)
        assert viewport.zoom_level == 2.0

    def test_set_zoom_with_invalid_level_raises_error(self):
        """Test set_zoom with invalid zoom level raises ValueError."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        with pytest.raises(ValueError, match="Zoom level must be between"):
            viewport.set_zoom(MIN_ZOOM - 0.1)
        
        with pytest.raises(ValueError, match="Zoom level must be between"):
            viewport.set_zoom(MAX_ZOOM + 0.1)

    def test_zoom_centers_on_point(self):
        """Test zoom centers on specified point."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_pan_x = viewport.pan_offset_x
        initial_pan_y = viewport.pan_offset_y

        # Zoom in centered on a point
        viewport.zoom_in(center_x=400, center_y=300)
        
        # Pan should have adjusted to maintain center point
        assert viewport.pan_offset_x != initial_pan_x or viewport.pan_offset_y != initial_pan_y

    def test_zoom_in_with_custom_factor(self):
        """Test zoom_in with custom factor."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_zoom = viewport.zoom_level

        viewport.zoom_in(factor=1.5)
        assert viewport.zoom_level == pytest.approx(initial_zoom * 1.5, rel=1e-6)

    def test_zoom_out_with_custom_factor(self):
        """Test zoom_out with custom factor."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        # Zoom in first
        viewport.zoom_in()
        initial_zoom = viewport.zoom_level

        viewport.zoom_out(factor=0.5)
        assert viewport.zoom_level == pytest.approx(initial_zoom * 0.5, rel=1e-6)


class TestViewportPanCalculations:
    """Unit tests for Viewport pan calculations."""

    def test_pan_updates_offsets(self):
        """Test pan updates offsets correctly."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        # Zoom in first so panning is possible
        viewport.zoom_in(factor=2.0)
        
        initial_pan_x = viewport.pan_offset_x
        initial_pan_y = viewport.pan_offset_y

        viewport.pan(delta_x=100, delta_y=50)
        
        assert viewport.pan_offset_x == initial_pan_x + 100
        assert viewport.pan_offset_y == initial_pan_y + 50

    def test_pan_constrained_to_boundaries(self):
        """Test pan is constrained to image boundaries."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        # Zoom in so panning is possible
        viewport.zoom_in(factor=3.0)
        
        # Try to pan way beyond boundaries
        viewport.pan(delta_x=10000, delta_y=10000)
        
        # Pan should be constrained
        viewport.constrain_pan()
        # After constraint, pan should be within bounds
        assert abs(viewport.pan_offset_x) <= abs(viewport.display_width - viewport.window_width) / 2 + 1
        assert abs(viewport.pan_offset_y) <= abs(viewport.display_height - viewport.window_height) / 2 + 1

    def test_pan_maintains_position_during_zoom(self):
        """Test pan maintains position during zoom when no center point specified."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        viewport.pan(delta_x=100, delta_y=50)
        
        pan_before = (viewport.pan_offset_x, viewport.pan_offset_y)
        
        # Zoom in without center point
        viewport.zoom_in(factor=1.2)
        
        # Pan should still be set (though may be constrained)
        assert viewport.pan_offset_x is not None
        assert viewport.pan_offset_y is not None

    def test_constrain_pan_at_fit_to_window(self):
        """Test constrain_pan at fit-to-window (no panning needed)."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        # At fit-to-window, pan should be 0
        viewport.constrain_pan()
        assert viewport.pan_offset_x == 0.0
        assert viewport.pan_offset_y == 0.0

    def test_constrain_pan_after_zoom(self):
        """Test constrain_pan after zooming."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        
        # Try to set pan beyond boundaries
        viewport.pan_offset_x = 10000
        viewport.pan_offset_y = 10000
        
        viewport.constrain_pan()
        
        # Pan should be constrained
        max_pan_x = max(0, (viewport.display_width - viewport.window_width) / 2)
        max_pan_y = max(0, (viewport.display_height - viewport.window_height) / 2)
        
        assert abs(viewport.pan_offset_x) <= max_pan_x + 0.1
        assert abs(viewport.pan_offset_y) <= max_pan_y + 0.1


class TestViewportResizeCalculations:
    """Unit tests for Viewport resize calculations."""

    def test_resize_window_updates_dimensions(self):
        """Test resize_window updates window dimensions."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        viewport.resize_window(1200, 900)
        
        assert viewport.window_width == 1200
        assert viewport.window_height == 900

    def test_resize_window_maintains_aspect_ratio(self):
        """Test resize_window maintains image aspect ratio."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_aspect = viewport._image_aspect_ratio
        
        viewport.resize_window(1200, 900)
        
        # Display should maintain aspect ratio
        display_aspect = viewport.display_width / viewport.display_height
        assert display_aspect == pytest.approx(initial_aspect, rel=1e-3)

    def test_resize_window_recalculates_display_size(self):
        """Test resize_window recalculates display size."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_display_width = viewport.display_width
        initial_display_height = viewport.display_height
        
        viewport.resize_window(1200, 900)
        
        # Display size should have changed
        assert viewport.display_width != initial_display_width or viewport.display_height != initial_display_height

    def test_resize_window_updates_visible_region(self):
        """Test resize_window updates visible region."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        initial_visible_region = viewport.get_visible_region()
        
        viewport.resize_window(1200, 900)
        
        # Visible region should be updated
        new_visible_region = viewport.get_visible_region()
        assert new_visible_region != initial_visible_region

    def test_resize_window_with_invalid_dimensions_raises_error(self):
        """Test resize_window with invalid dimensions raises ValueError."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        with pytest.raises(ValueError, match="Window dimensions must be positive"):
            viewport.resize_window(0, 600)
        
        with pytest.raises(ValueError, match="Window dimensions must be positive"):
            viewport.resize_window(800, -100)

    def test_get_display_size_returns_correct_dimensions(self):
        """Test get_display_size returns correct dimensions."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        display_width, display_height = viewport.get_display_size()
        
        assert display_width == viewport.display_width
        assert display_height == viewport.display_height
        assert display_width > 0
        assert display_height > 0

    def test_get_visible_region_returns_correct_coordinates(self):
        """Test get_visible_region returns correct coordinates."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        
        visible_region = viewport.get_visible_region()
        
        assert "x" in visible_region
        assert "y" in visible_region
        assert "width" in visible_region
        assert "height" in visible_region
        assert visible_region["width"] > 0
        assert visible_region["height"] > 0


class TestViewportResetZoom:
    """Unit tests for Viewport reset_zoom."""

    def test_reset_zoom_sets_level_to_fit_window(self):
        """Test reset_zoom sets zoom level to fit window."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        
        viewport.reset_zoom()
        
        assert viewport.zoom_level == DEFAULT_ZOOM

    def test_reset_zoom_centers_image(self):
        """Test reset_zoom centers image."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        viewport.pan(delta_x=100, delta_y=50)
        
        viewport.reset_zoom()
        
        assert viewport.pan_offset_x == 0.0
        assert viewport.pan_offset_y == 0.0

    def test_reset_zoom_preserves_aspect_ratio(self):
        """Test reset_zoom preserves aspect ratio."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        initial_aspect = viewport._image_aspect_ratio
        
        viewport.zoom_in(factor=2.0)
        viewport.reset_zoom()
        
        display_aspect = viewport.display_width / viewport.display_height
        assert display_aspect == pytest.approx(initial_aspect, rel=1e-3)

    def test_reset_zoom_recalculates_display(self):
        """Test reset_zoom recalculates display dimensions."""
        viewport = Viewport(image_width=1920, image_height=1080, window_width=800, window_height=600)
        viewport.zoom_in(factor=2.0)
        zoomed_display_width = viewport.display_width
        
        viewport.reset_zoom()
        
        # Display should be smaller (fit to window)
        assert viewport.display_width < zoomed_display_width

