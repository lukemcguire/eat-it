# Project Research Summary

**Project:** eat-it
**Domain:** Self-hosted recipe management + collaborative shopping lists
**Researched:** 2026-02-23
**Confidence:** MEDIUM-HIGH

## Executive Summary

Eat It is a self-hosted household recipe manager with an AI-powered
semantic search capability and collaborative shopping list generation.
The pattern is well-established — multiple open-source competitors
(Mealie, Tandoor, KitchenOwl) exist — but none offer local-only
embedding-based search or a preview-before-save import flow. The
recommended approach is a FastAPI/SQLite backend with
sentence-transformers for CPU-local embeddings, sqlite-vec for vector
storage in the same database file, and a React/Vite/shadcn frontend
served from the same container. The existing stack choices are all
confirmed correct; the main gaps are in tooling decisions (Alembic,
SQLModel, sqlite-vec initialization) that must be resolved before
implementation begins.

The key architectural insight is that five subsystems must coexist
cleanly from day one: recipe CRUD, the importer plugin registry, the
embedding pipeline, the shopping list engine, and the sharing/sync
layer. The pitfall research strongly indicates that schema decisions
made late cause expensive migrations. Specifically, ingredient structure
(structured parse fields alongside raw strings), embedding storage
(database column + model version tracking), and WAL mode for SQLite
must all be in place before any recipe import code is written. Every
critical pitfall identified maps to "Phase 1 — schema design," which
means the foundation phase carries the highest risk.

The clearest differentiation opportunities are: (1) local AI search
with no API key or cloud dependency, (2) a preview-before-confirm
import flow that competitors all lack, and (3) shareable shopping list
links without mandatory account creation. These three features should
all ship in v1 to make the product meaningfully different from existing
options. Deferring any of them removes the reason to choose Eat It over
Mealie.

## Key Findings

### Recommended Stack

The existing technology choices are sound and confirmed against current
versions. FastAPI 0.132.0, React 19, Tailwind v4, shadcn/ui, SQLite,
sentence-transformers, and recipe-scrapers are all the correct choices
for this domain. The main gaps are tooling and wiring: SQLModel and
Alembic are required and not yet decided; sqlite-vec needs explicit
initialization; the embedding model must load at startup via FastAPI's
lifespan context, not per request; and CPU-only PyTorch must be
installed explicitly to avoid pulling a 2GB CUDA build onto a Raspberry
Pi. See [STACK.md](STACK.md) for full version table.

**Core technologies:**
- FastAPI 0.132.0: REST API — async, typed, auto-OpenAPI; confirmed
  current
- SQLModel 0.0.37: ORM and schema — merges Pydantic and SQLAlchemy,
  eliminates duplicate model definitions
- Alembic 1.18.4: migrations — required; use `render_as_batch=True`
  for SQLite ALTER support
- sentence-transformers 5.2.3 + all-MiniLM-L6-v2: local embeddings —
  no API key, CPU-capable, 384 dims, ~90MB RAM
- sqlite-vec 0.1.6: vector search — SQLite-native KNN, no separate
  process, pin version (pre-v1 API)
- recipe-scrapers 15.11.0: URL import — 611 sites, MIT license
- React 19 + Vite 7 + Tailwind v4 + shadcn/ui: frontend stack —
  all confirmed compatible with each other
- TanStack Query v5: server state — caching, background refetch,
  polling interval for shopping list sync

**Critical library warnings:**
- Do NOT use passlib (abandoned, Python 3.13 incompatible); use
  pwdlib[argon2]
- Do NOT use ChromaDB (separate process, RAM-heavy); use sqlite-vec
- Do NOT use default `pip install sentence-transformers` on Raspberry
  Pi (pulls CUDA); install CPU-only PyTorch first

### Expected Features

Three tiers emerge clearly from research. Table stakes are features
users assume exist. Differentiators are what make Eat It worth choosing.
Anti-features are things that sound appealing but add cost without
proportional value. See [FEATURES.md](FEATURES.md) for full prioritization
matrix and competitor analysis.

**Must have (table stakes):**
- URL recipe import with graceful failure fallback
- Manual recipe entry/edit (covers import failures and handwritten
  recipes)
