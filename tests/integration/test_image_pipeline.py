"""Integration tests for image loading pipeline."""

import pytest
from pathlib import Path
from PIL import Image as PILImage
import tempfile
import os

from portrait_helper.image.loader import load_from_file, Image
from PySide6.QtGui import QImage


class TestImageLoadingPipeline:
    """Integration tests for image loading pipeline."""

    def test_file_load_to_image_entity_to_display_ready(self):
        """Test complete pipeline: file load → Image entity → display ready."""
        # Create a test image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            test_image = PILImage.new("RGB", (800, 600), color="blue")
            test_image.save(tmp.name, "PNG")

            try:
                # Load image
                image = load_from_file(tmp.name)

                # Verify Image entity is ready for display
                assert image.is_loaded is True
                assert image.is_valid() is True
                assert image.width == 800
                assert image.height == 600
                assert image.aspect_ratio == pytest.approx(800 / 600, rel=1e-6)

                # Verify pixel data is accessible
                pixel_data = image.get_pixel_data()
                assert pixel_data is not None
                assert pixel_data.width == 800
                assert pixel_data.height == 600

                # Verify metadata is complete
                metadata = image.get_metadata()
                assert metadata["is_loaded"] is True
                assert metadata["width"] == 800
                assert metadata["height"] == 600

            finally:
                os.unlink(tmp.name)

    def test_window_resize_with_aspect_ratio_preserved(self):
        """Test window resize maintains aspect ratio."""
        from portrait_helper.image.viewport import Viewport

        # Create a test image
        test_image = PILImage.new("RGB", (1920, 1080), color="red")
        image = Image(
            width=1920,
            height=1080,
            format="JPEG",
            source="/test/image.jpg",
            pixel_data=test_image,
            source_path="/test/image.jpg",
        )

        # Create viewport with initial window size
        viewport = Viewport(
            image_width=image.width,
            image_height=image.height,
            window_width=800,
            window_height=600,
        )

        # Get initial display size
        initial_width, initial_height = viewport.get_display_size()
        initial_aspect = initial_width / initial_height if initial_height > 0 else 1.0

        # Resize window
        viewport.resize_window(1200, 800)

        # Get new display size
        new_width, new_height = viewport.get_display_size()
        new_aspect = new_width / new_height if new_height > 0 else 1.0

        # Aspect ratio should be preserved (image aspect ratio, not window)
        # The viewport should maintain the image's aspect ratio
        image_aspect = image.aspect_ratio
        display_aspect_initial = initial_width / initial_height if initial_height > 0 else 1.0
        display_aspect_new = new_width / new_height if new_height > 0 else 1.0

        # Both display aspects should match image aspect (within rounding)
        assert abs(display_aspect_initial - image_aspect) < 0.01
        assert abs(display_aspect_new - image_aspect) < 0.01


