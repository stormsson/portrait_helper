# Viewport Library API Contract

**Date**: 2025-11-15  
**Feature**: Portrait Helper Application  
**Library**: `portrait_helper.image.viewport`

## Overview

The Viewport library provides calculations for image display transformations (zoom, pan, resize). This library is framework-agnostic and handles mathematical calculations only.

## CLI Interface

Per constitution principle II, the library exposes a CLI interface.

### Command: `calculate-viewport`

Calculate viewport parameters for given image and window dimensions.

**Usage**:
```bash
python -m portrait_helper.cli.viewport calculate-viewport \
  --image-width <width> \
  --image-height <height> \
  --window-width <width> \
  --window-height <height> \
  [--zoom <level>] \
  [--pan-x <offset>] \
  [--pan-y <offset>] \
  [--output-format <format>]
```

**Output (JSON format)**:
```json
{
  "display_width": 800.0,
  "display_height": 600.0,
  "zoom_level": 1.0,
  "visible_region": {
    "x": 0,
    "y": 0,
    "width": 1920,
    "height": 1080
  }
}
```

## Python API

### Class: `Viewport`

Manages viewport state and calculations.

**Initialization**:
```python
from portrait_helper.image.viewport import Viewport

viewport = Viewport(
    image_width=1920,
    image_height=1080,
    window_width=800,
    window_height=600
)
```

**Attributes**:
- `zoom_level` (float): Current zoom (1.0 = 100%)
- `pan_offset_x` (float): Horizontal pan offset
- `pan_offset_y` (float): Vertical pan offset
- `window_width` (int): Window width
- `window_height` (int): Window height

**Methods**:

#### `set_zoom(level: float, center_x: float = None, center_y: float = None) -> None`

Set zoom level, optionally centered on specific point.

**Parameters**:
- `level` (float): Zoom level (0.1 to 10.0)
- `center_x` (float, optional): X coordinate to center zoom on
- `center_y` (float, optional): Y coordinate to center zoom on

**Raises**:
- `ValueError`: Zoom level out of bounds

#### `zoom_in(factor: float = 1.2, center_x: float = None, center_y: float = None) -> None`

Increase zoom level.

**Parameters**:
- `factor` (float): Zoom multiplier (default: 1.2)
- `center_x` (float, optional): X coordinate to center zoom on
- `center_y` (float, optional): Y coordinate to center zoom on

#### `zoom_out(factor: float = 0.8, center_x: float = None, center_y: float = None) -> None`

Decrease zoom level.

**Parameters**:
- `factor` (float): Zoom divisor (default: 0.8)
- `center_x` (float, optional): X coordinate to center zoom on
- `center_y` (float, optional): Y coordinate to center zoom on

#### `pan(delta_x: float, delta_y: float) -> None`

Pan viewport by offset.

**Parameters**:
- `delta_x` (float): Horizontal pan offset
- `delta_y` (float): Vertical pan offset

#### `reset_zoom() -> None`

Reset zoom to fit-to-window (1.0) and center image.

#### `resize_window(width: int, height: int) -> None`

Update window dimensions and recalculate viewport.

**Parameters**:
- `width` (int): New window width
- `height` (int): New window height

#### `get_display_size() -> tuple[float, float]`

Get calculated display size (width, height) in pixels.

**Returns**: `(display_width, display_height)`

#### `get_visible_region() -> dict`

Get visible region coordinates.

**Returns**:
```python
{
    "x": float,
    "y": float,
    "width": float,
    "height": float
}
```

#### `constrain_pan() -> None`

Ensure pan offsets are within image boundaries at current zoom level.

## Constants

- `MIN_ZOOM` (float): 0.1 (10%)
- `MAX_ZOOM` (float): 10.0 (1000%)
- `DEFAULT_ZOOM` (float): 1.0 (100%)

## Testing Contract

### Unit Tests Required

1. **Zoom Calculations**:
   - Zoom in increases zoom level correctly
   - Zoom out decreases zoom level correctly
   - Zoom respects min/max bounds
   - Zoom centers on specified point

2. **Pan Calculations**:
   - Pan updates offsets correctly
   - Pan constrained to image boundaries
   - Pan maintains position during zoom

3. **Resize Calculations**:
   - Window resize maintains aspect ratio
   - Display size calculated correctly
   - Visible region updated correctly

4. **Fit-to-Window**:
   - Reset zoom sets level to fit window
   - Image centered after reset
   - Aspect ratio preserved

### Integration Tests Required

1. **Zoom/Pan Interaction**:
   - Pan position maintained during zoom
   - Zoom centers correctly on pan position
   - Boundaries respected during combined operations

2. **Resize Interaction**:
   - Zoom level adjusted on resize if needed
   - Pan offsets adjusted on resize
   - Aspect ratio always maintained