- Recipe CRUD with rating and notes
- Keyword and tag search (baseline before AI search)
- Natural language semantic search via local embeddings — primary
  differentiator; without it the app is just Mealie with less polish
- Shopping list generation from selected recipes with ingredient
  deduplication
- Manual shopping list editing (add/remove/check-off)
- Mobile-optimized checklist view with large tap targets
- Multi-device access via refresh-to-sync polling (no websockets)
- Shareable list link or PIN without mandatory account creation
- Data export (JSON and CSV)
- Docker deployment via single container with volume-mounted SQLite
- Duplicate URL detection on import

**Should have (competitive differentiators):**
- Preview-before-save import flow — no competitor does this; prevents
  bad parses polluting the collection
- Plugin/provider pattern for importers — enables OCR and video parsers
  without rewrites; build from day one even if no external plugins ship
- Versioned `metadata: {}` JSON field on Recipe and ShoppingList models
  — zero schema cost now, prevents hacks later

**Defer (v1.x after validation):**
- Serving size scaling (multiply quantities by N) — most-requested
  competitor feature; add once core is validated
- Ingredient category grouping on shopping list
- PWA offline checklist caching
- Recipe collections / cookbooks

**Defer (v2+ after product-market fit):**
- OCR and video recipe import (slots into plugin architecture)
- Real-time collaborative editing (websockets)
- Meal planning calendar
- Nutritional calculations
- Native mobile apps

### Architecture Approach

The architecture is a standard layered monolith: React SPA over REST,
FastAPI API layer, service layer, and a unified SQLite database file
containing both ORM tables and sqlite-vec virtual tables. The five key
patterns are: (1) Importer Provider/Strategy pattern with a plugin
directory scanned at startup; (2) Embedding Pipeline with model loaded
once at startup via FastAPI lifespan; (3) Preview-Then-Confirm import
split across two API calls; (4) Polling-based multi-device list sync
using `?since=` timestamp filtering; (5) Single-container Docker
deployment with FastAPI serving the built React SPA. The architecture
research also provides an explicit build order that avoids blockers.
See [ARCHITECTURE.md](ARCHITECTURE.md) for component diagram, code
patterns, and full project structure.

**Major components:**
1. FastAPI API layer — route handling, request validation, auth;
   never accesses DB directly
2. Importer Registry — plugin discovery via directory scan,
   `ImporterBase` ABC, dispatch by URL domain
3. Embedding Pipeline — model loaded at startup via lifespan, encoding
   run in thread pool to avoid blocking async loop, results stored in
   sqlite-vec virtual table
4. Recipe Service — orchestrates import, embedding, and CRUD; the
   primary coordinator
5. Shopping List Service — ingredient aggregation, deduplication,
   quantity merging, polling sync
6. Data Layer — SQLAlchemy engine with WAL mode and sqlite-vec
   extension loaded at connection time, Alembic migrations

### Critical Pitfalls

All five critical pitfalls from research map to Phase 1 decisions.
There are no "later" pitfalls that can be deferred safely. See
[PITFALLS.md](PITFALLS.md) for full recovery strategies and gotcha
tables.

1. **Embedding index out of sync with database** — Store embeddings in
   the database (not a flat file), record model name/version in a
   settings table, regenerate on recipe update/delete, expose
   `POST /admin/reindex`
2. **SQLite locked under concurrent Docker writes** — Enable WAL mode
   and `busy_timeout=5000` at engine creation; use named Docker volumes
   (not bind-mounts to macOS/Windows host); single-writer connection
   pool
3. **recipe-scrapers partial parse treated as success** — Validate all
   required fields post-parse; classify as SUCCESS, PARTIAL, or FAILURE;
   never auto-save; always show preview screen
4. **Ingredient text stored as raw strings blocks aggregation** — Define
   structured ingredient model (quantity, unit, name, preparation, raw)
   from day one; parse at import time with ingredient-parser-py; store
   both raw and structured fields
5. **Plugin directory scan crashes startup on bad plugin** — Wrap each
   plugin load in try/except; skip and log bad plugins; validate
   against ImporterBase ABC at registration time

## Implications for Roadmap

Based on combined research, the natural phase structure follows the
architecture build order exactly. The dependency chain is clear: DB
before models, models before services, services before API, API before
frontend. Shopping list is independent of search but depends on recipe
storage. Frontend can be developed in parallel from Phase 2 onward.

