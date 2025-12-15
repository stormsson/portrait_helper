# Quickstart Guide: Portrait Helper Application

**Date**: 2025-11-15  
**Feature**: Portrait Helper Application

## Purpose

This guide provides step-by-step instructions to verify the application works correctly after implementation. Each scenario tests a specific user story independently.

## Prerequisites

- Python 3.11+ installed
- Application dependencies installed (`pip install -r requirements.txt`)
- Test images available (local files or accessible URLs)

## User Story 1: Load and Display Images

### Scenario 1.1: Load Local Image File

**Steps**:
1. Launch the application
2. Click "File" → "Load Image" (or use keyboard shortcut)
3. Select a local image file (JPEG, PNG, or other supported format)
4. Observe the image displayed in the main window

**Expected Result**:
- Image appears in the window within 2 seconds
- Image maintains its aspect ratio
- Window can be resized and image adapts while keeping aspect ratio

**Verification**:
- ✅ Image displays correctly
- ✅ Aspect ratio preserved
- ✅ Window resize works

### Scenario 1.2: Load Image from Web URL

**Steps**:
1. Launch the application
2. Press Ctrl+V (or Cmd+V on macOS) to paste a web URL
3. Enter a valid image URL (e.g., `https://example.com/image.jpg`)
4. Press Enter or click "Load"

**Expected Result**:
- Image downloads and displays within 5 seconds (for images <5MB)
- Image appears in the window
- Image maintains aspect ratio

**Verification**:
- ✅ Web image loads successfully
- ✅ Image displays correctly
- ✅ Loading time acceptable

### Scenario 1.3: Handle Invalid Image File

**Steps**:
1. Launch the application
2. Click "File" → "Load Image"
3. Select an invalid file (e.g., a text file renamed to .jpg)
4. Observe error handling

**Expected Result**:
- Error message displayed explaining the issue
- Application remains stable
- User can try loading another file

**Verification**:
- ✅ Error message is clear and helpful
- ✅ Application doesn't crash
- ✅ User can recover from error

## User Story 2: Zoom and Pan Image

### Scenario 2.1: Zoom In/Out with Mouse Wheel

**Steps**:
1. Load an image (any image from Story 1)
2. Scroll mouse wheel up to zoom in
3. Scroll mouse wheel down to zoom out
4. Continue zooming to test min/max limits

**Expected Result**:
- Image zooms in when scrolling up
- Image zooms out when scrolling down
- Zoom centers on current view position
- Zoom stops at minimum (10%) and maximum (1000%) levels
- Zoom operations are smooth and responsive

**Verification**:
- ✅ Zoom in works correctly
- ✅ Zoom out works correctly
- ✅ Zoom limits enforced
- ✅ Performance is smooth

### Scenario 2.2: Pan Zoomed Image

**Steps**:
1. Load an image
2. Zoom in so image is larger than window
3. Click and drag the image to pan
4. Drag in different directions

**Expected Result**:
- Image moves smoothly when dragging
- Panning reveals different areas of the image
- Panning is responsive (no noticeable lag)
- Panning stops at image boundaries

**Verification**:
- ✅ Pan works correctly
- ✅ Boundaries respected
- ✅ Performance is responsive (<50ms)

### Scenario 2.3: Reset Zoom

**Steps**:
1. Load an image
2. Zoom in significantly
3. Pan to a corner of the image
4. Right-click and select "Reset Zoom" (or use keyboard shortcut)
5. Observe zoom and position reset

**Expected Result**:
- Zoom returns to fit-to-window (100%)
- Image is centered
- Aspect ratio maintained
- Operation completes quickly

**Verification**:
- ✅ Zoom resets correctly
- ✅ Image is centered
- ✅ Operation is fast

## User Story 3: Grid Overlay

### Scenario 3.1: Show/Hide Grid

**Steps**:
1. Load an image
2. Open grid configuration panel
3. Toggle "Show Grid" on
4. Toggle "Show Grid" off
5. Repeat toggle several times

**Expected Result**:
- Grid appears when enabled
- Grid disappears when disabled
- Toggle responds instantly (<100ms)
- Grid does not affect image display

**Verification**:
- ✅ Grid shows/hides correctly
- ✅ Toggle is responsive
- ✅ Image unaffected

### Scenario 3.2: Adjust Grid Size

**Steps**:
1. Load an image
2. Enable grid
3. Increase grid size (fewer subdivisions)
4. Decrease grid size (more subdivisions)
5. Test min/max limits

**Expected Result**:
- Grid cells become larger when size increased
- Grid cells become smaller when size decreased
- Grid always has square subdivisions
- Grid updates immediately (<100ms)
- Grid size respects min/max limits

**Verification**:
- ✅ Grid size adjusts correctly
- ✅ Subdivisions are square
- ✅ Updates are immediate
- ✅ Limits enforced

### Scenario 3.3: Grid with Zoom/Pan

**Steps**:
1. Load an image
2. Enable grid
3. Zoom in on the image
4. Pan the image
5. Observe grid behavior

