# Research: Portrait Helper Application

**Date**: 2025-11-15  
**Feature**: Portrait Helper Application

## Technology Decisions

### Decision: Python 3.11+ with PySide6

**Rationale**: 
- Python provides excellent image processing libraries (Pillow)
- PySide6 (Qt6 bindings) offers cross-platform GUI capabilities
- Qt6 provides robust widget system for image display, zoom/pan, and overlay rendering
- PySide6 is actively maintained and well-documented
- Python ecosystem supports rapid development and testing

**Alternatives considered**:
- **Tkinter**: Built-in but limited widget capabilities and less modern appearance
- **PyQt6**: Similar to PySide6 but licensing concerns for commercial use
- **wxPython**: Cross-platform but less active development
- **Electron + JavaScript**: Heavier resource usage, not Python-native

### Decision: Pillow for Image Processing

**Rationale**:
- Industry-standard Python image library (PIL fork)
- Supports all required formats (JPEG, PNG, GIF, BMP, WebP)
- Efficient memory handling for large images
- Provides image transformation and filter capabilities
- Well-tested and stable
- WebP support available in Pillow 10.0.0+ (with libwebp dependency)

**Alternatives considered**:
- **OpenCV**: Overkill for basic image viewing, heavier dependency
- **ImageIO**: Less feature-complete than Pillow
- **Wand (ImageMagick bindings)**: External dependency, more complex setup

**WebP Format Support**:
- Pillow reports WebP format as "WEBP" (uppercase) but application standardizes to "WebP"
- Format normalization handles both "WEBP" and "WebP" variants from PIL
- WebP detection works via file extension (.webp) and content-type headers
- WebP support requires libwebp library (typically available on modern systems)
- Graceful fallback: If WebP not available in PIL build, format detection still works via extension/content-type

### Decision: requests for Web Image Loading

**Rationale**:
- Simple, well-established HTTP library
- Handles URL validation and error cases
- Supports timeout configuration for slow connections
- Easy to test with mock responses

**Alternatives considered**:
- **urllib (stdlib)**: More verbose, less user-friendly error handling
- **httpx**: Modern but adds unnecessary complexity for simple use case

## Architecture Patterns

### Decision: Library-First Modular Structure

**Rationale**:
- Aligns with constitution principle I (Library-First)
- Enables independent testing of each component
- Facilitates CLI interfaces for libraries (constitution principle II)
- Clear separation of concerns: image processing, grid rendering, GUI

**Pattern**: 
- Core libraries (image/, grid/) are framework-agnostic
- GUI layer (gui/) depends on libraries, not vice versa
- CLI interfaces (cli/) wrap library functionality

### Decision: Viewport-Based Zoom/Pan

**Rationale**:
- Standard approach for image viewers
- Efficient: only render visible portion
- Smooth performance for large images
- Qt Graphics View framework supports this pattern

**Implementation approach**:
- Maintain source image at full resolution
- Calculate visible region based on zoom level and pan offset
- Render only visible portion to viewport
- Update calculations on zoom/pan events

### Decision: Grid Overlay as Separate Layer

**Rationale**:
- Grid should not modify source image
- Enables show/hide without image reprocessing
- Can be rendered independently of image
- Maintains grid alignment during zoom/pan

**Implementation approach**:
- Grid rendered as overlay on top of image widget
- Grid coordinates calculated from viewport dimensions
- Grid size controls subdivision count (squared cells)
- Grid color configurable (added per spec update)

## Best Practices

### Image Loading
- Validate file format before loading
- Handle large images with memory-efficient loading
- Provide progress feedback for web image downloads
- Cache web images temporarily to avoid re-downloading
- Normalize format names (e.g., PIL "WEBP" → "WebP", "JFIF" → "JPEG")
- Support format detection via file extension, content-type, and PIL format reporting

### Zoom/Pan Implementation
- Constrain zoom to reasonable min/max levels (e.g., 0.1x to 10x)
- Center zoom on mouse cursor position for better UX
- Smooth pan with mouse drag, update viewport in real-time
- Reset zoom returns to fit-to-window with aspect ratio

### Grid Rendering
- Grid lines should be anti-aliased for smooth appearance
- Grid should update immediately on size/color changes
- Grid alignment maintained during zoom/pan operations
- Grid subdivisions always square (equal width/height cells)

### Performance
- Use Qt's QPixmap for efficient image rendering
- Implement viewport culling (only render visible area)
- Lazy loading for very large images (tile-based if needed)
- Optimize redraws to minimize repaint operations

## Testing Strategy

### Unit Tests
- Image loader: local file loading, web URL handling, error cases
- Viewport: zoom calculations, pan offset calculations, boundary constraints
- Filter: grayscale conversion, color preservation
- Grid: subdivision calculations, alignment calculations

### Integration Tests
- Image loading → display pipeline
- Zoom/pan → viewport updates → rendering
- Grid overlay → image rendering (combined display)
- Filter application → display updates
- Window resize → aspect ratio preservation

### Contract Tests
- Image format support (JPEG, PNG, GIF, BMP, WebP)
- Format normalization (WEBP → WebP, JFIF → JPEG)
- Error handling for invalid files/URLs
- Performance benchmarks (loading time, rendering speed)
- WebP format detection via extension and content-type

## Dependencies