### Phase 1: Foundation and Data Layer

**Rationale:** All critical pitfalls require Phase 1 decisions. Schema
is the hardest to change later. WAL mode and structured ingredients
must exist before any recipe code is written. This phase has no
shortcuts.
**Delivers:** SQLite database with WAL mode, sqlite-vec extension
loaded, Alembic migrations configured, SQLModel recipe and ingredient
schemas (including structured ingredient fields and metadata JSON),
embedding model version tracking, FastAPI app skeleton with lifespan
context loading embedding model and importer registry.
**Addresses:** Recipe CRUD foundation, duplicate detection schema,
versioned metadata field
**Avoids:** All five critical pitfalls; schema lock-in for ingredients
and embeddings

### Phase 2: Recipe Import and CRUD

**Rationale:** Recipe storage must work before any downstream feature
(search, shopping list, export). Import is the primary user entry point
and the first differentiator (preview-before-save).
**Delivers:** URL import with ImporterRegistry + recipe-scrapers
adapter, preview-before-confirm API flow, manual recipe entry and
editing, rating and notes, duplicate URL detection, keyword and tag
search, data export.
**Uses:** recipe-scrapers 15.11.0, ImporterBase ABC, plugin directory
scanning with error isolation, httpx async HTTP client with User-Agent
and SSRF validation
**Implements:** Importer Registry pattern, Preview-Then-Confirm pattern,
Recipe Service

### Phase 3: Semantic Search

**Rationale:** Search depends on recipe storage and the embedding
pipeline. It is the primary technical differentiator and must ship in v1
to justify the product. Background task embedding prevents blocking
import.
**Delivers:** Embedding generation as FastAPI BackgroundTask on recipe
save/update/delete, sqlite-vec KNN search endpoint, keyword search
fallback when embedding unavailable, admin reindex endpoint, first-query
pre-warm on startup.
**Uses:** sentence-transformers all-MiniLM-L6-v2 (CPU-only PyTorch),
sqlite-vec virtual table, FastAPI BackgroundTasks
**Implements:** Embedding Pipeline pattern with lazy load + startup
pre-warm

### Phase 4: Shopping List

**Rationale:** Shopping list is the second core value proposition and
depends on recipe storage being stable. It is independent of semantic
search.
**Delivers:** Shopping list generation from selected recipes, ingredient
normalization and quantity merging (structured fields from Phase 1 make
this tractable), manual list editing (add/remove/check-off), server-side
check-off persistence, shareable list link via UUID/random token, polling
sync with `?since=` timestamp.
**Uses:** ShoppingListService, ingredient-parser-py normalization,
`secrets.token_urlsafe` for share tokens
**Implements:** Polling-Based Multi-Device List Sync pattern

### Phase 5: Mobile-Optimized Frontend and Deployment

**Rationale:** Frontend can be built in parallel from Phase 2 onward
using mock API data, but the full mobile-optimized experience and Docker
deployment are integration concerns that belong at the end once the API
is stable.
**Delivers:** React SPA with mobile-first checklist view (44px tap
targets, dvh viewport handling), large-target check-off, Docker
multi-stage build (node build + python runtime), docker-compose with
named volume for SQLite, FastAPI SPAStaticFiles mount.
**Uses:** React 19, Vite 7, Tailwind v4, shadcn/ui, TanStack Query v5
(polling interval), react-router-dom, react-hook-form, zod
**Implements:** Single-container Docker pattern

### Phase Ordering Rationale

- Schema-first ordering reflects the research finding that all critical
  pitfalls require Phase 1 schema decisions; there are no safe deferred
  schema choices in this domain.
- Import before search because embedding is generated as a background
  task on save — recipes must exist before embeddings can be built.
- Search before shopping list because both are independent of each other
  but search is the primary differentiator and should be validated
  earlier.
- Frontend last for integration, but it should be developed in parallel
  from Phase 2 onward against mock/stub API responses to avoid blocking.
- Plugin registry is built in Phase 2 alongside the first importer,
  validating the extension pattern before more importers are needed.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Semantic Search):** sqlite-vec is pre-v1 with stated
  breaking-change policy; verify current API shape and confirm ARM64
  wheel availability before writing vec table migration
