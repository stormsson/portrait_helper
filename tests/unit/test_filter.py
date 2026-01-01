"""Unit tests for image filter library."""

import pytest
from PIL import Image as PILImage

from portrait_helper.image.filter import FilterState


class TestFilterState:
    """Unit tests for FilterState entity."""

    def test_filter_state_creation_without_image(self):
        """Test FilterState creation without image data."""
        filter_state = FilterState()
        assert filter_state.grayscale_enabled is False
        assert filter_state.original_pixel_data is None
        assert filter_state.filtered_pixel_data is None

    def test_filter_state_creation_with_image(self):
        """Test FilterState creation with image data."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        assert filter_state.grayscale_enabled is False
        assert filter_state.original_pixel_data is test_image
        assert filter_state.filtered_pixel_data is None

    def test_filter_state_grayscale_enabled_initialization(self):
        """Test FilterState with grayscale enabled from start."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(
            original_pixel_data=test_image, grayscale_enabled=True
        )
        assert filter_state.grayscale_enabled is True
        assert filter_state.original_pixel_data is test_image

    def test_grayscale_enabled_toggle(self):
        """Test grayscale_enabled toggle functionality."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        
        # Initially disabled
        assert filter_state.grayscale_enabled is False
        
        # Toggle on
        filter_state.toggle_grayscale()
        assert filter_state.grayscale_enabled is True
        assert filter_state.filtered_pixel_data is not None
        
        # Toggle off (cache is preserved for performance)
        filter_state.toggle_grayscale()
        assert filter_state.grayscale_enabled is False
        # Cache is preserved for reuse when toggling back on
        assert filter_state.filtered_pixel_data is not None

    def test_original_pixel_data_preservation(self):
        """Test that original_pixel_data is preserved after filter application."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        original_copy = test_image.copy()
        filter_state = FilterState(original_pixel_data=test_image)
        
        # Apply filter
        filter_state.toggle_grayscale()
        
        # Original should still be the same
        assert filter_state.original_pixel_data is test_image
        assert filter_state.original_pixel_data.size == original_copy.size
        assert filter_state.original_pixel_data.mode == original_copy.mode

    def test_toggle_grayscale_without_image_raises_error(self):
        """Test that toggle_grayscale raises error when no image data."""
        filter_state = FilterState()
        with pytest.raises(ValueError, match="No original image data available"):
            filter_state.toggle_grayscale()

    def test_get_current_image_returns_original_when_disabled(self):
        """Test get_current_image returns original when grayscale disabled."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        assert filter_state.get_current_image() is test_image

    def test_get_current_image_returns_filtered_when_enabled(self):
        """Test get_current_image returns filtered when grayscale enabled."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        filter_state.toggle_grayscale()
        current = filter_state.get_current_image()
        assert current is not None
        assert current is filter_state.filtered_pixel_data
        assert current.mode == "L"  # Grayscale mode

    def test_get_current_image_returns_none_when_no_image(self):
        """Test get_current_image returns None when no image data."""
        filter_state = FilterState()
        assert filter_state.get_current_image() is None


class TestGrayscaleFilterApplication:
    """Unit tests for grayscale filter application."""

    def test_apply_grayscale_filter_to_rgb_image(self):
        """Test grayscale filter applied to RGB image."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        
        grayscale = filter_state.apply_grayscale_filter(test_image)
        assert grayscale.mode == "L"
        assert grayscale.size == test_image.size

    def test_apply_grayscale_filter_to_rgba_image(self):
        """Test grayscale filter applied to RGBA image."""
        test_image = PILImage.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        filter_state = FilterState(original_pixel_data=test_image)
        
        grayscale = filter_state.apply_grayscale_filter(test_image)
        assert grayscale.mode == "L"
        assert grayscale.size == test_image.size

    def test_apply_grayscale_filter_to_already_grayscale_image(self):
        """Test grayscale filter handles already grayscale image."""
        test_image = PILImage.new("L", (100, 100), color=128)
        filter_state = FilterState(original_pixel_data=test_image)
        
        grayscale = filter_state.apply_grayscale_filter(test_image)
        assert grayscale.mode == "L"
        assert grayscale.size == test_image.size
        # Should return a copy, not the same object
        assert grayscale is not test_image

    def test_grayscale_filter_preserves_image_dimensions(self):
        """Test grayscale filter preserves image dimensions."""
        test_image = PILImage.new("RGB", (800, 600), color="blue")
        filter_state = FilterState(original_pixel_data=test_image)
        
        grayscale = filter_state.apply_grayscale_filter(test_image)
        assert grayscale.width == 800
        assert grayscale.height == 600

    def test_grayscale_filter_caching(self):
        """Test that grayscale filter result is cached."""
        test_image = PILImage.new("RGB", (100, 100), color="red")
        filter_state = FilterState(original_pixel_data=test_image)
        
        # First toggle - should create filtered version
        filter_state.toggle_grayscale()
        first_filtered = filter_state.filtered_pixel_data
        
        # Toggle off and on again - should reuse cached version
        filter_state.toggle_grayscale()
        filter_state.toggle_grayscale()
        second_filtered = filter_state.filtered_pixel_data
        
        # Should be the same object (cached)
        assert first_filtered is second_filtered

    def test_grayscale_filter_creates_different_pixel_values(self):
        """Test that grayscale conversion actually changes pixel values."""
        # Create a colorful test image
        test_image = PILImage.new("RGB", (10, 10))
        pixels = []
        for y in range(10):
            for x in range(10):
                # Create a pattern with different colors
                pixels.append((x * 25, y * 25, (x + y) * 10))
        test_image.putdata(pixels)
        
        filter_state = FilterState(original_pixel_data=test_image)
        grayscale = filter_state.apply_grayscale_filter(test_image)
        
        # Grayscale should have different pixel values
        original_pixels = list(test_image.getdata())
        grayscale_pixels = list(grayscale.getdata())
        
        # All grayscale pixels should be single values (not tuples)
        assert all(isinstance(p, int) for p in grayscale_pixels)
        # Original pixels are tuples
        assert all(isinstance(p, tuple) for p in original_pixels)

