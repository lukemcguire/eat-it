# Stack Research

**Domain:** Self-hosted recipe management + shopping list web app
**Researched:** 2026-02-23
**Confidence:** HIGH (core stack verified via PyPI + official docs)

## Validation of Existing Decisions

The project has made the following stack choices. All are confirmed correct:

| Decision | Verdict | Notes |
|----------|---------|-------|
| FastAPI backend | CONFIRMED | v0.132.0 current; ideal for this use case |
| React + Vite + Tailwind + shadcn/ui | CONFIRMED | All Tailwind v4 + React 19 compatible |
| SQLite | CONFIRMED | Right fit for household scale, Raspberry Pi |
| sentence-transformers | CONFIRMED | v5.2.3 current; use all-MiniLM-L6-v2 |
| recipe-scrapers | CONFIRMED | v15.11.0 current; 611 sites supported |

**Gaps identified (not yet decided):**
- ORM / schema layer (SQLModel recommended)
- Migration tool (Alembic required)
- Vector storage (sqlite-vec recommended)
- Auth approach (pwdlib + python-jose)
- Job handling for embedding generation
- Frontend data fetching (TanStack Query recommended)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.13 | Runtime | Already configured; all deps support it |
| FastAPI | 0.132.0 | REST API | Official docs updated for this version; async, typed, auto-OpenAPI |
| Uvicorn | 0.34+ | ASGI server | Standard FastAPI server; single-worker sufficient for ≤10 users |
| SQLModel | 0.0.37 | ORM + schema | Same author as FastAPI; merges Pydantic + SQLAlchemy into one model, eliminates duplicate schema definitions |
| Alembic | 1.18.4 | DB migrations | Industry standard for SQLAlchemy-backed apps; required to evolve schema safely; use `render_as_batch=True` for SQLite |
| sentence-transformers | 5.2.3 | Local embeddings | State-of-art sentence embeddings, no API key, runs on CPU |
| sqlite-vec | 0.1.6 | Vector search | SQLite-native KNN search; no external vector DB needed; atomic with SQLite transactions |
| recipe-scrapers | 15.11.0 | Recipe parsing | 611 sites supported; Schema.org + JSON-LD aware; MIT license |
| React | 19.2.4 | Frontend UI | Largest ecosystem; TypeScript-first; shadcn/ui requires React |
| Vite | 7.x | Build tool | Fastest HMR for React+TS; native ESM; replaces CRA |
| Tailwind CSS | 4.x | Styling | CSS-first config in v4; no tailwind.config.js; @tailwindcss/vite plugin |
| shadcn/ui | latest | Component library | All components updated for Tailwind v4 + React 19; mobile-first |
| TypeScript | 5.x | Type safety | Required by shadcn/ui; catches API contract bugs |

### Supporting Libraries — Backend

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-jose[cryptography] | 3.5.0 | JWT encoding/decoding | Auth token generation + validation |
| pwdlib[argon2] | 0.3.0 | Password hashing | Replace passlib; Argon2 is memory-hard, safer than bcrypt |
| python-multipart | 0.0.20+ | Form/file parsing | Required by FastAPI for any form or upload endpoint |
| httpx | 0.28+ | Async HTTP client | For scraping recipe URLs in async context; also FastAPI test client |
| pydantic-settings | 2.x | Config management | Load .env into typed Pydantic models; replaces manual os.environ |

### Supporting Libraries — Frontend

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query | 5.x | Server state management | Caching, background refetch, loading/error states for API calls |
| react-router-dom | 6.x | Client-side routing | SPA routing between recipe list, detail, shopping list views |
| react-hook-form | 7.x | Form management | Recipe edit forms, shopping list item editing; integrates with zod |
| zod | 3.x | Runtime validation | Frontend schema validation matching Pydantic backend models |
| lucide-react | latest | Icons | Used by shadcn/ui; consistent icon set |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Ruff 0.15.1+ | Lint + format | Already configured; keep existing setup |
| pytest + pytest-asyncio | Test backend | Already configured; add httpx as async test client |
| Vitest | Test frontend | Pairs with Vite; replaces Jest for this stack |
| Docker + Docker Compose | Container deployment | Single-container pattern: FastAPI serves static frontend build |