- **Phase 4 (Shopping List):** Ingredient normalization accuracy is
  domain-specific; evaluate ingredient-parser-py against real recipe
  data before committing to the parsing approach; plan for ~20% null
  structured fields on first import

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** SQLModel + Alembic + WAL setup is
  well-documented with official sources; follow STACK.md patterns
  directly
- **Phase 5 (Frontend/Docker):** React/Vite/Tailwind/shadcn/ui stack
  is standard; Docker multi-stage build pattern is well-documented
  in FastAPI official docs

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core choices verified against PyPI current versions and official docs |
| Features | MEDIUM-HIGH | Competitor analysis from official docs + community surveys; user pain points from multiple sources |
| Architecture | MEDIUM-HIGH | Standard patterns verified against official FastAPI/SQLite docs; sqlite-vec pre-v1 is the uncertainty |
| Pitfalls | MEDIUM | Domain-specific findings verified across multiple sources; some from community discussions |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **CPU-only PyTorch install:** Must be handled explicitly in Dockerfile
  before `pip install sentence-transformers`. Failure means a ~2GB CUDA
  download on Raspberry Pi build. Confirm approach during Phase 3
  planning.
- **sqlite-vec ARM64 wheel:** Pre-built wheels for Raspberry Pi ARM64
  exist as of 0.1.6 but are not guaranteed for future versions. Pin
  version in pyproject.toml; verify wheel at Phase 3 start.
- **Ingredient parser accuracy:** ingredient-parser-py provides ~80%
  accuracy on typical recipe ingredient strings. The 20% unparseable
  rate must be handled gracefully (store null structured fields, display
  raw). Validate on a sample of real import data before committing.
- **Model download at Docker build time:** The sentence-transformers
  model (~90MB) must be baked into the Docker image or volume-mounted,
  not downloaded at runtime on Raspberry Pi. Decide approach during
  Phase 3 Docker design.
- **Shopping list sync strategy:** TanStack Query `refetchInterval` for
  polling is the recommended approach. Confirm interval (5-10 seconds)
  is acceptable UX for the co-shopper scenario before implementing.
- **Auth scope:** PROJECT.md mentions a simple admin PIN/password
  approach. Confirm this is sufficient before Phase 1 (auth schema
  affects user/session model if it exists).

## Sources

### Primary (HIGH confidence)
- PyPI: FastAPI 0.132.0 — https://pypi.org/project/fastapi/
- PyPI: sentence-transformers 5.2.3 —
  https://pypi.org/project/sentence-transformers/
- PyPI: recipe-scrapers 15.11.0 —
  https://pypi.org/project/recipe-scrapers/
- PyPI: SQLModel 0.0.37 — https://pypi.org/project/sqlmodel/
- PyPI: Alembic 1.18.4 — https://pypi.org/project/alembic/
- FastAPI official docs (background tasks, Docker, security, SQL) —
  https://fastapi.tiangolo.com/
- SQLite WAL mode official docs — https://sqlite.org/wal.html
- sentence-transformers official docs — https://sbert.net/
- shadcn/ui Tailwind v4 docs — https://ui.shadcn.com/docs/tailwind-v4
- Alembic batch migrations — https://alembic.sqlalchemy.org/en/latest/batch.html
- TanStack Query v5 — https://tanstack.com/query/v5/docs/

### Secondary (MEDIUM confidence)
- sqlite-vec stable release and GitHub —
  https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html
- Mealie official docs and 2024 user survey —
  https://docs.mealie.io/
- Tandoor Recipes GitHub — https://github.com/TandoorRecipes/recipes
- KitchenOwl features — https://kitchenowl.org/features/
- Python plugin systems —
  https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
- SQLite concurrent writes pitfalls —
  https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/
- DagShub vector database pitfalls —
  https://dagshub.com/blog/common-pitfalls-to-avoid-when-using-vector-databases/

### Tertiary (MEDIUM-LOW confidence)
- Hacker News Mealie discussion (community pain points) —
  https://news.ycombinator.com/item?id=30623852
- Lemmy/SDF self-hosted recipe manager suggestions —
  https://lemmy.sdf.org/post/351462
- PWA iOS Safari limitations —
  https://brainhub.eu/library/pwa-on-ios

---
*Research completed: 2026-02-23*
*Ready for roadmap: yes*
