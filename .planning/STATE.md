# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-23)

**Core value:** All your recipes and shopping lists live on your own hardware,
searchable in plain English, with no ads, no accounts required, and no data
leaving your network.
**Current focus:** Phase 3 (Semantic Search) - In Progress

## Current Position

Phase: 3 of 5 (Semantic Search) - IN PROGRESS
Plan: 2 of 4 in current phase
Status: Completed 03-02 Recipe CRUD Embedding Hooks
Last activity: 2026-03-04 — Completed 03-02 Recipe CRUD Embedding Hooks

Progress: [====----] 50%

## Performance Metrics

**Velocity:**
- Total plans completed: 11
- Average duration: 14 min
- Total execution time: 2.31 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation | 4 | 95min | 24min |
| 2. Recipe Import | 5 | 39min | 8min |
| 3. Semantic Search | 2 | 10min | 5min |
| 4. Shopping List | 0 | TBD | - |
| 5. Frontend/Deploy | 0 | TBD | - |

**Recent Trend:**
- Last 5 plans: 02-03 (10min), 02-04 (12min), 02-05 (2min), 03-01 (5min), 03-02 (5min)
- Trend: Phase 3 in progress

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [02-03]: Use recipe-scrapers wild mode (supported_only=False) for any website support
- [02-03]: Check duplicates at parse time, not save time, for early user feedback
- [02-03]: Add from_attributes=True to RecipePublic for SQLModel validation
- [02-04]: Dedicated annotation endpoints for rating/notes following RESTful PATCH semantics
- [02-01]: Add rating (1-5 int) and notes (text) as nullable fields to Recipe
- [02-01]: Create separate RecipeRatingUpdate and RecipeNotesUpdate schemas per CONTEXT.md
- [01-04]: Import sqlite_vec inside function to keep dependency localized
- [01-04]: Use try/finally for raw_connection cleanup (context manager not
  supported)
- [01-03]: Use importlib.metadata.entry_points for plugin discovery
- [01-03]: Store initialized components in app.state for request access
- [01-03]: Eager load embedding model at startup for faster queries
- [01-02]: Use metadata_ as field name since SQLAlchemy reserves metadata
- [01-02]: Single initial migration for all Phase 1 tables
- [01-02]: Key-value Settings table with JSON values for flexibility
- [01-02]: In-memory SQLite (:memory:) for test isolation
- [01-01]: Use pydantic-settings with EAT_IT_ prefix for environment vars
- [01-01]: Provide both settings global and get_settings() for compatibility
- [Roadmap]: Phase ordering follows research recommendations (schema-first
  approach to avoid critical pitfalls)
- [Roadmap]: DATA-01 (export) assigned to Phase 2 alongside Recipe CRUD
  for coherent data management
- [Roadmap]: Phase 5 depends on both Phase 3 and Phase 4 (frontend
  integrates all features)
- [Phase 02]: Prefix defined in include_router only, not in APIRouter
- [Phase 02]: Use StaticPool for test database to handle thread pool
- [Phase 02]: No-op lifespan for tests to avoid loading embedding model
- [Phase 02-05]: CSV escapes newlines as \n and joins tags with | for safe parsing
- [03-02]: Generate embeddings before commit for transactional consistency
- [03-02]: Use session.flush() to get recipe ID before embedding insert
- [03-02]: Set embedding_model=None in conftest client for existing tests

### Pending Todos

None yet.

### Blockers/Concerns

From research SUMMARY.md - Phase 3 and Phase 4 flags:

- **Phase 3 (Semantic Search):** sqlite-vec is pre-v1 with stated breaking-change
  policy; verify current API shape and confirm ARM64 wheel availability before
  writing vec table migration
- **Phase 4 (Shopping List):** Ingredient normalization accuracy is domain-specific;
  evaluate ingredient-parser-py against real recipe data before committing to
  the parsing approach; plan for ~20% null structured fields on first import

## Session Continuity

Last session: 2026-03-04
Stopped at: Completed 03-02 Recipe CRUD Embedding Hooks
Resume file: .planning/phases/03-semantic-search/03-03-PLAN.md