---

## Installation

```bash
# Backend — production
pip install fastapi[standard] sqlmodel alembic \
  sentence-transformers sqlite-vec recipe-scrapers \
  python-jose[cryptography] pwdlib[argon2] \
  python-multipart httpx pydantic-settings

# Frontend — scaffold
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query react-router-dom \
  react-hook-form zod lucide-react
npx shadcn@latest init

# Frontend — dev deps
npm install -D vitest @testing-library/react
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| SQLModel | SQLAlchemy (direct) | If you need complex query control or SQLModel's double-model limitation becomes a problem in large codebases |
| SQLModel | Tortoise ORM | If you prefer a Django-style async ORM; less FastAPI integration |
| sqlite-vec | ChromaDB | If you outgrow SQLite or want a dedicated embedding store with rich metadata filtering |
| sqlite-vec | pgvector + PostgreSQL | If you scale beyond household use and need multi-writer support |
| pwdlib[argon2] | bcrypt directly | If you specifically need bcrypt and don't want a wrapper layer |
| FastAPI BackgroundTasks | ARQ | If embedding jobs take >30s or you need job status tracking in UI |
| Uvicorn (single worker) | Gunicorn + Uvicorn workers | If you deploy to multi-core cloud instead of single Raspberry Pi |
| Vite 7 | Next.js | If you need SSR or SSG; overkill for a self-hosted SPA |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| passlib | No releases since 2020; incompatible with Python 3.13 (`crypt` module removed); FastAPI docs dropped it | pwdlib[argon2] |
| Celery | Requires Redis/RabbitMQ broker; overkill for a single-household app; adds operational complexity | FastAPI BackgroundTasks for <30s jobs; ARQ if job tracking needed |
| ChromaDB | Runs a separate server process; requires more RAM than Raspberry Pi may have | sqlite-vec (SQLite extension, no separate process) |
| OpenAI / Anthropic embeddings API | Violates the privacy-first, offline-capable requirement | sentence-transformers (local CPU inference) |
| Flask | Lacks async support, auto-validation, and OpenAPI generation that FastAPI provides | FastAPI (already decided) |
| Create React App | Abandoned/deprecated; slow; replaced by Vite ecosystem | Vite (already decided) |
| Tailwind CSS v3 | shadcn/ui components now shipped for v4; CSS-first config is cleaner | Tailwind CSS v4 |
| all-mpnet-base-v2 (768d) | 2x larger than needed; slower on Raspberry Pi ARM; 768-dim vectors use more storage | all-MiniLM-L6-v2 (384d) — sufficient quality for recipe search |

---

## Stack Patterns by Variant

**For embedding generation (recipe import):**
- Use FastAPI `BackgroundTasks` — embedding a single recipe takes ~1-3s on CPU
- Do NOT block the HTTP response; return the recipe immediately, embed async
- Store `embedding_status: pending | ready` on the recipe row

**For the embedding model itself:**
- Use `all-MiniLM-L6-v2` (22M params, 384 dims, ~80MB download)
- L6 vs L12: L6 is adequate for recipe semantics; L12 is ~30% slower for
  marginal quality gain in this domain — not worth it on Raspberry Pi
- Load model once at startup in a FastAPI lifespan context; do NOT reload
  per request (model load is 2-5s)

**For SQLite in production:**
- Enable WAL mode: `PRAGMA journal_mode=WAL` at startup — allows concurrent
  reads during writes; critical for multi-device shopping list access
- Set `PRAGMA synchronous=NORMAL` for write performance on Raspberry Pi SD
  card without data loss risk
- sqlite-vec and WAL mode are compatible

**For Docker deployment (single-container):**
- Build React frontend (`npm run build`) into FastAPI's `static/` directory
- FastAPI serves the SPA at `/` and API at `/api/`
- Mount SQLite DB file as a Docker volume at `/data/eat-it.db`
- Single container = minimal Raspberry Pi memory overhead

**For auth (household use, no mandatory accounts):**
- Use a simple env-var-configured admin PIN or password
- python-jose + pwdlib for token-based session (no full user database needed)
- Shopping lists shared via generated link/PIN per PROJECT.md requirement

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| SQLModel 0.0.37 | SQLAlchemy 2.x, Pydantic v2 | Requires both; installs them automatically |
| Alembic 1.18.4 | SQLAlchemy 2.x | render_as_batch=True required for SQLite ALTER |
| sentence-transformers 5.2.3 | Python 3.10-3.13, PyTorch 1.11+ | CPU-only install: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| sqlite-vec 0.1.6 | SQLite 3.x, Python 3.x | Pre-built ARM64 wheels available for Raspberry Pi |
| FastAPI 0.132.0 | Pydantic v2, Python 3.10+ | `fastapi[standard]` installs uvicorn + CLI |
| shadcn/ui latest | Tailwind CSS v4, React 19 | CSS-first config; no tailwind.config.js |
| Tailwind CSS v4 | Vite 7 via @tailwindcss/vite | PostCSS plugin approach deprecated in v4 |
| pwdlib 0.3.0 | Python 3.10+ | Beta status; API stable but watch for 1.0 breaking changes |

---

## Gaps the Project Has Not Yet Addressed

These decisions must be made before implementation begins:

1. **Database migration tool**: Alembic is required. Without it, schema
   changes require manual SQLite file manipulation.

2. **Embedding model loading strategy**: The sentence-transformers model
   must be loaded once at startup (FastAPI `lifespan` context), not per
   request. Failure to do this means 2-5s cold start on every search.

3. **CPU-only PyTorch**: The default `pip install sentence-transformers`
   pulls in CUDA PyTorch (~2GB). For Raspberry Pi, explicitly install
   CPU-only PyTorch first.

4. **sqlite-vec initialization**: Must call `sqlite_vec.load(conn)` after
   opening the SQLite connection. This is not automatic.

5. **Frontend build pipeline integration**: Decide whether the Docker build
   runs `npm run build` inside the image (single Dockerfile) or whether
   frontend is pre-built. Single Dockerfile is simpler for self-hosters.

6. **Shopping list sync strategy**: PROJECT.md specifies "sync on refresh,
   no websockets in MVP." TanStack Query's `refetchInterval` handles this
   without websockets — confirm this is the approach.

---

## Sources

- PyPI: recipe-scrapers 15.11.0 — https://pypi.org/project/recipe-scrapers/
- PyPI: sentence-transformers 5.2.3 — https://pypi.org/project/sentence-transformers/
- PyPI: sqlite-vec 0.1.6 — https://pypi.org/project/sqlite-vec/
- PyPI: SQLModel 0.0.37 — https://pypi.org/project/sqlmodel/
- PyPI: FastAPI 0.132.0 — https://pypi.org/project/fastapi/
- PyPI: Alembic 1.18.4 — https://pypi.org/project/alembic/
- PyPI: pwdlib 0.3.0 — https://pypi.org/project/pwdlib/
- PyPI: python-jose 3.5.0 — https://pypi.org/project/python-jose/
- shadcn/ui Tailwind v4 docs — https://ui.shadcn.com/docs/tailwind-v4
- FastAPI SQL Databases — https://fastapi.tiangolo.com/tutorial/sql-databases/
- FastAPI Docker deployment — https://fastapi.tiangolo.com/deployment/docker/
- FastAPI security/OAuth2-JWT — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- FastAPI background tasks — https://fastapi.tiangolo.com/tutorial/background-tasks/
- sqlite-vec stable release post — https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html
- TanStack Query v5 docs — https://tanstack.com/query/v5/docs/framework/react/overview
- FastAPI discussion: passlib deprecation — https://github.com/fastapi/fastapi/discussions/11773
- Alembic + FastAPI guide — https://blog.greeden.me/en/2025/08/12/no-fail-guide-getting-started-with-database-migrations-fastapi-x-sqlalchemy-x-alembic/
- HuggingFace all-MiniLM-L6-v2 — https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

---
*Stack research for: self-hosted recipe + shopping list app (eat-it)*
*Researched: 2026-02-23*
