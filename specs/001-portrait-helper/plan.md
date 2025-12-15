# Implementation Plan: WebP Image Skew Bug Fix

**Branch**: `001-portrait-helper` | **Date**: 2025-01-27 | **Spec**: `/specs/001-portrait-helper/spec.md`
**Input**: Bug report: "WebP images are skewed when loaded - first line of pixels is ok, second line is shifted left by 1 pixel, and so on. This does not happen with any other format."

**Note**: This is a bug fix plan, not a new feature. The plan focuses on diagnosing and fixing the WebP image display issue.

## Summary

**Problem**: WebP images display with progressive horizontal skew - each scanline is shifted left by 1 pixel relative to the previous line. This affects only WebP format; JPEG, PNG, GIF, and BMP display correctly.

**Root Cause Hypothesis**: The issue is likely in the PIL-to-QImage conversion in `_pil_to_qimage()` method in `src/portrait_helper/gui/image_viewer.py`. WebP images may have different stride/padding requirements or byte alignment issues when converted to QImage format.

**Solution Approach**: 
1. Research WebP-specific conversion issues between PIL and QImage
2. Fix the `_pil_to_qimage()` method to properly handle WebP format stride/alignment
3. Add regression tests to prevent recurrence
4. Verify fix works for all image formats

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PySide6 (Qt6), Pillow (PIL), requests  
**Storage**: N/A (in-memory image processing)  
**Testing**: pytest, pytest-qt  
**Target Platform**: Desktop (Windows, macOS, Linux)  
**Project Type**: Single desktop application  
**Performance Goals**: Image display should render correctly without visual artifacts  
**Constraints**: Must maintain backward compatibility with existing image formats (JPEG, PNG, GIF, BMP)  
**Scale/Scope**: Bug fix affecting WebP image display functionality

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First
✅ **PASS**: Bug fix is within existing `image.loader` and `gui.image_viewer` libraries. No new libraries required.

### II. CLI Interface
✅ **PASS**: Existing CLI interfaces remain unchanged. Bug fix is internal to image display.

### III. Test-First (NON-NEGOTIABLE)
⚠️ **REQUIRES ATTENTION**: Must write failing test that reproduces the WebP skew bug before implementing fix. Test should verify correct pixel alignment for WebP images.

### IV. Integration Testing
✅ **PASS**: Integration test needed to verify WebP images display correctly end-to-end (load → convert → display).

### V. Observability & Simplicity
✅ **PASS**: Fix should be minimal and focused. Add logging if needed for debugging.

**Gate Status**: ✅ **PASS** (with test-first requirement)

## Project Structure

### Documentation (this feature)

```text
specs/001-portrait-helper/
├── plan.md              # This file
├── research.md          # Phase 0 output - WebP conversion research
├── data-model.md        # Existing (no changes needed)
├── quickstart.md        # Existing (no changes needed)
├── contracts/           # Existing (no changes needed)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── portrait_helper/
│   ├── image/
│   │   └── loader.py          # Image loading (may need WebP-specific handling)
│   └── gui/
│       └── image_viewer.py    # PRIMARY FIX LOCATION: _pil_to_qimage() method
│
tests/
├── contract/
│   └── test_image_formats.py  # Add WebP display verification test
├── integration/
│   └── test_image_pipeline.py # Add WebP end-to-end test
└── unit/
    └── test_image_viewer.py   # NEW: Unit tests for _pil_to_qimage() conversion
```

**Structure Decision**: Single project structure. Bug fix touches existing files in `src/portrait_helper/gui/image_viewer.py` and adds tests.

## Complexity Tracking

> **No constitution violations - standard bug fix**

## Phase 0: Research & Root Cause Analysis

### Research Tasks

1. **WebP Format Characteristics**
   - Research WebP image format specifics (stride, padding, byte alignment)
   - Investigate known issues with PIL WebP loading
   - Check if WebP images have different internal representation in PIL

2. **PIL-to-QImage Conversion**
   - Research QImage format requirements (RGB888, RGBA8888 stride/padding)
   - Investigate known issues with `tobytes("raw", "RGB")` for WebP images
   - Check if WebP requires different conversion approach than other formats

3. **Stride/Padding Issues**
   - Research how QImage handles image stride (bytes per line)
   - Investigate if PIL WebP images have non-standard stride
   - Check if explicit stride calculation is needed for WebP

4. **Alternative Conversion Methods**
   - Research alternative PIL-to-QImage conversion methods
   - Investigate using `PIL.ImageQt` if available in PySide6
   - Check if saving to temporary format (PNG bytes) then loading works

### Expected Research Output

`research.md` should document:
- Root cause of WebP skew (stride/padding/alignment issue)
- Recommended fix approach
- Alternative solutions considered
- Testing strategy for verification

## Phase 1: Design & Implementation Plan

### Root Cause Analysis

**Hypothesis**: The `_pil_to_qimage()` method uses `pil_image.tobytes("raw", "RGB")` which may not account for WebP-specific stride requirements. QImage expects tightly-packed bytes with specific stride, but WebP images may have different internal representation.

**Investigation Steps**:
1. Compare PIL image properties (mode, size, stride) for WebP vs other formats
2. Check if WebP images need explicit stride calculation
3. Verify if `tobytes()` output matches QImage expectations for WebP

### Fix Strategy

**Option 1: Explicit Stride Calculation** (Preferred if needed)
- Calculate proper stride for QImage format
- Ensure bytes are properly aligned
- Handle WebP-specific requirements

**Option 2: Use PIL.ImageQt** (If available)
- Use PIL's built-in Qt conversion if available in PySide6
- May handle format-specific conversions automatically

**Option 3: Intermediate Format Conversion**
- Convert WebP to PNG bytes in memory
- Load PNG bytes into QImage
- More overhead but guaranteed compatibility

**Option 4: Format-Specific Handling**
- Add WebP-specific conversion path in `_pil_to_qimage()`
- Handle WebP differently from other formats

### Implementation Plan

1. **Write Failing Test** (Test-First)
   - Create test that loads WebP image and verifies pixel alignment
   - Test should fail with current implementation (reproduces bug)
   - Test should pass after fix

2. **Fix `_pil_to_qimage()` Method**
   - Implement fix based on research findings
   - Ensure backward compatibility with other formats
   - Add format-specific handling if needed

3. **Add Regression Tests**
   - Test WebP images of various sizes
   - Test WebP images with different modes (RGB, RGBA)
   - Verify other formats still work correctly

4. **Integration Testing**
   - End-to-end test: Load WebP → Display → Verify no skew
   - Test WebP from both file and URL sources

### API Contracts

No API changes required. Internal method `_pil_to_qimage()` is private.

## Phase 2: Implementation Tasks

*(Will be generated by `/speckit.tasks` command)*

## Success Criteria

- **SC-001**: WebP images display without horizontal skew in 100% of test cases
- **SC-002**: Other image formats (JPEG, PNG, GIF, BMP) continue to display correctly
- **SC-003**: WebP images load and display within performance targets (<2s for local, <5s for URL)
- **SC-004**: Regression tests prevent recurrence of this bug
- **SC-005**: Fix is minimal and doesn't introduce complexity

## Risk Assessment

**Low Risk**:
- Fix is isolated to single method
- Other formats unaffected
- Can be tested independently

**Medium Risk**:
- If fix requires format-specific handling, may need maintenance
- Performance impact if using intermediate conversion

**Mitigation**:
- Comprehensive test coverage
- Performance testing with various WebP image sizes
- Fallback to alternative approach if primary fix fails
