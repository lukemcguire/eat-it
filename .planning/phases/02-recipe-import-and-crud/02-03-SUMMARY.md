---
phase: 02-recipe-import-and-crud
plan: 03
subsystem: api
tags: [recipe-scrapers, httpx, url-parsing, duplicate-detection, error-handling]

# Dependency graph
requires:
  - phase: 02-01
    provides: Recipe model with source_url field and RecipePublic schema
provides:
  - RecipeParser service for URL parsing with error handling
  - GET /recipes/parse endpoint with duplicate detection
  - Structured error responses with suggested actions
affects: [02-04, 02-05]

# Tech tracking
tech-stack:
  added: [recipe-scrapers>=15.11.0, httpx>=0.28.1]
  patterns: [async URL fetching, wild-mode parsing, error code enums]

key-files:
  created:
    - src/eat_it/services/recipe_parser.py
    - tests/test_recipe_parse.py
  modified:
    - src/eat_it/routers/recipes.py
    - src/eat_it/schemas/recipe.py
    - tests/conftest.py
    - pyproject.toml

key-decisions:
  - "Use recipe-scrapers wild mode (supported_only=False) for any website support"
  - "Check duplicates at parse time, not save time, for early user feedback"
  - "Add from_attributes=True to RecipePublic for SQLModel validation"

patterns-established:
  - "ParseErrorCode enum for structured error types"
  - "ParseResult dataclass for success/error responses"
  - "ParseError with suggested_action for user guidance"

requirements-completed: [RECIPE-01, RECIPE-04, RECIPE-05, RECIPE-06]

# Metrics
duration: 10min
completed: 2026-02-25
---

# Phase 2 Plan 3: URL Recipe Parsing Summary

**URL recipe parsing with recipe-scrapers wild mode, structured error responses,
and duplicate detection at parse time**

## Performance

- **Duration:** 10 min
- **Started:** 2026-02-25T23:41:40Z
- **Completed:** 2026-02-25T23:52:18Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Added recipe-scrapers and httpx dependencies for URL parsing
- Created RecipeParser service with async parse_url method using wild mode
- Added GET /recipes/parse endpoint with duplicate URL detection
- Implemented structured error responses with suggested actions for users
- Added comprehensive tests for all parsing scenarios

## Task Commits

Each task was committed atomically:

1. **Task 1: Add dependencies** - `1074d1e` (feat)
2. **Task 2: Create RecipeParser service** - `15ce506` (feat)
3. **Task 3: Add /parse endpoint** - `360fb88` (feat)
4. **Task 4: Add tests** - `56d2b3f` (feat)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified

- `pyproject.toml` - Added recipe-scrapers and httpx dependencies
- `uv.lock` - Lockfile updated with new dependencies
- `src/eat_it/services/recipe_parser.py` - RecipeParser service with
  ParseErrorCode, ParseError, ParseResult classes
- `src/eat_it/routers/recipes.py` - Added /parse endpoint with duplicate
  detection
- `src/eat_it/schemas/recipe.py` - Added ConfigDict(from_attributes=True) to
  RecipePublic
- `tests/conftest.py` - Fixed SQLite shared cache mode for thread-safe tests
- `tests/test_recipe_parse.py` - 5 tests for parse endpoint scenarios

## Decisions Made

- Used recipe-scrapers wild mode (supported_only=False) to attempt parsing any
  website with schema.org data
- Duplicate detection at parse time (not save time) provides early feedback
  before user commits to saving
- Error responses include suggested_action field for user guidance
- Added from_attributes=True to RecipePublic to support SQLModel instance
  validation

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed SQLite thread-safety for TestClient**

- **Found during:** Task 4 (Add tests for /parse endpoint)
- **Issue:** TestClient runs in thread pool, but SQLite in-memory databases are
  connection-specific, causing "no such table" errors
- **Fix:** Changed test_engine fixture to use shared cache mode
  (`sqlite:///file::memory:?cache=shared&uri=true`) with
  `check_same_thread=False`
- **Files modified:** tests/conftest.py
- **Verification:** All 5 tests pass
- **Committed in:** 56d2b3f (Task 4 commit)

**2. [Rule 1 - Bug] Fixed RecipePublic validation error**

- **Found during:** Task 4 (Add tests for /parse endpoint)
- **Issue:** RecipePublic.model_validate(existing_recipe) failed because
  RecipePublic didn't have from_attributes=True for SQLModel validation
- **Fix:** Added `model_config = ConfigDict(from_attributes=True)` to
  RecipePublic schema
- **Files modified:** src/eat_it/schemas/recipe.py
- **Verification:** test_parse_duplicate_warning passes
- **Committed in:** 56d2b3f (Task 4 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Both fixes necessary for test infrastructure and proper
model validation. No scope creep.

## Issues Encountered

- Initial test failures due to SQLite in-memory database thread isolation -
  resolved with shared cache mode
- Pydantic v2 model validation requires from_attributes=True for ORM model
  conversion - added to RecipePublic

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- URL parsing infrastructure complete, ready for recipe import workflow
- /parse endpoint provides preview-before-save flow for frontend integration
- Error handling guides users toward manual entry when parsing fails

---

*Phase: 02-recipe-import-and-crud*
*Completed: 2026-02-25*

## Self-Check: PASSED

- All created files exist
- All commit hashes verified
