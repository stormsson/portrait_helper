# Image Loader Library API Contract

**Date**: 2025-11-15  
**Feature**: Portrait Helper Application  
**Library**: `portrait_helper.image.loader`

## Overview

The Image Loader library provides functionality to load images from local file system or web URLs. This library is framework-agnostic and can be used independently of the GUI layer.

## CLI Interface

Per constitution principle II, the library exposes a CLI interface.

### Command: `load-image`

Load an image from a file path or URL.

**Usage**:
```bash
python -m portrait_helper.cli.image_loader load-image <source> [--output-format <format>]
```

**Arguments**:
- `source` (required): File path or URL to image
- `--output-format` (optional): Output format (json, text). Default: text

**Output (text format)**:
```
SUCCESS
Width: 1920
Height: 1080
Format: JPEG
Aspect Ratio: 1.7778
Path: /path/to/image.jpg
```

**Output (JSON format)**:
```json
{
  "status": "success",
  "width": 1920,
  "height": 1080,
  "format": "JPEG",
  "aspect_ratio": 1.7778,
  "source": "/path/to/image.jpg"
}
```

**Error Output (stderr)**:
```
ERROR: File not found: /invalid/path.jpg
```

**Exit Codes**:
- `0`: Success
- `1`: File/URL not found or inaccessible
- `2`: Invalid image format
- `3`: Corrupted image data
- `4`: Network error (for URLs)

## Python API

### Function: `load_from_file(file_path: str) -> Image`

Load an image from a local file path.

**Parameters**:
- `file_path` (str): Path to image file

**Returns**:
- `Image`: Image object with loaded pixel data and metadata

**Raises**:
- `FileNotFoundError`: File does not exist
- `ValueError`: Invalid image format or corrupted data
- `IOError`: File cannot be read

**Example**:
```python
from portrait_helper.image.loader import load_from_file

try:
    image = load_from_file("/path/to/image.jpg")
    print(f"Loaded: {image.width}x{image.height}")
except FileNotFoundError:
    print("File not found")
```

### Function: `load_from_url(url: str, timeout: int = 30) -> Image`

Load an image from a web URL.

**Parameters**:
- `url` (str): HTTP/HTTPS URL to image
- `timeout` (int): Request timeout in seconds (default: 30)

**Returns**:
- `Image`: Image object with loaded pixel data and metadata

**Raises**:
- `requests.RequestException`: Network error or invalid URL
- `ValueError`: Invalid image format or corrupted data
- `TimeoutError`: Request timed out

**Example**:
```python
from portrait_helper.image.loader import load_from_url

try:
    image = load_from_url("https://example.com/image.png")
    print(f"Loaded: {image.width}x{image.height}")
except requests.RequestException as e:
    print(f"Network error: {e}")
```

### Class: `Image`

Represents a loaded image.

**Attributes**:
- `width` (int): Image width in pixels
- `height` (int): Image height in pixels
- `aspect_ratio` (float): Width / height
- `format` (str): Image format (JPEG, PNG, GIF, BMP, WebP)
- `source` (str): Original source (file path or URL)
- `pixel_data` (PIL.Image): Pillow Image object

**Methods**:
- `get_pixel_data() -> PIL.Image`: Returns Pillow Image object
- `is_valid() -> bool`: Checks if image data is valid
- `get_metadata() -> dict`: Returns image metadata as dictionary

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## Error Handling

All functions raise exceptions for error conditions. CLI interface outputs errors to stderr and uses exit codes. Python API uses standard exception types.

## Testing Contract

### Unit Tests Required

1. **File Loading**:
   - Valid image file loads successfully
   - Non-existent file raises FileNotFoundError
   - Invalid format raises ValueError
   - Corrupted file raises ValueError

2. **URL Loading**:
   - Valid URL loads successfully
   - Invalid URL raises RequestException
   - Timeout raises TimeoutError
   - Non-image URL raises ValueError

3. **Format Support**:
   - All supported formats load correctly
   - Unsupported formats raise ValueError

4. **Metadata**:
   - Width/height are correct
   - Aspect ratio is calculated correctly
   - Format is detected correctly

### Integration Tests Required

1. **CLI Interface**:
   - CLI command loads file successfully
   - CLI command loads URL successfully
   - CLI outputs correct format (text/JSON)
   - CLI error handling works correctly

2. **Error Propagation**:
   - File errors propagate correctly
   - Network errors propagate correctly
   - Format errors propagate correctly