class TestWebPDisplayCorrectness:
    """Integration tests for WebP image display correctness (bug fix)."""

    def create_test_webp(self, width: int = 200, height: int = 200) -> str:
        """Create a test WebP image with known pattern.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Path to temporary WebP file
        """
        # Create a simple test pattern: vertical stripes
        img = PILImage.new("RGB", (width, height), color="white")
        pixels = img.load()
        
        # Create vertical stripes: every 20 pixels alternate black/white
        for y in range(height):
            for x in range(width):
                stripe = x // 20
                if stripe % 2 == 0:
                    pixels[x, y] = (0, 0, 0)  # Black
                else:
                    pixels[x, y] = (255, 255, 255)  # White
        
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
            img.save(tmp.name, "WebP")
            return tmp.name

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_display_correctness_from_file(self):
        """Test T032: WebP display correctness from file.
        
        Load WebP from file, convert to QImage, and verify no skew.
        """
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage
        
        # Initialize QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        webp_path = self.create_test_webp(200, 200)
        try:
            # Load WebP image
            image = load_from_file(webp_path)
            assert image.format == "WebP"
            assert image.is_loaded is True
            
            # Convert to QImage using ImageViewer
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            pil_image = image.get_pixel_data()
            qimage = viewer._pil_to_qimage(pil_image)
            
            # Verify dimensions
            assert qimage.width() == 200
            assert qimage.height() == 200
            
            # Check vertical stripes - if skewed, stripes will be diagonal
            # Column 0 should be black (first stripe)
            pixel_0_0 = qimage.pixel(0, 0)
            pixel_0_100 = qimage.pixel(0, 100)
            pixel_0_199 = qimage.pixel(0, 199)
            
            # All pixels in column 0 should be black (or very close)
            for pixel in [pixel_0_0, pixel_0_100, pixel_0_199]:
                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF
                assert r < 10 and g < 10 and b < 10, f"Column 0 should be black, got ({r},{g},{b})"
            
            # Column 20 should be white (second stripe)
            pixel_20_0 = qimage.pixel(20, 0)
            pixel_20_100 = qimage.pixel(20, 100)
            pixel_20_199 = qimage.pixel(20, 199)
            
            # All pixels in column 20 should be white (or very close)
            for pixel in [pixel_20_0, pixel_20_100, pixel_20_199]:
                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF
                assert r > 245 and g > 245 and b > 245, f"Column 20 should be white, got ({r},{g},{b})"
            
        finally:
            os.unlink(webp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_display_correctness_from_url(self):
        """Test T033: WebP display correctness from URL.
        
        This test simulates loading WebP from URL by creating a file
        and loading it (actual URL loading would require network).
        """
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage
        
        # Initialize QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        webp_path = self.create_test_webp(150, 150)
        try:
            # Simulate URL loading by loading from file
            # In real scenario, this would be load_from_url()
            image = load_from_file(webp_path)
            assert image.format == "WebP"
            assert image.is_loaded is True
            
            # Convert to QImage
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            pil_image = image.get_pixel_data()
            qimage = viewer._pil_to_qimage(pil_image)
            
            # Verify no skew by checking that vertical lines are vertical
            # Check multiple columns at different rows
            test_columns = [0, 20, 40, 60, 80, 100, 120, 140]
            for col in test_columns:
                if col < 150:
                    # Get pixel at top and bottom of column
                    pixel_top = qimage.pixel(col, 0)
                    pixel_bottom = qimage.pixel(col, 149)
                    
                    # Extract RGB
                    r_top = (pixel_top >> 16) & 0xFF
                    r_bottom = (pixel_bottom >> 16) & 0xFF
                    
                    # Top and bottom should have similar color (same stripe)
                    # Allow some tolerance for compression
                    assert abs(r_top - r_bottom) < 20, f"Column {col} shows skew: top={r_top}, bottom={r_bottom}"
            
        finally:
            os.unlink(webp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_various_sizes(self):
        """Test T039: Verify fix with various WebP image sizes."""
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        sizes = [(50, 50), (100, 100), (500, 500), (1000, 1000)]
        
        for width, height in sizes:
            webp_path = self.create_test_webp(width, height)
            try:
                image = load_from_file(webp_path)
                from portrait_helper.gui.image_viewer import ImageViewer
                viewer = ImageViewer()
                pil_image = image.get_pixel_data()
                qimage = viewer._pil_to_qimage(pil_image)
                
                # Verify dimensions match
                assert qimage.width() == width
                assert qimage.height() == height
                
                # Verify format
                assert qimage.format() in (QImage.Format.Format_RGB888, QImage.Format.Format_RGBA8888)
                
            finally:
                os.unlink(webp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_different_modes(self):
        """Test T040: Verify fix with WebP images in different modes."""
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test RGB mode
        rgb_img = PILImage.new("RGB", (100, 100), color="red")
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
            rgb_img.save(tmp.name, "WebP")
            rgb_path = tmp.name
        
        try:
            image = load_from_file(rgb_path)
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            pil_image = image.get_pixel_data()
            qimage = viewer._pil_to_qimage(pil_image)
            
            assert qimage.width() == 100
            assert qimage.height() == 100
            assert qimage.format() == QImage.Format.Format_RGB888
            
        finally:
            os.unlink(rgb_path)
        
        # Test RGBA mode if supported
        rgba_img = PILImage.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
            try:
                rgba_img.save(tmp.name, "WebP")
                rgba_path = tmp.name
                
                image = load_from_file(rgba_path)
                viewer = ImageViewer()
                pil_image = image.get_pixel_data()
                # PIL may convert RGBA to RGB during load
                qimage = viewer._pil_to_qimage(pil_image)
                
                assert qimage.width() == 100
                assert qimage.height() == 100
                
            finally:
                if os.path.exists(rgba_path):
                    os.unlink(rgba_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_conversion_performance(self):
        """Test T041: Performance test for WebP conversion."""
        import time
        
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create a medium-sized WebP image
        webp_path = self.create_test_webp(800, 600)
        try:
            image = load_from_file(webp_path)
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            pil_image = image.get_pixel_data()
            
            # Time the conversion
            start_time = time.time()
            qimage = viewer._pil_to_qimage(pil_image)
            conversion_time = time.time() - start_time
            
            # Conversion should be fast (< 100ms for 800x600 image)
            assert conversion_time < 0.1, f"WebP conversion too slow: {conversion_time:.3f}s"
            
            # Verify result is correct
            assert qimage.width() == 800
            assert qimage.height() == 600
            
        finally:
            os.unlink(webp_path)


class TestFilterToggle:
    """Integration tests for filter toggle functionality."""

    def test_filter_toggle_applies_and_removes_filter(self):
        """Test T075: Filter applies, toggles off, viewport state preserved."""
        from PySide6.QtWidgets import QApplication
        from portrait_helper.image.filter import FilterState
        from portrait_helper.image.viewport import Viewport
        
        # Initialize QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create a color test image
        test_image = PILImage.new("RGB", (400, 300), color="red")
        
        # Create filter state
        filter_state = FilterState(original_pixel_data=test_image)
        
        # Verify initial state
        assert filter_state.grayscale_enabled is False
        assert filter_state.get_current_image() is test_image
        assert filter_state.get_current_image().mode == "RGB"
        
        # Apply filter
        filter_state.toggle_grayscale()
        assert filter_state.grayscale_enabled is True
        filtered_image = filter_state.get_current_image()
        assert filtered_image is not None
        assert filtered_image.mode == "L"  # Grayscale
        
        # Toggle off
        filter_state.toggle_grayscale()
        assert filter_state.grayscale_enabled is False
        restored_image = filter_state.get_current_image()
        assert restored_image is test_image
        assert restored_image.mode == "RGB"
        
        # Verify original is preserved
        assert filter_state.original_pixel_data is test_image

    def test_viewport_state_preserved_on_filter_toggle(self):
        """Test that viewport state (zoom/pan) is preserved when filter is toggled."""
        from PySide6.QtWidgets import QApplication
        from portrait_helper.image.filter import FilterState
        from portrait_helper.image.viewport import Viewport
        
        # Initialize QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create test image
        test_image = PILImage.new("RGB", (800, 600), color="blue")
        filter_state = FilterState(original_pixel_data=test_image)
        
        # Create viewport with zoom and pan
        viewport = Viewport(
            image_width=800,
            image_height=600,
            window_width=400,
            window_height=300,
        )
        
        # Set zoom and pan
        viewport.set_zoom(2.0)
        viewport.pan(50, 30)
        
        # Capture viewport state
        zoom_before = viewport.zoom_level
        pan_x_before = viewport.pan_offset_x
        pan_y_before = viewport.pan_offset_y
        
        # Toggle filter
        filter_state.toggle_grayscale()
        
        # Viewport state should be unchanged
        assert viewport.zoom_level == zoom_before
        assert viewport.pan_offset_x == pan_x_before
        assert viewport.pan_offset_y == pan_y_before
        
        # Toggle filter off
        filter_state.toggle_grayscale()
        
        # Viewport state should still be unchanged
        assert viewport.zoom_level == zoom_before
        assert viewport.pan_offset_x == pan_x_before
        assert viewport.pan_offset_y == pan_y_before

