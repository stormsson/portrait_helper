"""Unit tests for grid overlay library."""

import pytest
from portrait_helper.grid.config import (
    GridConfiguration,
    MIN_SUBDIVISIONS,
    MAX_SUBDIVISIONS,
    DEFAULT_SUBDIVISIONS,
)


class TestGridConfiguration:
    """Unit tests for GridConfiguration entity."""

    def test_grid_configuration_creation_with_defaults(self):
        """Test GridConfiguration creation with default values."""
        config = GridConfiguration()

        assert config.visible is False
        assert config.subdivision_count == DEFAULT_SUBDIVISIONS
        assert config.color == (255, 255, 255)
        assert config.line_width == 1.0
        assert config.opacity == 1.0

    def test_grid_configuration_creation_with_custom_values(self):
        """Test GridConfiguration creation with custom values."""
        config = GridConfiguration(
            visible=True,
            subdivision_count=5,
            color=(255, 0, 0),
            line_width=2.0,
            opacity=0.5,
        )

        assert config.visible is True
        assert config.subdivision_count == 5
        assert config.color == (255, 0, 0)
        assert config.line_width == 2.0
        assert config.opacity == 0.5

    def test_toggle_visible(self):
        """Test toggle_visible method."""
        config = GridConfiguration(visible=False)
        assert config.visible is False

        config.toggle_visible()
        assert config.visible is True

        config.toggle_visible()
        assert config.visible is False

    def test_increase_size(self):
        """Test increase_size method (fewer subdivisions)."""
        config = GridConfiguration(subdivision_count=3)
        initial_count = config.subdivision_count

        config.increase_size()
        assert config.subdivision_count == initial_count + 1

        # Should not exceed MAX_SUBDIVISIONS
        config = GridConfiguration(subdivision_count=MAX_SUBDIVISIONS)
        config.increase_size()
        assert config.subdivision_count == MAX_SUBDIVISIONS

    def test_decrease_size(self):
        """Test decrease_size method (more subdivisions)."""
        config = GridConfiguration(subdivision_count=5)
        initial_count = config.subdivision_count

        config.decrease_size()
        assert config.subdivision_count == initial_count - 1

        # Should not go below MIN_SUBDIVISIONS
        config = GridConfiguration(subdivision_count=MIN_SUBDIVISIONS)
        config.decrease_size()
        assert config.subdivision_count == MIN_SUBDIVISIONS

    def test_set_color_rgb(self):
        """Test set_color with RGB tuple."""
        config = GridConfiguration()
        config.set_color((128, 64, 32))

        assert config.color == (128, 64, 32)

    def test_set_color_rgba(self):
        """Test set_color with RGBA tuple."""
        config = GridConfiguration()
        config.set_color((128, 64, 32, 255))

        assert config.color == (128, 64, 32, 255)

    def test_set_color_invalid(self):
        """Test set_color with invalid color tuple."""
        config = GridConfiguration()

        with pytest.raises(ValueError, match="Color must be RGB or RGBA tuple"):
            config.set_color((128, 64))  # Too few components

        with pytest.raises(ValueError, match="Color must be RGB or RGBA tuple"):
            config.set_color((128, 64, 32, 255, 0))  # Too many components

    def test_subdivision_count_bounds_validation(self):
        """Test subdivision_count bounds validation."""
        # Below minimum
        with pytest.raises(
            ValueError,
            match=f"Subdivision count must be between {MIN_SUBDIVISIONS} and {MAX_SUBDIVISIONS}",
        ):
            GridConfiguration(subdivision_count=MIN_SUBDIVISIONS - 1)

        # Above maximum
        with pytest.raises(
            ValueError,
            match=f"Subdivision count must be between {MIN_SUBDIVISIONS} and {MAX_SUBDIVISIONS}",
        ):
            GridConfiguration(subdivision_count=MAX_SUBDIVISIONS + 1)

    def test_line_width_validation(self):
        """Test line_width validation."""
        with pytest.raises(ValueError, match="Line width must be positive"):
            GridConfiguration(line_width=0)

        with pytest.raises(ValueError, match="Line width must be positive"):
            GridConfiguration(line_width=-1.0)

    def test_opacity_validation(self):
        """Test opacity validation."""
        with pytest.raises(ValueError, match="Opacity must be between 0.0 and 1.0"):
            GridConfiguration(opacity=-0.1)

        with pytest.raises(ValueError, match="Opacity must be between 0.0 and 1.0"):
            GridConfiguration(opacity=1.1)

    def test_cell_size_calculation(self):
        """Test cell_size calculation."""
        config = GridConfiguration(subdivision_count=3)

        # Initially zero
        assert config.cell_size == 0.0

        # Calculate for square viewport
        config.calculate_cell_size(viewport_width=900, viewport_height=900)
        assert config.cell_size == 300.0  # 900 / 3

        # Calculate for rectangular viewport (uses smaller dimension)
        config.calculate_cell_size(viewport_width=1200, viewport_height=600)
        assert config.cell_size == 200.0  # 600 / 3 (uses height, smaller dimension)

        # Calculate for different subdivision count
        config = GridConfiguration(subdivision_count=5)
        config.calculate_cell_size(viewport_width=1000, viewport_height=1000)
        assert config.cell_size == 200.0  # 1000 / 5

    def test_cell_size_property(self):
        """Test cell_size property access."""
        config = GridConfiguration()
        assert config.cell_size == 0.0

        config.calculate_cell_size(viewport_width=600, viewport_height=600)
        assert config.cell_size == 200.0  # 600 / 3 (default subdivisions)


