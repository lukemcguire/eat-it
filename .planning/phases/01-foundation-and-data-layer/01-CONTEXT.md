# Phase 1: Foundation and Data Layer - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish SQLite database with WAL mode and sqlite-vec extension, define all
core schemas (Recipe, Shopping List, Settings), and create FastAPI app
structure with importer registry. This phase delivers the data layer and
application skeleton that all future phases build upon. No user-facing
features—pure infrastructure.

</domain>

<decisions>
## Implementation Decisions

### Ingredient Schema

- Five-field structured model: `quantity`, `unit`, `name`, `preparation`,
  `raw`
- `unit` can be null for unit-less ingredients ("salt to taste")
- `raw` stores the original unparsed string for reference
- Unit conversion is deferred to Phase 4 (shopping list phase)—store as-is
  for now, add normalization layer later when aggregating shopping lists

### Ingredient Groups

- Nested structure: recipe has ingredient groups, each containing
  ingredients
- Groups have a `name` (e.g., "For the sauce:") and an `ingredients` array
- This preserves recipe hierarchy even if v1 doesn't display groups
  prominently

### Recipe Schema Fields

- Standard set: `title`, `description`, `ingredients` (nested groups),
  `instructions`, `prep_time`, `cook_time`, `servings`, `source_url`,
  `image_url`, `tags`
- Timestamps: `created_at` and `updated_at` on all tables

### Shopping List Schema

- Simple relationship: List → Items
- Items are generated from recipes but become independent (no back-link to
  source recipe)
- Item fields: `name`, `quantity`, `unit`, `checked` status

### Database & Storage

- Location: `./data/eat-it.db` (project-relative, works with Docker volume
  mounts)
- Deletes: Hard deletes—self-hosted means users own their data and can
  re-import if needed
- Timestamps: `created_at` + `updated_at` on all tables

### Importer Registry & Plugin Architecture

- Registry pattern: importers register themselves via entry points
- App calls `registry.parse(url)` — simple, testable, allows runtime
  registration
- Plugin discovery via Python entry_points (user uses `uv` for package
  management, not pip)

### Configuration

- Environment variables only (12-factor app style)
- Examples: `EAT_IT_DATABASE_URL`, `EAT_IT_EMBEDDING_MODEL`

### Embedding Model

- Default: `all-MiniLM-L6-v2` from sentence-transformers
- Model name and version tracked in Settings table
- Eager load at app startup (in lifespan context)
- Fully configurable via environment

### FastAPI Application Structure

- Modular routers (separate routers for recipes, shopping lists, etc.)
- Lifespan context handles: database initialization, embedding model
  loading, importer registry setup
- Structured JSON error responses with error codes, messages, and details

### Testing Strategy

- In-memory SQLite (`:memory:`) per test for isolation
- Fast, no cleanup needed, each test gets fresh database

### Claude's Discretion

- Alembic migration organization (single vs multiple migrations)
- Settings table structure (key-value vs typed columns)
- Versioned metadata field structure (keep minimal—just version number
  and empty object)
- Exact indexing strategy
- Lifespan context implementation details

</decisions>

<specifics>
## Specific Ideas

- "There's going to need to be some way to convert between different units.
  For example, 1 cup sugar = 200 grams. This is critical for shopping list
  aggregation—defer to Phase 4."
- "Building in room to grow is smart. For ingredient groups, we don't need
  to use all that info initially, but at least the schema is there."
- User uses `uv` for package management (not pip)—entry points must work
  with `uv`

</specifics>

<deferred>
## Deferred Ideas

None—discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation-and-data-layer*
*Context gathered: 2026-02-23*
