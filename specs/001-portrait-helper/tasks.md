# Tasks: Portrait Helper Application

**Input**: Design documents from `/specs/001-portrait-helper/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per constitution (Test-First principle). All test tasks must be completed before implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow plan.md structure: `src/portrait_helper/` with subdirectories

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in src/portrait_helper/
- [x] T002 Initialize Python project with requirements.txt (PySide6, Pillow, requests, pytest, pytest-qt)
- [x] T003 [P] Create __init__.py files in src/portrait_helper/, src/portrait_helper/gui/, src/portrait_helper/image/, src/portrait_helper/grid/, src/portrait_helper/cli/
- [x] T004 [P] Create tests/ directory structure (unit/, integration/, contract/)
- [x] T005 [P] Configure pytest in pytest.ini or pyproject.toml
- [x] T006 [P] Setup logging configuration in src/portrait_helper/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create base Image entity class in src/portrait_helper/image/loader.py (attributes: width, height, aspect_ratio, format, source, pixel_data)
- [x] T008 [P] Create base Viewport entity class in src/portrait_helper/image/viewport.py (attributes: zoom_level, pan_offset_x, pan_offset_y, window_width, window_height)
- [x] T009 [P] Create base GridConfiguration entity class in src/portrait_helper/grid/config.py (attributes: visible, subdivision_count, color, line_width, opacity)
- [x] T010 [P] Create base FilterState entity class in src/portrait_helper/image/filter.py (attributes: grayscale_enabled, original_pixel_data, filtered_pixel_data)
- [x] T011 Setup error handling infrastructure in src/portrait_helper/image/loader.py (FileNotFoundError, ValueError, IOError, RequestException)
- [x] T012 [P] Setup structured logging for image operations in src/portrait_helper/image/loader.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and Display Images (Priority: P1) 🎯 MVP

**Goal**: Enable users to load images from local files or web URLs and display them in a resizable window that maintains aspect ratio.

**Independent Test**: Load a local image file and verify it displays correctly in a resizable window. Resize the window and confirm the image adapts while maintaining proportions.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T013 [P] [US1] Unit test for load_from_file in tests/unit/test_image_loader.py (valid file, non-existent file, invalid format, corrupted file)
- [x] T014 [P] [US1] Unit test for load_from_url in tests/unit/test_image_loader.py (valid URL, invalid URL, timeout, non-image URL)
- [x] T015 [P] [US1] Unit test for Image entity in tests/unit/test_image_loader.py (width, height, aspect_ratio, format, metadata)
- [x] T016 [P] [US1] Contract test for image formats in tests/contract/test_image_formats.py (JPEG, PNG, GIF, BMP, WebP)
- [x] T017 [US1] Integration test for image loading pipeline in tests/integration/test_image_pipeline.py (file load → Image entity → display ready)
- [x] T018 [US1] Integration test for window resize with aspect ratio in tests/integration/test_image_pipeline.py (resize → aspect ratio preserved)

### Implementation for User Story 1

- [x] T019 [US1] Implement load_from_file function in src/portrait_helper/image/loader.py (loads local image, validates format, creates Image entity)
- [x] T020 [US1] Implement load_from_url function in src/portrait_helper/image/loader.py (downloads web image, validates format, creates Image entity)
- [x] T021 [US1] Implement Image class in src/portrait_helper/image/loader.py (get_pixel_data, is_valid, get_metadata methods)
- [x] T022 [US1] Implement CLI interface for image loader in src/portrait_helper/cli/image_loader.py (load-image command with text/JSON output)
- [x] T023 [US1] Create main application window in src/portrait_helper/gui/main_window.py (QMainWindow with menu bar, file dialog)
- [x] T024 [US1] Create image viewer widget in src/portrait_helper/gui/image_viewer.py (QWidget that displays Image with aspect ratio preservation)
- [x] T025 [US1] Implement window resize handler in src/portrait_helper/gui/main_window.py (resizeEvent that maintains image aspect ratio)
- [x] T026 [US1] Implement file load menu action in src/portrait_helper/gui/main_window.py (File → Load Image opens dialog, loads file)
- [x] T027 [US1] Implement URL paste handler in src/portrait_helper/gui/main_window.py (Ctrl+V paste URL, loads image from web)
- [x] T028 [US1] Implement error message display in src/portrait_helper/gui/main_window.py (QMessageBox for load errors)
- [x] T029 [US1] Create application entry point in src/portrait_helper/main.py (QApplication initialization, main window launch)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can load images and view them in a resizable window.

---

## Phase 4: WebP Image Skew Bug Fix 🐛

**Goal**: Fix WebP image display bug where images are skewed (each scanline shifted left by 1 pixel). This is a critical bug fix that must be completed before proceeding with additional user stories.

**Problem**: WebP images display with progressive horizontal skew - first line correct, second line shifted left by 1 pixel, third line shifted left by 2 pixels, etc. This affects only WebP format; JPEG, PNG, GIF, and BMP display correctly.

**Root Cause**: Issue is in PIL-to-QImage conversion in `_pil_to_qimage()` method in `src/portrait_helper/gui/image_viewer.py`. WebP images may have different stride/padding requirements when converted to QImage format.

**Independent Test**: Load a WebP image with known pixel pattern (e.g., checkerboard), verify pixel alignment is correct (no skew). Compare with other formats to ensure fix doesn't break them.

### Tests for WebP Bug Fix ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (Test-First principle)**

- [x] T030 [P] [BUGFIX] Unit test for WebP pixel alignment in tests/unit/test_image_viewer.py (create test WebP image with checkerboard pattern, verify pixel positions after conversion to QImage)
- [x] T031 [P] [BUGFIX] Unit test for _pil_to_qimage conversion in tests/unit/test_image_viewer.py (test WebP format specifically, verify stride/alignment, compare with other formats)
- [x] T032 [BUGFIX] Integration test for WebP display correctness in tests/integration/test_image_pipeline.py (load WebP from file → display → verify no skew visually or programmatically)
- [x] T033 [BUGFIX] Integration test for WebP from URL in tests/integration/test_image_pipeline.py (load WebP from URL → display → verify no skew)
- [x] T034 [P] [BUGFIX] Regression test for other formats in tests/contract/test_image_formats.py (verify JPEG, PNG, GIF, BMP still display correctly after fix)

### Investigation for WebP Bug Fix

- [x] T035 [BUGFIX] Investigate PIL image properties for WebP in tests/unit/test_image_viewer.py (compare mode, size, stride for WebP vs other formats, log findings)
- [x] T036 [BUGFIX] Test PIL.ImageQt availability in src/portrait_helper/gui/image_viewer.py (check if PIL.ImageQt is available in PySide6, document findings)

### Implementation for WebP Bug Fix

- [x] T037 [BUGFIX] Fix _pil_to_qimage method in src/portrait_helper/gui/image_viewer.py (implement fix based on investigation findings - explicit stride calculation or PIL.ImageQt fallback)
- [x] T038 [BUGFIX] Add format-specific handling for WebP in src/portrait_helper/gui/image_viewer.py (if needed, add WebP-specific conversion path while maintaining backward compatibility)

### Verification for WebP Bug Fix

- [x] T039 [BUGFIX] Verify fix with various WebP image sizes in tests/integration/test_image_pipeline.py (test small, medium, large WebP images)
- [x] T040 [BUGFIX] Verify fix with WebP images in different modes in tests/integration/test_image_pipeline.py (test RGB, RGBA WebP images if applicable)
- [x] T041 [BUGFIX] Performance test for WebP conversion in tests/integration/test_image_pipeline.py (ensure fix doesn't degrade performance significantly)

**Checkpoint**: At this point, WebP images should display correctly without skew. All other image formats should continue to work correctly. Bug fix is complete and regression tests prevent recurrence.

---

## Phase 5: User Story 3 - Grid Overlay (Priority: P2)

**Goal**: Enable users to overlay a grid on images with configurable size and color for composition assistance.

**Independent Test**: Load an image, enable grid, adjust grid size, change grid color. Verify grid shows/hides correctly and maintains alignment during zoom/pan.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T059 [P] [US3] Unit test for GridConfiguration in tests/unit/test_grid_overlay.py (visible toggle, subdivision_count bounds, color, cell_size calculation)
- [x] T060 [P] [US3] Unit test for grid rendering calculations in tests/unit/test_grid_overlay.py (square subdivisions, alignment, scaling)
- [x] T061 [US3] Integration test for grid overlay rendering in tests/integration/test_grid_rendering.py (grid displays, hides, updates on config change)
- [x] T062 [US3] Integration test for grid with zoom/pan in tests/integration/test_grid_rendering.py (grid moves with image, maintains alignment)

### Implementation for User Story 3

- [x] T063 [US3] Implement GridConfiguration class methods in src/portrait_helper/grid/config.py (toggle_visible, increase_size, decrease_size, set_color, validate bounds)
- [x] T064 [US3] Implement GridOverlay rendering in src/portrait_helper/grid/overlay.py (calculate grid lines, render as overlay layer)
- [x] T065 [US3] Implement CLI interface for grid overlay in src/portrait_helper/cli/grid_overlay.py (calculate-grid command with subdivision count, color, output format)
- [x] T066 [US3] Create grid configuration panel widget in src/portrait_helper/gui/grid_config.py (show/hide toggle, size controls, color picker)
- [x] T067 [US3] Integrate grid overlay with ImageViewer in src/portrait_helper/gui/image_viewer.py (grid layer rendered on top of image)
- [x] T068 [US3] Implement grid show/hide toggle in src/portrait_helper/gui/grid_config.py (checkbox updates GridConfiguration.visible)
- [x] T069 [US3] Implement grid size increase/decrease in src/portrait_helper/gui/grid_config.py (buttons update subdivision_count, enforce min/max)
- [x] T070 [US3] Implement grid color picker in src/portrait_helper/gui/grid_config.py (color dialog updates GridConfiguration.color)
- [x] T071 [US3] Update grid rendering on viewport changes in src/portrait_helper/gui/image_viewer.py (grid redraws on zoom/pan/resize)
- [x] T072 [US3] Ensure grid cells are always square in src/portrait_helper/grid/overlay.py (equal width/height subdivisions)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can load images, zoom/pan, and use grid overlay.

---

## Phase 6: User Story 2 - Zoom and Pan Image (Priority: P3)

**Goal**: Enable users to zoom in/out on images using mouse wheel and pan zoomed images by dragging.

**Independent Test**: Load an image, zoom in using mouse wheel, then pan the image by dragging. Reset zoom and verify it returns to fit-to-window.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T042 [P] [US2] Unit test for Viewport zoom calculations in tests/unit/test_viewport.py (zoom_in, zoom_out, set_zoom, min/max bounds)
- [x] T043 [P] [US2] Unit test for Viewport pan calculations in tests/unit/test_viewport.py (pan, constrain_pan, boundary checks)
- [x] T044 [P] [US2] Unit test for Viewport resize calculations in tests/unit/test_viewport.py (resize_window, display_size, visible_region)
- [x] T045 [P] [US2] Unit test for Viewport reset_zoom in tests/unit/test_viewport.py (reset to fit-to-window, centering)
- [x] T046 [US2] Integration test for zoom/pan interaction in tests/integration/test_zoom_pan.py (zoom centers on point, pan maintains position)
- [x] T047 [US2] Integration test for viewport resize interaction in tests/integration/test_zoom_pan.py (resize adjusts zoom/pan, aspect ratio maintained)

### Implementation for User Story 2

- [x] T048 [US2] Implement Viewport class methods in src/portrait_helper/image/viewport.py (set_zoom, zoom_in, zoom_out, pan, reset_zoom, resize_window, get_display_size, get_visible_region, constrain_pan)
- [x] T049 [US2] Implement CLI interface for viewport in src/portrait_helper/cli/viewport.py (calculate-viewport command)
- [x] T050 [US2] Integrate Viewport with ImageViewer in src/portrait_helper/gui/image_viewer.py (viewport state management)
- [x] T051 [US2] Implement mouse wheel zoom handler in src/portrait_helper/gui/image_viewer.py (wheelEvent for zoom in/out, centers on cursor)
- [x] T052 [US2] Implement mouse drag pan handler in src/portrait_helper/gui/image_viewer.py (mousePressEvent, mouseMoveEvent, mouseReleaseEvent for panning)
- [x] T053 [US2] Implement zoom gesture support in src/portrait_helper/gui/image_viewer.py (pinch-to-zoom for touch devices)
- [x] T054 [US2] Implement zoom limits enforcement in src/portrait_helper/image/viewport.py (MIN_ZOOM 0.1, MAX_ZOOM 10.0)
- [x] T055 [US2] Implement pan boundary constraints in src/portrait_helper/image/viewport.py (constrain_pan prevents panning beyond image)
- [x] T056 [US2] Update image rendering in src/portrait_helper/gui/image_viewer.py (paintEvent uses viewport calculations for visible region)
- [x] T057 [US2] Add reset zoom to context menu in src/portrait_helper/gui/context_menu.py (Reset Zoom option)
- [x] T058 [US2] Add keyboard shortcut for reset zoom in src/portrait_helper/gui/main_window.py (platform-aware shortcut)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can load images, zoom, and pan.

---


## Phase 7: User Story 4 - Black and White Filter (Priority: P4)

**Goal**: Enable users to toggle black/white (grayscale) filter on images while preserving zoom and pan state.

**Independent Test**: Load a color image, toggle black/white mode, verify grayscale display. Toggle off and verify color returns. Verify zoom/pan preserved.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T073 [P] [US4] Unit test for FilterState in tests/unit/test_filter.py (grayscale_enabled toggle, original_pixel_data preservation)
- [x] T074 [P] [US4] Unit test for grayscale filter application in tests/unit/test_filter.py (color to grayscale conversion, grayscale image handling)
- [x] T075 [US4] Integration test for filter toggle in tests/integration/test_image_pipeline.py (filter applies, toggles off, viewport state preserved)

### Implementation for User Story 4

- [x] T076 [US4] Implement FilterState class in src/portrait_helper/image/filter.py (grayscale_enabled, original_pixel_data, filtered_pixel_data attributes)
- [x] T077 [US4] Implement apply_grayscale_filter function in src/portrait_helper/image/filter.py (converts PIL.Image to grayscale)
- [x] T078 [US4] Implement toggle_grayscale method in src/portrait_helper/image/filter.py (applies/removes filter, caches result)
- [x] T079 [US4] Implement CLI interface for filter library in src/portrait_helper/cli/filter.py (apply-filter command with input image, filter type, output format)
- [x] T080 [US4] Add Toggle Black/White Mode to context menu in src/portrait_helper/gui/context_menu.py (menu option)
- [x] T081 [US4] Add keyboard shortcut for filter toggle in src/portrait_helper/gui/main_window.py (platform-aware shortcut)
- [x] T082 [US4] Integrate filter with ImageViewer in src/portrait_helper/gui/image_viewer.py (filter applied to displayed image)
- [x] T083 [US4] Ensure viewport state preserved on filter toggle in src/portrait_helper/gui/image_viewer.py (zoom/pan unchanged)

**Checkpoint**: All user stories should now be independently functional. Users can load images, zoom/pan, use grid overlay, and apply black/white filter.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T084 [P] Create context menu implementation in src/portrait_helper/gui/context_menu.py (right-click menu with all options)
- [x] T085 [P] Implement keyboard shortcuts for all menu functions in src/portrait_helper/gui/main_window.py (platform-aware shortcuts)
- [ ] T086 [P] Add structured logging throughout application in src/portrait_helper/image/loader.py, src/portrait_helper/image/viewport.py, src/portrait_helper/gui/
- [ ] T087 [P] Add error handling for edge cases in src/portrait_helper/gui/main_window.py (slow URLs, corrupted files, unsupported formats)
- [ ] T088 [P] Optimize image rendering performance in src/portrait_helper/gui/image_viewer.py (viewport culling, efficient repaints)
- [ ] T089 [P] Add performance monitoring in src/portrait_helper/gui/image_viewer.py (track load times, render times)
- [ ] T090 [P] Code cleanup and refactoring (review all files for consistency)
- [ ] T091 [P] Additional unit tests in tests/unit/ (edge cases, error conditions)
- [ ] T092 Run quickstart.md validation (verify all scenarios work)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **WebP Bug Fix (Phase 4)**: Depends on User Story 1 completion (needs ImageViewer widget) - CRITICAL bug fix
- **User Stories (Phase 5+)**: All depend on Foundational phase completion
  - User Story 2 depends on User Story 1 (ImageViewer widget)
  - User Story 3 depends on User Story 1 (ImageViewer) and User Story 2 (Viewport)
  - User Story 4 depends on User Story 1 (Image entity and ImageViewer)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **WebP Bug Fix**: Must complete after User Story 1 (Phase 3) - Fixes critical display bug
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 Image entity and ImageViewer widget
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 ImageViewer widget, US2 Viewport for alignment
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US1 Image entity and ImageViewer widget

### Within Each Phase

- Tests (REQUIRED) MUST be written and FAIL before implementation
- Investigation tasks before implementation tasks (for bug fix)
- Models/entities before services/libraries
- Libraries before GUI integration
- Core implementation before integration
- Phase complete before moving to next phase

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T006)
- All Foundational tasks marked [P] can run in parallel (T008-T010, T012)
- All test tasks for a phase marked [P] can run in parallel
- Investigation tasks for bug fix marked [P] can run in parallel (T035-T036)
- Models/entities within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (after dependencies met)

---

## Parallel Example: WebP Bug Fix

```bash
# Launch all test tasks for WebP bug fix together:
Task: "Unit test for WebP pixel alignment in tests/unit/test_image_viewer.py"
Task: "Unit test for _pil_to_qimage conversion in tests/unit/test_image_viewer.py"
Task: "Regression test for other formats in tests/contract/test_image_formats.py"