class TestGridRenderingCalculations:
    """Unit tests for grid rendering calculations."""

    def test_square_subdivisions(self):
        """Test that grid cells are always square."""
        config = GridConfiguration(subdivision_count=3)

        # Square viewport
        config.calculate_cell_size(viewport_width=900, viewport_height=900)
        cell_size = config.cell_size
        assert cell_size == 300.0

        # Rectangular viewport - should use smaller dimension
        config.calculate_cell_size(viewport_width=1200, viewport_height=600)
        cell_size = config.cell_size
        assert cell_size == 200.0  # Uses height (600) / 3

        # Wide viewport
        config.calculate_cell_size(viewport_width=1600, viewport_height=800)
        cell_size = config.cell_size
        assert cell_size == 266.66666666666663  # Uses height (800) / 3

    def test_grid_alignment_calculation(self):
        """Test grid alignment calculations."""
        config = GridConfiguration(subdivision_count=3)
        config.calculate_cell_size(viewport_width=900, viewport_height=900)

        cell_size = config.cell_size
        assert cell_size == 300.0

        # Grid lines should be at: 0, 300, 600, 900
        expected_lines = [0, 300, 600, 900]
        for i in range(config.subdivision_count + 1):
            line_position = i * cell_size
            assert line_position == expected_lines[i]

    def test_grid_scaling_with_viewport(self):
        """Test grid scales correctly with viewport size."""
        config = GridConfiguration(subdivision_count=4)

        # Small viewport
        config.calculate_cell_size(viewport_width=400, viewport_height=400)
        small_cell_size = config.cell_size
        assert small_cell_size == 100.0  # 400 / 4

        # Large viewport
        config.calculate_cell_size(viewport_width=1600, viewport_height=1600)
        large_cell_size = config.cell_size
        assert large_cell_size == 400.0  # 1600 / 4

        # Cell size should scale proportionally
        assert large_cell_size == small_cell_size * 4

    def test_grid_with_different_subdivision_counts(self):
        """Test grid calculations with different subdivision counts."""
        # 2x2 grid
        config2 = GridConfiguration(subdivision_count=2)
        config2.calculate_cell_size(viewport_width=1000, viewport_height=1000)
        assert config2.cell_size == 500.0

        # 3x3 grid
        config3 = GridConfiguration(subdivision_count=3)
        config3.calculate_cell_size(viewport_width=1000, viewport_height=1000)
        assert config3.cell_size == pytest.approx(333.333, rel=1e-3)

        # 5x5 grid
        config5 = GridConfiguration(subdivision_count=5)
        config5.calculate_cell_size(viewport_width=1000, viewport_height=1000)
        assert config5.cell_size == 200.0

    def test_grid_alignment_maintains_square_cells(self):
        """Test that grid alignment always maintains square cells."""
        config = GridConfiguration(subdivision_count=3)

        # Test various viewport aspect ratios
        test_cases = [
            (1200, 600),  # 2:1 wide
            (600, 1200),  # 1:2 tall
            (800, 800),   # 1:1 square
            (1920, 1080), # 16:9 wide
            (1080, 1920), # 9:16 tall
        ]

        for width, height in test_cases:
            config.calculate_cell_size(viewport_width=width, viewport_height=height)
            cell_size = config.cell_size

            # Cell size should be based on smaller dimension
            min_dimension = min(width, height)
            expected_cell_size = min_dimension / config.subdivision_count
            assert cell_size == expected_cell_size

            # Verify cells are square (width == height)
            # This is implicit in the calculation using min_dimension