**Expected Result**:
- Grid moves with image during pan
- Grid scales with zoom
- Grid maintains alignment with image
- Grid remains visible and aligned

**Verification**:
- ✅ Grid follows image during pan
- ✅ Grid scales with zoom
- ✅ Alignment maintained

### Scenario 3.4: Change Grid Color

**Steps**:
1. Load an image
2. Enable grid
3. Open grid configuration
4. Change grid color (e.g., to red, blue, or custom color)
5. Observe grid appearance

**Expected Result**:
- Grid color changes immediately
- New color is visible and distinct
- Color change does not affect grid size or alignment

**Verification**:
- ✅ Grid color changes correctly
- ✅ Change is immediate
- ✅ Other grid properties unaffected

## User Story 4: Black and White Filter

### Scenario 4.1: Toggle Black/White Mode

**Steps**:
1. Load a color image
2. Right-click on the image
3. Select "Toggle Black/White Mode"
4. Observe image changes to grayscale
5. Toggle again to return to color

**Expected Result**:
- Image displays in grayscale when enabled
- Image returns to color when disabled
- Toggle completes within 200ms
- Zoom and pan position preserved during toggle

**Verification**:
- ✅ Filter applies correctly
- ✅ Toggle works both ways
- ✅ Performance is fast
- ✅ Viewport state preserved

### Scenario 4.2: Filter with Zoom/Pan

**Steps**:
1. Load a color image
2. Zoom in and pan to a specific area
3. Toggle black/white mode
4. Verify zoom and pan position

**Expected Result**:
- Filter applies correctly
- Zoom level unchanged
- Pan position unchanged
- Same area of image visible

**Verification**:
- ✅ Filter doesn't affect viewport
- ✅ Zoom preserved
- ✅ Pan preserved

## Integration Scenarios

### Scenario I.1: Complete Workflow

**Steps**:
1. Load an image from web URL
2. Zoom in to examine details
3. Pan to different areas
4. Enable grid overlay
5. Adjust grid size
6. Toggle black/white mode
7. Reset zoom
8. Resize window

**Expected Result**:
- All features work together correctly
- No conflicts between features
- Performance remains acceptable
- Application remains stable

**Verification**:
- ✅ All features work in combination
- ✅ No regressions
- ✅ Performance acceptable

### Scenario I.2: Window Resize with All Features

**Steps**:
1. Load an image
2. Enable grid
3. Zoom in
4. Pan to corner
5. Toggle black/white mode
6. Resize window to different sizes
7. Verify all states preserved

**Expected Result**:
- Window resizes correctly
- Aspect ratio maintained
- Grid remains aligned
- Zoom/pan state preserved
- Filter state preserved

**Verification**:
- ✅ Resize works with all features
- ✅ States preserved correctly
- ✅ No visual glitches

## Performance Validation

### Scenario P.1: Large Image Handling

**Steps**:
1. Load a large image (>50MB if available)
2. Perform zoom operations
3. Perform pan operations
4. Toggle grid
5. Toggle filter

**Expected Result**:
- Image loads successfully
- Operations remain responsive
- No memory issues
- Application remains stable

**Verification**:
- ✅ Large images handled correctly
- ✅ Performance acceptable
- ✅ Memory usage reasonable

## Error Handling Validation

### Scenario E.1: Network Error Handling

**Steps**:
1. Attempt to load image from invalid URL
2. Attempt to load image from slow/unavailable URL
3. Observe error messages

**Expected Result**:
- Clear error messages displayed
- Application remains stable
- User can try again

**Verification**:
- ✅ Error messages are helpful
- ✅ Application doesn't crash
- ✅ Recovery possible

### Scenario E.2: Invalid File Handling

**Steps**:
1. Attempt to load corrupted image file
2. Attempt to load unsupported format
3. Observe error handling

**Expected Result**:
- Error messages explain the issue
- Application remains stable
- User can load another file

**Verification**:
- ✅ Errors handled gracefully
- ✅ Messages are clear
- ✅ Application stable

## Success Criteria Validation

After completing all scenarios, verify:

- ✅ SC-001: Local image loads within 2 seconds
- ✅ SC-002: Web image loads within 5 seconds
- ✅ SC-003: Aspect ratio maintained 100% of the time
- ✅ SC-004: Zoom operations complete smoothly
- ✅ SC-005: Pan responds with no noticeable lag
- ✅ SC-006: Grid toggle responds instantly
- ✅ SC-007: Grid size adjustment is immediate
- ✅ SC-008: Filter toggle completes within 200ms
- ✅ SC-009: Basic operations work on first attempt
- ✅ SC-010: Large images handled without degradation

## Notes

- Test with various image formats (JPEG, PNG, GIF, BMP, WebP)
- Test with different image sizes (small, medium, large)
- Test on different window sizes
- Verify keyboard shortcuts work
- Verify right-click menu works
- Test on target platforms (Windows, macOS, Linux)

