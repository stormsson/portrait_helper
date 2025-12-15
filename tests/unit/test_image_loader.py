"""Unit tests for image loader library."""

import pytest
from pathlib import Path
from PIL import Image as PILImage
import tempfile
import os

from portrait_helper.image.loader import (
    Image,
    ImageLoadError,
    ImageFormatError,
    ImageCorruptionError,
    load_from_file,
    load_from_url,
)


class TestImageEntity:
    """Unit tests for Image entity."""

    def test_image_creation_with_valid_data(self):
        """Test Image entity creation with valid data."""
        # Create a test image
        test_image = PILImage.new("RGB", (100, 200), color="red")

        image = Image(
            width=100,
            height=200,
            format="PNG",
            source="/test/path.png",
            pixel_data=test_image,
            source_path="/test/path.png",
        )

        assert image.width == 100
        assert image.height == 200
        assert image.aspect_ratio == 0.5
        assert image.format == "PNG"
        assert image.source == "/test/path.png"
        assert image.is_loaded is True
        assert image.is_valid() is True

    def test_image_aspect_ratio_calculation(self):
        """Test aspect ratio is calculated correctly."""
        test_image = PILImage.new("RGB", (1920, 1080), color="blue")

        image = Image(
            width=1920,
            height=1080,
            format="JPEG",
            source="/test/image.jpg",
            pixel_data=test_image,
            source_path="/test/image.jpg",
        )

        assert image.aspect_ratio == pytest.approx(1920 / 1080, rel=1e-6)

    def test_image_metadata(self):
        """Test get_metadata returns correct information."""
        test_image = PILImage.new("RGB", (50, 75), color="green")

        image = Image(
            width=50,
            height=75,
            format="GIF",
            source="/test/image.gif",
            pixel_data=test_image,
            source_path="/test/image.gif",
        )

        metadata = image.get_metadata()
        assert metadata["width"] == 50
        assert metadata["height"] == 75
        assert metadata["format"] == "GIF"
        assert metadata["is_loaded"] is True
        assert metadata["source_path"] == "/test/image.gif"

    def test_image_validation_fails_when_not_loaded(self):
        """Test is_valid returns False when image not loaded."""
        image = Image(
            width=100,
            height=100,
            format="PNG",
            source="/test/path.png",
            pixel_data=None,
            source_path="/test/path.png",
        )

        assert image.is_loaded is False
        assert image.is_valid() is False

    def test_image_requires_source_path_or_url(self):
        """Test Image requires either source_path or source_url."""
        with pytest.raises(ValueError, match="Either source_path or source_url must be set"):
            Image(
                width=100,
                height=100,
                format="PNG",
                source="/test/path.png",
                pixel_data=None,
            )

    def test_image_cannot_have_both_source_path_and_url(self):
        """Test Image cannot have both source_path and source_url."""
        with pytest.raises(ValueError, match="Cannot set both source_path and source_url"):
            Image(
                width=100,
                height=100,
                format="PNG",
                source="/test/path.png",
                pixel_data=None,
                source_path="/test/path.png",
                source_url="http://example.com/image.png",
            )

    def test_image_requires_positive_dimensions(self):
        """Test Image requires positive width and height."""
        with pytest.raises(ValueError, match="Width and height must be positive integers"):
            Image(
                width=0,
                height=100,
                format="PNG",
                source="/test/path.png",
                pixel_data=None,
                source_path="/test/path.png",
            )


class TestLoadFromFile:
    """Unit tests for load_from_file function."""

    def test_load_valid_image_file(self):
        """Test loading a valid image file."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            test_image = PILImage.new("RGB", (100, 100), color="red")
            test_image.save(tmp.name, "PNG")

            try:
                image = load_from_file(tmp.name)

                assert image.width == 100
                assert image.height == 100
                assert image.format == "PNG"
                assert image.is_loaded is True
                assert image.is_valid() is True
            finally:
                os.unlink(tmp.name)

    def test_load_nonexistent_file_raises_error(self):
        """Test loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_from_file("/nonexistent/path/image.jpg")

    def test_load_invalid_format_raises_error(self):
        """Test loading invalid format raises ValueError."""
        # Create a text file (not an image)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as tmp:
            tmp.write("This is not an image")
            tmp_path = tmp.name

            try:
                with pytest.raises(ValueError, match="Invalid image format"):
                    load_from_file(tmp_path)
            finally:
                os.unlink(tmp_path)

    def test_load_corrupted_file_raises_error(self):
        """Test loading corrupted file raises ValueError."""
        # Create a file with invalid image data
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(b"Invalid image data")
            tmp_path = tmp.name

            try:
                with pytest.raises(ValueError):
                    load_from_file(tmp_path)
            finally:
                os.unlink(tmp_path)


class TestLoadFromURL:
    """Unit tests for load_from_url function."""

    @pytest.mark.skip(reason="Requires network access and mock server setup")
    def test_load_valid_url(self):
        """Test loading image from valid URL."""
        # This would require a mock HTTP server or actual network access
        # Skipped for now, will be implemented with proper mocking
        pass

    @pytest.mark.skip(reason="Requires network access and mock server setup")
    def test_load_invalid_url_raises_error(self):
        """Test loading from invalid URL raises RequestException."""
        # This would require proper mocking of requests library
        pass

    @pytest.mark.skip(reason="Requires network access and mock server setup")
    def test_load_timeout_raises_error(self):
        """Test loading from slow URL raises TimeoutError."""
        # This would require proper timeout testing
        pass

    @pytest.mark.skip(reason="Requires network access and mock server setup")
    def test_load_non_image_url_raises_error(self):
        """Test loading non-image URL raises ValueError."""
        # This would require proper content-type checking
        pass

