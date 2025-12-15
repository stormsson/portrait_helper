# Data Model: Portrait Helper Application

**Date**: 2025-11-15  
**Feature**: Portrait Helper Application

## Entities

### Image

Represents a loaded image with its properties and current display state.

**Attributes**:
- `source_path` (string, optional): Local file path if loaded from file system
- `source_url` (string, optional): Web URL if loaded from network
- `width` (integer): Original image width in pixels
- `height` (integer): Original image height in pixels
- `aspect_ratio` (float): Calculated as width / height
- `format` (string): Image format (JPEG, PNG, GIF, BMP, WebP)
- `pixel_data` (PIL.Image or QPixmap): In-memory image data
- `is_loaded` (boolean): Whether image data is currently loaded
- `load_error` (string, optional): Error message if loading failed

**State Transitions**:
- `UNLOADED` → `LOADING` → `LOADED` (success)
- `UNLOADED` → `LOADING` → `ERROR` (failure)
- `LOADED` → `UNLOADED` (when new image loaded)

**Validation Rules**:
- Either `source_path` or `source_url` must be set, not both
- `width` and `height` must be positive integers
- `aspect_ratio` must be positive
- `format` must be one of supported formats
- `pixel_data` must be valid image data when `is_loaded` is true

**Relationships**:
- Used by `Viewport` for display calculations
- Used by `Filter` for color transformations

### Viewport

Represents the visible area and transformation state of the displayed image.

**Attributes**:
- `zoom_level` (float): Current zoom multiplier (1.0 = 100%, 0.5 = 50%, 2.0 = 200%)
- `pan_offset_x` (float): Horizontal pan offset in pixels (relative to center)
- `pan_offset_y` (float): Vertical pan offset in pixels (relative to center)
- `window_width` (integer): Current window width in pixels
- `window_height` (integer): Current window height in pixels
- `display_width` (float): Calculated display width based on zoom and aspect ratio
- `display_height` (float): Calculated display height based on zoom and aspect ratio
- `visible_region_x` (float): X coordinate of visible region start
- `visible_region_y` (float): Y coordinate of visible region start
- `visible_region_width` (float): Width of visible region
- `visible_region_height` (float): Height of visible region

**State Transitions**:
- Initial state: `zoom_level = 1.0`, `pan_offset_x = 0`, `pan_offset_y = 0` (fit to window)
- Zoom in/out: `zoom_level` changes, `pan_offset` may adjust to keep center point
- Pan: `pan_offset_x` and `pan_offset_y` change
- Window resize: `window_width` and `window_height` change, `zoom_level` may reset to fit

**Validation Rules**:
- `zoom_level` must be between `MIN_ZOOM` (0.1) and `MAX_ZOOM` (10.0)
- `pan_offset_x` and `pan_offset_y` must be within image boundaries at current zoom
- `window_width` and `window_height` must be positive integers
- `display_width` and `display_height` must maintain image aspect ratio
- `visible_region` coordinates must be within image bounds

**Relationships**:
- References `Image` for source dimensions and aspect ratio
- Used by `ImageWidget` for rendering calculations
- Used by `GridOverlay` for grid alignment

### GridConfiguration

Represents the grid overlay settings.

**Attributes**:
- `visible` (boolean): Whether grid is currently displayed
- `subdivision_count` (integer): Number of grid subdivisions (e.g., 3 = 3x3 grid)
- `cell_size` (float): Calculated cell size in pixels (derived from subdivision_count)
- `color` (QColor or tuple): Grid line color (RGB/RGBA)
- `line_width` (float): Grid line width in pixels
- `opacity` (float): Grid opacity (0.0 to 1.0)

**State Transitions**:
- `visible` can toggle between true/false
- `subdivision_count` can increase/decrease within min/max bounds
- `color` can change to any valid color value
- Changes trigger immediate grid redraw

**Validation Rules**:
- `subdivision_count` must be between `MIN_SUBDIVISIONS` (2) and `MAX_SUBDIVISIONS` (50)
- `color` must be valid color representation
- `line_width` must be positive (typically 1.0 to 3.0 pixels)
- `opacity` must be between 0.0 and 1.0
- Grid cells are always square (equal width and height)

**Relationships**:
- Used by `GridOverlay` for rendering
- References `Viewport` for alignment and sizing calculations

### FilterState

Represents the current image filter state.

**Attributes**:
- `grayscale_enabled` (boolean): Whether black/white filter is active
- `original_pixel_data` (PIL.Image or QPixmap): Original image data (preserved for toggle)
- `filtered_pixel_data` (PIL.Image or QPixmap, optional): Grayscale version (cached)

**State Transitions**:
- `grayscale_enabled = false` → `true`: Apply grayscale filter, cache result
- `grayscale_enabled = true` → `false`: Restore original image data
- Filter application preserves zoom and pan state

**Validation Rules**:
- `original_pixel_data` must be valid image data
- `filtered_pixel_data` must be valid image data when `grayscale_enabled` is true
- Filter toggle must not affect viewport state (zoom/pan preserved)

**Relationships**:
- References `Image` for source data
- Used by `ImageWidget` for display rendering

## Data Flow

### Image Loading Flow
1. User initiates load (file dialog or URL paste)
2. `ImageLoader` validates source (file exists or URL accessible)
3. `ImageLoader` loads pixel data into `Image.pixel_data`
4. `Image` calculates dimensions and aspect ratio
5. `Viewport` initializes to fit image to window
6. `ImageWidget` renders image using viewport calculations

### Zoom/Pan Flow
1. User scrolls mouse wheel or drags image
2. `Viewport` updates `zoom_level` or `pan_offset`
3. `Viewport` recalculates `display_width`, `display_height`, `visible_region`
4. `ImageWidget` requests repaint with new viewport state
5. Only visible region is rendered for performance

### Grid Toggle Flow
1. User toggles grid visibility in configuration
2. `GridConfiguration.visible` updates
3. `GridOverlay` receives update event
4. Grid layer redraws (or hides) without affecting image layer

### Filter Toggle Flow
1. User toggles black/white mode
2. `FilterState.grayscale_enabled` toggles
3. If enabling: Apply grayscale filter, cache in `filtered_pixel_data`
4. If disabling: Restore `original_pixel_data`
5. `ImageWidget` updates display, preserves viewport state

## Constraints

### Performance Constraints
- Image loading must complete within 2s (local) or 5s (web)
- Viewport calculations must complete in <16ms for 60fps
- Grid rendering must not add >10ms to frame time
- Filter application must complete in <200ms

### Memory Constraints
- Large images (>50MB) may require viewport-based rendering only
- Original and filtered pixel data should not both be kept in memory simultaneously when possible
- Grid overlay uses minimal memory (vector calculations, not pixel data)

### Display Constraints
- Window must maintain minimum size (e.g., 400x300 pixels)
- Image display must maintain aspect ratio at all zoom levels
- Grid must align with image pixels, not screen pixels (for accuracy)

## Relationships Summary

```
Image (1) ──< (1) Viewport
Image (1) ──< (1) FilterState
Viewport (1) ──< (1) GridConfiguration
Viewport ──> Image (references for dimensions)
GridConfiguration ──> Viewport (references for alignment)
FilterState ──> Image (references for pixel data)
```

