"""Contract tests for image format support."""

import pytest
from pathlib import Path
from PIL import Image as PILImage
import tempfile
import os

from portrait_helper.image.loader import load_from_file, Image


class TestImageFormatSupport:
    """Contract tests for supported image formats."""

    def create_test_image(self, format: str) -> str:
        """Create a temporary test image file.

        Args:
            format: Image format (PNG, JPEG, GIF, BMP, WebP)

        Returns:
            Path to temporary image file
        """
        test_image = PILImage.new("RGB", (100, 100), color="blue")
        suffix_map = {
            "PNG": ".png",
            "JPEG": ".jpg",
            "GIF": ".gif",
            "BMP": ".bmp",
            "WebP": ".webp",
        }

        with tempfile.NamedTemporaryFile(suffix=suffix_map.get(format, ".png"), delete=False) as tmp:
            test_image.save(tmp.name, format)
            return tmp.name

    def test_load_jpeg_format(self):
        """Test JPEG format is supported."""
        tmp_path = self.create_test_image("JPEG")
        try:
            image = load_from_file(tmp_path)
            assert image.format in ("JPEG", "JFIF")  # PIL may report as JFIF
            assert image.is_loaded is True
        finally:
            os.unlink(tmp_path)

    def test_load_png_format(self):
        """Test PNG format is supported."""
        tmp_path = self.create_test_image("PNG")
        try:
            image = load_from_file(tmp_path)
            assert image.format == "PNG"
            assert image.is_loaded is True
        finally:
            os.unlink(tmp_path)

    def test_load_gif_format(self):
        """Test GIF format is supported."""
        tmp_path = self.create_test_image("GIF")
        try:
            image = load_from_file(tmp_path)
            assert image.format == "GIF"
            assert image.is_loaded is True
        finally:
            os.unlink(tmp_path)

    def test_load_bmp_format(self):
        """Test BMP format is supported."""
        tmp_path = self.create_test_image("BMP")
        try:
            image = load_from_file(tmp_path)
            assert image.format == "BMP"
            assert image.is_loaded is True
        finally:
            os.unlink(tmp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_load_webp_format(self):
        """Test WebP format is supported (if available)."""
        tmp_path = self.create_test_image("WebP")
        try:
            image = load_from_file(tmp_path)
            # Format is normalized to "WebP" (not "WEBP")
            assert image.format == "WebP"
            assert image.is_loaded is True
        finally:
            os.unlink(tmp_path)

    def test_unsupported_format_raises_error(self):
        """Test unsupported format raises ValueError."""
        # Create a file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
            tmp.write(b"Invalid format")
            tmp_path = tmp.name

            try:
                with pytest.raises(ValueError):
                    load_from_file(tmp_path)
            finally:
                os.unlink(tmp_path)

    @pytest.mark.skipif(
        not hasattr(PILImage, "features") or "webp" not in PILImage.features.get("formats", []),
        reason="WebP support not available in this PIL build",
    )
    def test_regression_other_formats_after_webp_fix(self):
        """Test T034: Regression test - verify other formats still work after WebP fix.
        
        This test ensures that fixing the WebP skew bug doesn't break
        other image formats (JPEG, PNG, GIF, BMP).
        """
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QImage
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        formats_to_test = ["JPEG", "PNG", "GIF", "BMP"]
        
        for fmt in formats_to_test:
            tmp_path = self.create_test_image(fmt)
            try:
                # Load image
                image = load_from_file(tmp_path)
                assert image.is_loaded is True
                
                # Convert to QImage using ImageViewer
                from portrait_helper.gui.image_viewer import ImageViewer
                viewer = ImageViewer()
                pil_image = image.get_pixel_data()
                qimage = viewer._pil_to_qimage(pil_image)
                
                # Verify QImage is valid
                assert qimage.width() == 100
                assert qimage.height() == 100
                assert not qimage.isNull()
                
                # Verify format is correct
                assert qimage.format() in (
                    QImage.Format.Format_RGB888,
                    QImage.Format.Format_RGBA8888
                )
                
                # Verify we can read pixels (no crash)
                pixel = qimage.pixel(0, 0)
                assert pixel is not None
                
            finally:
                os.unlink(tmp_path)

