"""Unit tests for image viewer widget."""

import pytest
from pathlib import Path
from PIL import Image as PILImage
import tempfile
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage

from portrait_helper.gui.image_viewer import ImageViewer
from portrait_helper.image.loader import Image, load_from_file


# Initialize QApplication for Qt tests (required for QImage)
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestPILToQImageConversion:
    """Unit tests for PIL to QImage conversion."""

    def create_checkerboard_webp(self, size: int = 100) -> str:
        """Create a WebP image with checkerboard pattern for testing pixel alignment.
        
        Args:
            size: Image size (width and height)
            
        Returns:
            Path to temporary WebP file
        """
        # Create checkerboard pattern: alternating black and white squares
        img = PILImage.new("RGB", (size, size), color="white")
        pixels = img.load()
        
        # Create 10x10 checkerboard pattern
        square_size = size // 10
        for y in range(size):
            for x in range(size):
                square_x = x // square_size
                square_y = y // square_size
                if (square_x + square_y) % 2 == 0:
                    pixels[x, y] = (0, 0, 0)  # Black
                else:
                    pixels[x, y] = (255, 255, 255)  # White
        
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp:
            img.save(tmp.name, "WebP")
            return tmp.name

    def create_checkerboard_png(self, size: int = 100) -> str:
        """Create a PNG image with checkerboard pattern for comparison.
        
        Args:
            size: Image size (width and height)
            
        Returns:
            Path to temporary PNG file
        """
        # Create checkerboard pattern: alternating black and white squares
        img = PILImage.new("RGB", (size, size), color="white")
        pixels = img.load()
        
        # Create 10x10 checkerboard pattern
        square_size = size // 10
        for y in range(size):
            for x in range(size):
                square_x = x // square_size
                square_y = y // square_size
                if (square_x + square_y) % 2 == 0:
                    pixels[x, y] = (0, 0, 0)  # Black
                else:
                    pixels[x, y] = (255, 255, 255)  # White
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name, "PNG")
            return tmp.name

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_webp_pixel_alignment(self, qapp):
        """Test T030: WebP pixel alignment after conversion to QImage.
        
        This test creates a WebP image with a known checkerboard pattern
        and verifies that pixel positions are correct after conversion to QImage.
        If pixels are skewed, the checkerboard pattern will be distorted.
        """
        webp_path = self.create_checkerboard_webp(100)
        try:
            # Load WebP image
            image = load_from_file(webp_path)
            pil_image = image.get_pixel_data()
            
            # Convert to QImage using the same method as ImageViewer
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            qimage = viewer._pil_to_qimage(pil_image)
            
            # Verify QImage dimensions
            assert qimage.width() == 100
            assert qimage.height() == 100
            
            # Check specific pixel positions that should be black or white
            # Top-left corner (0,0) should be black (first square)
            pixel_00 = qimage.pixel(0, 0)
            r_00 = (pixel_00 >> 16) & 0xFF
            g_00 = (pixel_00 >> 8) & 0xFF
            b_00 = pixel_00 & 0xFF
            # Should be black (0,0,0) or very close
            assert r_00 < 10 and g_00 < 10 and b_00 < 10, f"Pixel (0,0) should be black, got ({r_00},{g_00},{b_00})"
            
            # Pixel (10,0) should be white (second square in first row)
            pixel_10_0 = qimage.pixel(10, 0)
            r_10_0 = (pixel_10_0 >> 16) & 0xFF
            g_10_0 = (pixel_10_0 >> 8) & 0xFF
            b_10_0 = pixel_10_0 & 0xFF
            # Should be white (255,255,255) or very close
            assert r_10_0 > 245 and g_10_0 > 245 and b_10_0 > 245, f"Pixel (10,0) should be white, got ({r_10_0},{g_10_0},{b_10_0})"
            
            # Check a pixel in the second row - if skewed, this will be wrong
            # Pixel (0,10) should be white (first square in second row)
            pixel_0_10 = qimage.pixel(0, 10)
            r_0_10 = (pixel_0_10 >> 16) & 0xFF
            g_0_10 = (pixel_0_10 >> 8) & 0xFF
            b_0_10 = pixel_0_10 & 0xFF
            # Should be white (255,255,255) or very close
            assert r_0_10 > 245 and g_0_10 > 245 and b_0_10 > 245, f"Pixel (0,10) should be white, got ({r_0_10},{g_0_10},{b_0_10})"
            
            # Check a pixel further down - if there's progressive skew, this will be very wrong
            # Pixel (0,50) should be black (first square in 6th row)
            pixel_0_50 = qimage.pixel(0, 50)
            r_0_50 = (pixel_0_50 >> 16) & 0xFF
            g_0_50 = (pixel_0_50 >> 8) & 0xFF
            b_0_50 = pixel_0_50 & 0xFF
            # Should be black (0,0,0) or very close
            assert r_0_50 < 10 and g_0_50 < 10 and b_0_50 < 10, f"Pixel (0,50) should be black, got ({r_0_50},{g_0_50},{b_0_50})"
            
        finally:
            os.unlink(webp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_pil_to_qimage_conversion_webp(self, qapp):
        """Test T031: _pil_to_qimage conversion for WebP format.
        
        This test verifies stride/alignment for WebP images and compares
        with other formats to ensure WebP is handled correctly.
        """
        # Create WebP image
        webp_path = self.create_checkerboard_webp(100)
        png_path = self.create_checkerboard_png(100)
        
        try:
            # Load both images
            webp_image = load_from_file(webp_path)
            png_image = load_from_file(png_path)
            
            webp_pil = webp_image.get_pixel_data()
            png_pil = png_image.get_pixel_data()
            
            # Verify PIL image properties
            assert webp_pil.mode == "RGB" or webp_pil.mode == "RGBA"
            assert png_pil.mode == "RGB"
            assert webp_pil.size == (100, 100)
            assert png_pil.size == (100, 100)
            
            # Convert both to QImage
            from portrait_helper.gui.image_viewer import ImageViewer
            viewer = ImageViewer()
            webp_qimage = viewer._pil_to_qimage(webp_pil)
            png_qimage = viewer._pil_to_qimage(png_pil)
            
            # Verify QImage properties
            assert webp_qimage.width() == 100
            assert webp_qimage.height() == 100
            assert png_qimage.width() == 100
            assert png_qimage.height() == 100
            
            # Verify format
            assert webp_qimage.format() in (QImage.Format.Format_RGB888, QImage.Format.Format_RGBA8888)
            assert png_qimage.format() == QImage.Format.Format_RGB888
            
            # Compare pixel values at same positions - they should match
            # Sample a few pixels
            test_positions = [(0, 0), (10, 10), (50, 50), (99, 99)]
            for x, y in test_positions:
                webp_pixel = webp_qimage.pixel(x, y)
                png_pixel = png_qimage.pixel(x, y)
                
                # Extract RGB values
                webp_r = (webp_pixel >> 16) & 0xFF
                webp_g = (webp_pixel >> 8) & 0xFF
                webp_b = webp_pixel & 0xFF
                
                png_r = (png_pixel >> 16) & 0xFF
                png_g = (png_pixel >> 8) & 0xFF
                png_b = png_pixel & 0xFF
                
                # Pixels should match (within small tolerance for compression)
                assert abs(webp_r - png_r) < 5, f"Pixel ({x},{y}) R mismatch: WebP={webp_r}, PNG={png_r}"
                assert abs(webp_g - png_g) < 5, f"Pixel ({x},{y}) G mismatch: WebP={webp_g}, PNG={png_g}"
                assert abs(webp_b - png_b) < 5, f"Pixel ({x},{y}) B mismatch: WebP={webp_b}, PNG={png_b}"
            
        finally:
            os.unlink(webp_path)
            os.unlink(png_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_investigate_pil_image_properties_webp(self, qapp):
        """Test T035: Investigate PIL image properties for WebP vs other formats.
        
        This test compares mode, size, and stride for WebP vs other formats
        to identify any differences that might cause the skew issue.
        """
        # Create test images in different formats
        webp_path = self.create_checkerboard_webp(100)
        png_path = self.create_checkerboard_png(100)
        
        try:
            # Load images
            webp_image = load_from_file(webp_path)
            png_image = load_from_file(png_path)
            
            webp_pil = webp_image.get_pixel_data()
            png_pil = png_image.get_pixel_data()
            
            # Log properties for investigation
            print(f"\nWebP PIL properties:")
            print(f"  Mode: {webp_pil.mode}")
            print(f"  Size: {webp_pil.size}")
            print(f"  Format: {webp_pil.format}")
            
            print(f"\nPNG PIL properties:")
            print(f"  Mode: {png_pil.mode}")
            print(f"  Size: {png_pil.size}")
            print(f"  Format: {png_pil.format}")
            
            # Check tobytes output
            webp_bytes = webp_pil.tobytes("raw", "RGB")
            png_bytes = png_pil.tobytes("raw", "RGB")
            
            print(f"\nWebP bytes length: {len(webp_bytes)}")
            print(f"PNG bytes length: {len(png_bytes)}")
            print(f"Expected bytes (100*100*3): {100 * 100 * 3}")
            
            # Verify bytes length matches expected (width * height * 3 for RGB)
            assert len(webp_bytes) == 100 * 100 * 3, f"WebP bytes length mismatch: expected {100*100*3}, got {len(webp_bytes)}"
            assert len(png_bytes) == 100 * 100 * 3, f"PNG bytes length mismatch: expected {100*100*3}, got {len(png_bytes)}"
            
            # Check if first few bytes match (should be similar for same pattern)
            # Note: WebP is lossy, so exact match not expected, but should be close
            print(f"\nFirst 30 bytes comparison:")
            print(f"  WebP: {webp_bytes[:30]}")
            print(f"  PNG:  {png_bytes[:30]}")
            
        finally:
            os.unlink(webp_path)
            os.unlink(png_path)

