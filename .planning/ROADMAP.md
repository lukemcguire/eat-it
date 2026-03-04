# Roadmap: Eat It

## Overview

Eat It delivers a privacy-first, self-hosted recipe management system with
local AI-powered search and collaborative shopping lists. The roadmap
progresses from foundation (database + schema) to recipe import/CRUD, then
semantic search, shopping lists, and finally mobile-optimized frontend with
Docker deployment. This ordering ensures schema decisions are locked in
before any feature code is written, avoiding the critical pitfall of late
schema changes.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation and Data Layer** - SQLite with WAL mode,
  sqlite-vec extension, Alembic migrations, and core SQLModel schemas
- [x] **Phase 2: Recipe Import and CRUD** - URL import with preview-before-save,
  manual entry, rating/notes, duplicate detection, keyword search, and data
  export
- [x] **Phase 3: Semantic Search** - Local embedding generation, sqlite-vec
  KNN search, and natural language query support
- [ ] **Phase 4: Shopping List** - Recipe-to-list generation, ingredient
  deduplication, manual editing, shareable links, and polling sync
- [ ] **Phase 5: Frontend and Deployment** - Mobile-optimized React SPA,
  Docker container, and self-hosting setup

## Phase Details

### Phase 1: Foundation and Data Layer
**Goal**: A stable database foundation with all schemas defined, enabling
future phases to build without schema rework.
**Depends on**: Nothing (first phase)
**Requirements**: ARCH-01, ARCH-02, ARCH-03
**Success Criteria** (what must be TRUE):
  1. Developer can create a new SQLite database with WAL mode and
     sqlite-vec extension loaded via a single Alembic migration
  2. Recipe schema exists with structured ingredient fields (quantity,
     unit, name, preparation, raw) and versioned metadata JSON field
  3. Shopping list schema exists with versioned metadata JSON field
  4. Settings table exists with embedding model name/version tracking
  5. FastAPI app starts with lifespan context that loads embedding model
     and initializes importer registry
**Plans**: 4 plans

- [x] 01-01-PLAN.md - Project setup and configuration
- [x] 01-02-PLAN.md - Database layer and SQLModel schemas
- [x] 01-03-PLAN.md - FastAPI application with lifespan
- [x] 01-04-PLAN.md - sqlite-vec extension loading (gap closure)

### Phase 2: Recipe Import and CRUD
**Goal**: Users can import recipes from URLs (with preview before save),
enter recipes manually, and perform full CRUD operations with export.
**Depends on**: Phase 1
**Requirements**: RECIPE-01, RECIPE-02, RECIPE-03, RECIPE-04, RECIPE-05,
  RECIPE-06, DATA-01
**Success Criteria** (what must be TRUE):
  1. User can paste a URL and see a preview of parsed recipe data before
     deciding to save
  2. User can manually enter or edit any recipe field when URL parsing
     fails or is unavailable
  3. User can add private notes and a rating (1-5 stars) to any saved recipe
  4. User sees a clear error message and manual-entry form when URL parsing
     fails completely
  5. User is warned when attempting to import a URL that already exists in
     their collection
  6. User can export all recipes as JSON or CSV from the application
**Plans**: 5 plans

- [x] 02-01-PLAN.md - Recipe model extensions (rating/notes, Pydantic schemas)
- [x] 02-02-PLAN.md - Recipe CRUD API (list, get, create, update, delete)
- [x] 02-03-PLAN.md - Recipe import/parse (URL parsing, duplicate detection)
- [x] 02-04-PLAN.md - Recipe annotations (rating/notes endpoints)
- [x] 02-05-PLAN.md - Recipe export (JSON/CSV download)

### Phase 3: Semantic Search
**Goal**: Users can find recipes using natural language queries powered by
local embeddings, with no internet or API key required.
**Depends on**: Phase 2
**Requirements**: SEARCH-01, SEARCH-02
**Success Criteria** (what must be TRUE):
  1. User can type a natural language query like "vegetarian dinner for 4"
     and receive relevant recipe results
  2. User can fall back to keyword or tag search when embedding search is
     unavailable or returns no results
  3. Search response time is under 1 second for collections up to several
     thousand recipes
  4. Embeddings are generated automatically when a recipe is saved or
     updated (background task)
**Plans**: 3 plans

- [x] 03-01-PLAN.md - Embedding infrastructure (vec0 table, service module)
- [x] 03-02-PLAN.md - Recipe CRUD embedding hooks (create/update)
- [x] 03-03-PLAN.md - Search endpoint (semantic + keyword fallback)

### Phase 4: Shopping List
**Goal**: Users can generate shopping lists from selected recipes and share
them with household members for collaborative grocery shopping.
**Depends on**: Phase 2
**Requirements**: SHOP-01, SHOP-02, SHOP-03, SHOP-04, SHOP-05, SHOP-06
**Success Criteria** (what must be TRUE):
  1. User can select one or more recipes and generate a shopping list with
     ingredients deduplicated and quantities summed
  2. User can add, remove, and edit items on a shopping list, including
     adjusting quantities
  3. User can check off items on a mobile-optimized list view with large
     tap targets (44px minimum)
  4. User can access the same shopping list from multiple devices on the
     same local network
  5. A second user can view and check off items from a shared shopping list
     (sync on page refresh)
  6. User can share a shopping list via a simple link or PIN without
     creating an account
**Plans**: 3 plans

- [ ] 04-01-PLAN.md - Store sections model and ingredient combining service
- [ ] 04-02-PLAN.md - Shopping list CRUD and generate endpoint
- [ ] 04-03-PLAN.md - WebSocket sync and shareable links

### Phase 5: Frontend and Deployment
**Goal**: Users can access the full application through a mobile-optimized
web interface and deploy it via Docker with minimal setup.
**Depends on**: Phase 3, Phase 4
**Requirements**: DATA-02
**Success Criteria** (what must be TRUE):
  1. User can access the application through a responsive web interface
     optimized for mobile devices
  2. Shopping list view displays large tap targets (44px minimum) suitable
     for one-handed use
  3. User can deploy the application via a single Docker container with
     minimal configuration
  4. Application data persists across container restarts via volume-mounted
     SQLite database
**Plans**: 4 plans

- [ ] 05-01-PLAN.md - Docker infrastructure (Dockerfile, docker-compose,
  StaticFiles)
- [ ] 05-02-PLAN.md - Frontend integration (TanStack Query, API hooks)
- [ ] 05-03-PLAN.md - Layout components (TouchButton, Header, BottomNav,
  Sidebar)
- [ ] 05-04-PLAN.md - AppLayout and routing (AppLayout wrapper, App.tsx)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Data Layer | 4/4 | Complete | 2026-02-25 |
| 2. Recipe Import and CRUD | 5/5 | Complete | 2026-02-25 |
| 3. Semantic Search | 3/3 | Complete | 2026-03-04 |
| 4. Shopping List | 0/3 | Not started | - |
| 5. Frontend and Deployment | 0/4 | Not started | - |

---
*Roadmap created: 2026-02-23*
*Depth: comprehensive*