### Required
- **PySide6** (>=6.5.0): GUI framework
- **Pillow** (>=10.0.0): Image processing
- **requests** (>=2.31.0): Web image loading

### Development
- **pytest** (>=7.4.0): Testing framework
- **pytest-qt** (>=4.2.0): PySide6 widget testing
- **black**: Code formatting
- **mypy**: Type checking (optional)

## Open Questions Resolved

1. **Q: How to handle very large images?**  
   A: Use viewport-based rendering, only load/display visible portion. For extremely large images (>100MB), consider tiling or downscaling for initial display.

2. **Q: Should grid be part of image or overlay?**  
   A: Overlay - keeps source image unchanged, enables show/hide without reprocessing.

3. **Q: How to handle aspect ratio during resize?**  
   A: Calculate display size based on window dimensions while maintaining image aspect ratio. Center image if window aspect doesn't match.

4. **Q: Keyboard shortcuts - platform-specific?**  
   A: Use Qt's standard shortcuts with platform-aware modifiers (Ctrl on Windows/Linux, Cmd on macOS).

5. **Q: How to handle WebP format variations?**  
   A: Pillow may report WebP as "WEBP" (uppercase) while application standardizes to "WebP". Format normalization maps both variants. WebP detection works via file extension (.webp) and HTTP content-type headers. If WebP support not available in PIL build, format detection still works via extension/content-type matching.

## WebP Image Skew Bug Investigation

**Date**: 2025-01-27  
**Issue**: WebP images display with progressive horizontal skew - each scanline shifted left by 1 pixel.

### Root Cause Analysis

**Symptom**: WebP images show progressive horizontal skew (first line correct, second line shifted left by 1 pixel, third line shifted left by 2 pixels, etc.). This affects only WebP format; JPEG, PNG, GIF, and BMP display correctly.

**Hypothesis**: The issue is in the PIL-to-QImage conversion in `_pil_to_qimage()` method. The `tobytes("raw", "RGB")` method may not properly handle WebP image stride/alignment requirements for QImage.

### Investigation Findings

**1. PIL `tobytes()` Behavior**
- `tobytes("raw", "RGB")` returns tightly-packed RGB bytes
- For standard formats (JPEG, PNG), bytes are correctly aligned
- WebP images may have different internal representation or stride requirements

**2. QImage Format Requirements**
- `QImage.Format_RGB888` expects tightly-packed RGB bytes with no padding
- QImage constructor: `QImage(bytes, width, height, format)` assumes bytes are tightly-packed
- If stride doesn't match width * bytes_per_pixel, pixels will be misaligned

**3. Potential Causes**
- **Stride Mismatch**: WebP images may have non-standard stride that `tobytes()` doesn't account for
- **Byte Alignment**: WebP decoder may produce bytes with different alignment than expected
- **Format Conversion**: Converting WebP to RGB in PIL may introduce stride issues

### Solution Approaches

**Option 1: Explicit Stride Calculation** (Primary)
- Calculate proper stride: `stride = width * bytes_per_pixel`
- Ensure bytes are tightly-packed before creating QImage
- Verify PIL image has no padding/stride issues

**Option 2: Use PIL.ImageQt** (If available)
- PIL provides `ImageQt` module for Qt integration
- May handle format-specific conversions automatically
- Check if available in PySide6: `from PIL import ImageQt`

**Option 3: Intermediate Format Conversion**
- Convert WebP to PNG bytes in memory: `pil_image.save(BytesIO(), format='PNG')`
- Load PNG bytes into QImage
- More overhead but guaranteed compatibility

**Option 4: Format-Specific Handling**
- Detect WebP format in `_pil_to_qimage()`
- Use alternative conversion method for WebP only
- Keep existing method for other formats

### Recommended Fix Strategy

**Primary Approach**: Verify and fix stride handling in `_pil_to_qimage()`
1. Ensure PIL image is in correct mode (RGB) before conversion
2. Use `tobytes("raw", "RGB")` which should produce tightly-packed bytes
3. Verify QImage constructor receives correct width/height
4. If issue persists, try explicit stride calculation or PIL.ImageQt

**Fallback Approach**: Use PIL.ImageQt if available
- Check if `PIL.ImageQt` is available in PySide6
- Use `ImageQt.toqimage()` for WebP images specifically
- Maintain existing method for other formats

**Testing Strategy**:
1. Create test WebP image with known pixel pattern (checkerboard)
2. Load and convert to QImage
3. Verify pixel alignment by checking specific pixel positions
4. Compare with other formats to ensure fix doesn't break them

### Known Issues & Considerations

- **Pillow Version**: Some Pillow versions have WebP-related bugs. Ensure latest version is used.
- **libwebp Version**: System libwebp library version may affect WebP decoding. Check if updating helps.
- **Platform Differences**: WebP handling may vary by platform. Test on all target platforms.

### Decision

**Chosen Approach**: Start with Option 1 (explicit stride verification), fallback to Option 2 (PIL.ImageQt) if needed.

**Rationale**: 
- Option 1 is minimal change and addresses root cause directly
- Option 2 provides robust alternative if Option 1 doesn't work
- Options 3 and 4 add unnecessary complexity

**Implementation Priority**:
1. Write failing test that reproduces WebP skew bug
2. Investigate PIL image properties (mode, size, stride) for WebP vs other formats
3. Fix `_pil_to_qimage()` method based on findings
4. Verify fix with regression tests