# Launch investigation tasks together:
Task: "Investigate PIL image properties for WebP in tests/unit/test_image_viewer.py"
Task: "Test PIL.ImageQt availability in src/portrait_helper/gui/image_viewer.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Bug Fix Priority

1. Complete Phase 1-3: Setup, Foundational, User Story 1
2. **Complete Phase 4: WebP Bug Fix** (CRITICAL - fixes display bug)
3. **STOP and VALIDATE**: Test WebP images display correctly
4. Proceed with additional user stories

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. **Fix WebP Bug → Test independently → Deploy/Demo (Bug Fix!)**
4. Add User Story 2 → Test independently → Deploy/Demo
5. Add User Story 3 → Test independently → Deploy/Demo
6. Add User Story 4 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (can start immediately)
3. Once User Story 1 is done:
   - Developer A: WebP Bug Fix (CRITICAL - must fix before proceeding)
   - Developer B: User Story 2 (waits for US1 ImageViewer)
4. Once Bug Fix is done:
   - Developer A: User Story 2 (if not already started)
   - Developer B: User Story 3 (waits for US1 ImageViewer + US2 Viewport)
   - Developer C: User Story 4 (waits for US1 ImageViewer)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- [BUGFIX] label indicates bug fix tasks (not tied to user story)
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All test tasks are REQUIRED per constitution (Test-First principle)
- WebP bug fix is CRITICAL and must be completed before proceeding with User Story 2
