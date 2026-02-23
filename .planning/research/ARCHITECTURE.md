# Architecture Research

**Domain:** Self-hosted recipe manager with local AI search
**Researched:** 2026-02-23
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (React SPA)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Recipes  │  │  Search  │  │Shopping  │  │ Import   │   │
│  │  Pages   │  │   Page   │  │  List    │  │  Page    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼──────────────┼──────────┘
        │             │    REST/JSON │              │
        │             │    API calls │              │
┌───────┼─────────────┼─────────────┼──────────────┼──────────┐
│       ↓             ↓             ↓              ↓           │
│              FastAPI (API Layer)                             │
│  /api/recipes  /api/search  /api/lists  /api/import/preview │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer                               │
│  ┌────────────┐  ┌───────────┐  ┌──────────────────────┐   │
│  │  Recipe    │  │  Search   │  │  Shopping List       │   │
│  │  Service   │  │  Service  │  │  Service             │   │
│  └─────┬──────┘  └─────┬─────┘  └──────────┬───────────┘   │
│        │               │                   │               │
│  ┌─────┴──────┐  ┌─────┴─────┐             │               │
│  │  Importer  │  │ Embedding │             │               │
│  │  Registry  │  │ Pipeline  │             │               │
│  └─────┬──────┘  └─────┬─────┘             │               │
├────────┼───────────────┼───────────────────┼───────────────┤
│        ↓               ↓                   ↓               │
│                   Data Layer                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         SQLite (WAL mode)  +  sqlite-vec             │   │
│  │   recipes  │  shopping_lists  │  vec_embeddings      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| React SPA | User interface, client-side routing, form state | FastAPI via REST/JSON |
| FastAPI API layer | Route handling, request validation, auth | Service layer only |
| Recipe Service | CRUD for recipes, triggering import and embed | Importer Registry, Embedding Pipeline, DB |
| Search Service | Embedding queries, keyword fallback, result ranking | Embedding Pipeline, DB |
| Shopping List Service | List generation, ingredient aggregation, item sync | DB |
| Importer Registry | Plugin discovery, provider dispatch, parse preview | recipe-scrapers, custom providers |
| Embedding Pipeline | Model loading, encode text, write vectors to DB | sentence-transformers, sqlite-vec |
| Data Layer | SQLAlchemy models, migrations, query abstraction | SQLite file |

## Recommended Project Structure

```
eat-it/
├── src/
│   ├── main.py                  # FastAPI app init, lifespan startup
│   ├── config.py                # Settings via pydantic-settings
│   ├── api/
│   │   ├── recipes.py           # /api/recipes CRUD endpoints
│   │   ├── search.py            # /api/search endpoint
│   │   ├── shopping_lists.py    # /api/lists endpoints
│   │   └── import_.py           # /api/import/preview + /confirm
│   ├── services/
│   │   ├── recipe_service.py    # Orchestrates import + embed + store
│   │   ├── search_service.py    # Semantic + keyword search
│   │   └── shopping_service.py  # Aggregation + list management
│   ├── importers/
│   │   ├── base.py              # ImporterBase ABC
│   │   ├── registry.py          # Plugin loader + dispatch
│   │   ├── recipe_scrapers.py   # Adapter for recipe-scrapers lib
│   │   └── plugins/             # Drop-in custom importers scanned at startup
│   ├── embeddings/
│   │   ├── pipeline.py          # Model load, encode, write to vec table
│   │   └── models.py            # Embedding model constants + lazy init
│   ├── db/
│   │   ├── engine.py            # SQLAlchemy engine, WAL pragma setup
│   │   ├── session.py           # Async session factory + dependency
│   │   └── migrations/          # Alembic versions
│   ├── models/
│   │   ├── recipe.py            # Recipe ORM + Pydantic schemas
│   │   ├── shopping_list.py     # ShoppingList + ShoppingListItem
│   │   └── embedding.py         # Vec table definition
│   └── utils/
│       ├── ingredient_parser.py # Quantity normalization + dedup
│       └── logger.py            # Structured logging config
├── frontend/
│   ├── src/
│   │   ├── components/          # Shared UI components
│   │   ├── pages/               # Route-level pages
│   │   ├── hooks/               # Custom hooks (useSearch, useList)
│   │   └── api/                 # Typed API client (axios/fetch wrappers)
│   └── dist/                    # Built output served by FastAPI
├── docker/
│   ├── Dockerfile               # Multi-stage: node build → python runtime
│   └── docker-compose.yml       # Single service + volume mount for DB
└── tests/
    ├── unit/
    └── integration/
```

### Structure Rationale

- **src/importers/**: Isolates all import concerns. The `plugins/`
  subdirectory is scanned at startup. New importers never require changes
  outside this directory.
- **src/embeddings/**: Separates the model lifecycle (slow first load)
  from the rest of the app. Lazy initialization avoids blocking startup.
- **src/db/**: Engine configuration separate from session dependency
  injection so WAL pragmas and sqlite-vec extension loading happen once
  at engine creation, not per request.
- **frontend/dist/**: Built by Docker's Node stage, then mounted into the
  Python runtime stage. FastAPI serves it with a SPAStaticFiles mount
  after all `/api/` routes are registered.

## Architectural Patterns

### Pattern 1: Importer Provider / Strategy Pattern

**What:** An abstract base class defines the importer contract. A
registry scans `src/importers/plugins/` at startup using
`importlib.util.spec_from_file_location` and builds a dispatch table
keyed by URL domain or importer name.

**When to use:** Every time a new import source is needed (OCR, video
transcript, Paprika export). New file in `plugins/` — nothing else
changes.

**Trade-offs:** Adds indirection; worth it because the project
explicitly names extensibility as an architectural requirement.

```python
# src/importers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ParsedRecipe:
    title: str
    ingredients: list[str]
    instructions: list[str]
    metadata: dict  # versioned field

class ImporterBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def can_handle(self, url: str) -> bool: ...

    @abstractmethod
    def parse(self, url: str) -> ParsedRecipe: ...
```

```python
# src/importers/registry.py
import importlib.util
from pathlib import Path
from .base import ImporterBase

class ImporterRegistry:
    def __init__(self) -> None:
        self._importers: list[ImporterBase] = []

    def load_plugins(self, plugin_dir: Path) -> None:
        for path in sorted(plugin_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            spec = importlib.util.spec_from_file_location(
                path.stem, path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for attr in vars(mod).values():
                if (
                    isinstance(attr, type)
                    and issubclass(attr, ImporterBase)
                    and attr is not ImporterBase
                ):
                    self._importers.append(attr())

    def get_importer(self, url: str) -> ImporterBase | None:
        for importer in self._importers:
            if importer.can_handle(url):
                return importer
        return None
```

### Pattern 2: Embedding Pipeline with Lazy Model Loading

**What:** The embedding model (sentence-transformers) is loaded once at
application startup via FastAPI's lifespan context manager. The model
instance is stored as application state and injected into services via
FastAPI's `Depends`. Embedding is written to SQLite synchronously in a
thread pool executor to avoid blocking the async event loop.

**When to use:** Always. Sentence-transformers models (even small ones
like `all-MiniLM-L6-v2`) take 1-3 seconds to load. Loading on first
request causes a noticeable delay.

**Trade-offs:** Model stays in RAM (~90MB for MiniLM). On a Raspberry
Pi with 2GB RAM this is acceptable; on 1GB it may require model
quantization.

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .embeddings.pipeline import EmbeddingPipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.embeddings = EmbeddingPipeline(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    app.state.embeddings.load()       # blocks startup, intentional
    app.state.importers = ImporterRegistry()
    app.state.importers.load_plugins(PLUGIN_DIR)
    yield
    # cleanup on shutdown

app = FastAPI(lifespan=lifespan)
```

### Pattern 3: sqlite-vec for Vector Storage

**What:** sqlite-vec is loaded as a SQLite extension at engine creation.
A `vec0` virtual table stores float32 embeddings alongside a recipe_id
foreign key. Similarity search uses `vec_distance_cosine()` or
`ORDER BY distance` against the virtual table, joined back to the
recipes table.

**When to use:** For all semantic search queries. Keyword fallback runs
a plain `LIKE` query on the recipes table when the embedding pipeline is
unavailable.

**Trade-offs:** sqlite-vec is pre-v1 and the API may have breaking
changes. Pin the version in `pyproject.toml`. The virtual table does not
support `FOREIGN KEY` constraints; enforce referential integrity at the
service layer.

**Confidence:** MEDIUM — sqlite-vec is actively developed and the
recommended approach for embedded vector search, but "expect breaking
changes" is their stated policy as of v0.1.6.

```python
# src/db/engine.py
import sqlite3
import sqlite_vec
from sqlalchemy import event, create_engine

engine = create_engine("sqlite:///./data/eat-it.db")

@event.listens_for(engine, "connect")
def load_sqlite_extensions(dbapi_conn, _):
    dbapi_conn.enable_load_extension(True)
    sqlite_vec.load(dbapi_conn)
    dbapi_conn.execute("PRAGMA journal_mode=WAL")
    dbapi_conn.execute("PRAGMA synchronous=NORMAL")
```

```sql
-- src/db/migrations/001_vec_table.sql
CREATE VIRTUAL TABLE IF NOT EXISTS vec_recipe_embeddings
USING vec0(
  recipe_id INTEGER,
  embedding float[384]   -- MiniLM-L6-v2 dimension
);
```

### Pattern 4: Preview-Then-Confirm Import

**What:** Import is split into two API calls. `POST /api/import/preview`
calls the importer registry, returns a `ParsedRecipe` but does NOT write
to the database. `POST /api/import/confirm` takes the previewed data
(optionally edited by the user) and persists it, then enqueues embedding
generation as a FastAPI background task.

**When to use:** All URL imports. Prevents polluting the recipe
collection with bad parses.

**Trade-offs:** Embedding runs after the response is returned. The
recipe appears in the collection immediately but search results may not
include it for 1-2 seconds on first load.

```python
# Data flow for import + embed
POST /api/import/preview
  → ImporterRegistry.get_importer(url).parse(url)
  → return ParsedRecipe (no DB write)

POST /api/import/confirm
  → RecipeService.create(parsed_recipe)      # writes to recipes table
  → BackgroundTasks.add_task(embed_recipe)   # async, non-blocking
    → EmbeddingPipeline.encode(recipe_text)
    → INSERT INTO vec_recipe_embeddings ...
```

### Pattern 5: Polling-Based Multi-Device List Sync

**What:** Shopping list items include an `updated_at` timestamp. Clients
poll `GET /api/lists/{id}?since=<timestamp>` to receive only changed
items. The endpoint returns a list-level ETag or `last_modified`
header. No websockets required in MVP.

**When to use:** All shared list scenarios. Works for 2-5 concurrent
users on a household LAN without any real-time infrastructure.

**Trade-offs:** User A checks off an item; User B sees the change on
next poll (default 5-10 seconds). Not instant, but the project
requirements explicitly accept this trade-off.

```python
# src/api/shopping_lists.py
@router.get("/{list_id}/items")
async def get_list_items(
    list_id: int,
    since: float | None = None,   # Unix timestamp query param
    session: AsyncSession = Depends(get_session),
):
    items = await ShoppingListService.get_items(
        session, list_id, modified_since=since
    )
    return {"items": items, "server_time": time.time()}
```

## Data Flow

### Import → Parse → Embed → Store

```
User pastes URL
    ↓
POST /api/import/preview
    ↓
ImporterRegistry.get_importer(url)   ← plugin dispatch by domain
    ↓
importer.parse(url)                  ← recipe-scrapers or custom
    ↓
return ParsedRecipe to frontend       ← user edits/confirms
    ↓
POST /api/import/confirm
    ↓
RecipeService.create(data)           ← INSERT into recipes table
    ↓  (response returned to user)
BackgroundTask: embed_recipe()
    ↓
EmbeddingPipeline.encode(title + ingredients + instructions)
    ↓
INSERT INTO vec_recipe_embeddings    ← sqlite-vec virtual table
```

### Search Flow

```
User types query
    ↓
POST /api/search  { "q": "vegetarian dinner for 4" }
    ↓
SearchService.search(query)
    ↓
EmbeddingPipeline.encode(query)      ← same model as indexing
    ↓
SELECT recipe_id, distance
  FROM vec_recipe_embeddings
  WHERE embedding MATCH ?
  ORDER BY distance LIMIT 20         ← sqlite-vec KNN query
    ↓
JOIN recipes ON id = recipe_id       ← fetch full recipe data
    ↓
return ranked results                ← distance = relevance score
    ↓ (if embedding unavailable)
FALLBACK: SELECT * FROM recipes
  WHERE title LIKE ? OR ...          ← plain keyword search
```

### Shopping List Generation

```
User selects N recipes
    ↓
POST /api/lists  { "recipe_ids": [1, 3, 7] }
    ↓
ShoppingListService.generate(recipe_ids)
    ↓
Fetch all ingredients from recipes
    ↓
IngredientParser.normalize_and_merge()  ← dedup + sum quantities
    ↓
INSERT INTO shopping_lists + shopping_list_items
    ↓
return list with shareable link/PIN
```

### Shopping List Sync (Polling)

```
User A checks item on mobile
    ↓
PATCH /api/lists/{id}/items/{item_id}  { "checked": true }
    ↓
UPDATE shopping_list_items SET checked=true, updated_at=NOW()
    ↓
User B's client polls GET /api/lists/{id}/items?since={last_poll}
    ↓
Return only items where updated_at > since
    ↓
Frontend merges delta into current list state
```

## Docker Deployment Architecture

Single-container deployment using a 3-stage Dockerfile:

```text
Stage 1 (node:alpine)  — build React/Vite frontend
    npm ci && npm run build → /app/dist

Stage 2 (python:3.13-slim) — install Python deps
    pip install --no-cache-dir .

Stage 3 (python:3.13-slim) — runtime
    COPY --from=stage1 /app/dist  → /app/frontend/dist
    COPY --from=stage2 packages   → /app
    CMD ["uvicorn", "src.main:app"]
    EXPOSE 8000
```

FastAPI serves the built frontend using a custom SPAStaticFiles mount
registered after all `/api/` routes:

```python
from starlette.staticfiles import StaticFiles

# Must be LAST — catches all unmatched routes for SPA routing
app.mount("/", SPAStaticFiles(
    directory="frontend/dist", html=True
), name="spa")
```

`docker-compose.yml` for household deployment:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data        # SQLite file persisted outside container
      - ./plugins:/app/src/importers/plugins  # hot-swap custom importers
    environment:
      - DATA_DIR=/app/data
      - PLUGIN_DIR=/app/src/importers/plugins
```

SQLite file lives in the mounted volume. No database server container
needed.

## Integration Points

### External Libraries

| Library | Integration Pattern | Notes |
|---------|---------------------|-------|
| recipe-scrapers | Wrapped in `RecipeScrapersImporter(ImporterBase)` | Supports wild_mode for unsupported sites via Schema.org parsing |
| sentence-transformers | Loaded once in lifespan; injected via app.state | Model download on first run (~90MB); cache in Docker volume |
| sqlite-vec | SQLAlchemy engine connect event loads extension | Pin version; pre-v1 API may change |
| SQLAlchemy 2.x async | AsyncSession per request via Depends | Requires `aiosqlite` driver for async SQLite |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API → Service | Direct function call (same process) | Never access DB from API layer directly |
| Service → DB | AsyncSession injected, repository functions | No raw SQL outside db/ module |
| Service → Embedding | app.state.embeddings injected | Pipeline may be None if model failed to load; service handles gracefully |
| Service → Importers | app.state.importers registry | Returns None if no importer matches; triggers manual-entry path |
| Frontend → API | REST/JSON over HTTP | Same origin in Docker; CORS config for dev |

## Suggested Build Order

Components have the following dependency chain. Build in this order to
avoid blockers:

```
1. DB engine + migrations (sqlite-vec table, WAL setup)
      ↓
2. Recipe ORM model + Pydantic schemas
      ↓
3. Importer ABC + recipe-scrapers adapter (no DB yet needed)
      ↓
4. Recipe Service (import + CRUD) + API endpoints
      ↓  (app usable for basic import/view at this point)
5. Embedding pipeline + sqlite-vec integration
      ↓
6. Search Service + search API endpoint
      ↓  (search works at this point)
7. Shopping list models + ShoppingListService
      ↓
8. Shopping list API + polling sync
      ↓  (full MVP feature set)
9. Frontend React app (builds against stable API)
      ↓
10. Docker multi-stage build + docker-compose
```

**Rationale:** DB and models must exist before any service. Import works
without embeddings (embeddings run as background task). Search depends
on embeddings. Shopping list is independent of search. Frontend can be
developed against mock API in parallel from step 4 onward.

## Anti-Patterns

### Anti-Pattern 1: Embedding at Request Time Synchronously

**What people do:** Call `model.encode(text)` inside the POST endpoint
handler before returning the response.

**Why it's wrong:** MiniLM-L6-v2 takes ~50-200ms per encode on CPU.
On a Raspberry Pi it may take 500ms+. The import endpoint stalls until
embedding completes.

**Do this instead:** Return the recipe immediately from the confirm
endpoint. Use FastAPI's `BackgroundTasks` to encode and write the
vector after the response is sent. The recipe appears in keyword search
immediately; semantic search catches up within seconds.

### Anti-Pattern 2: Loading the Embedding Model Per Request

**What people do:** Instantiate `SentenceTransformer(model_name)` inside
a route handler or Depends function.

**Why it's wrong:** Model load takes 1-3 seconds and downloads ~90MB on
first call. Each request would either wait or re-download.

**Do this instead:** Use FastAPI's lifespan context to load the model
once at startup and store it in `app.state.embeddings`.

### Anti-Pattern 3: Bypassing the Importer Registry

**What people do:** Call `recipe_scrapers.scrape_me(url)` directly in
the recipe service or API route handler.

**Why it's wrong:** Couples the core recipe service to a specific
library. Adding a new importer type (OCR, CSV, Paprika) requires editing
service logic.

**Do this instead:** The service only calls
`importer_registry.get_importer(url).parse(url)`. The registry handles
dispatch. New importers are added as files in `plugins/`.

### Anti-Pattern 4: Storing Embeddings in a Separate SQLite File

**What people do:** Keep vectors in `vectors.db` and recipes in
`recipes.db` to "separate concerns."

**Why it's wrong:** JOIN-equivalent queries across two SQLite databases
require ATTACH or application-level joins, losing the simplicity of
single-file deployment.

**Do this instead:** Load sqlite-vec into the same database file. The
`vec0` virtual table coexists with ORM tables. Backup is a single file
copy.

### Anti-Pattern 5: WebSockets for Household Sync

**What people do:** Add WebSocket infrastructure for "real-time"
shopping list updates to feel modern.

**Why it's wrong:** WebSockets require persistent connections, add
infrastructure complexity, and are unnecessary when the latency
requirement is "sync on refresh." The project explicitly defers real-time
to a future milestone.

**Do this instead:** Client-side polling every 5-10 seconds with the
`?since=` timestamp filter. Simple, stateless, and sufficient for
2-5 users on a LAN.

## Scaling Considerations

This app targets 5-10 concurrent household users. Scale beyond that is
out of scope for v1.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-10 users (MVP target) | SQLite WAL mode, single container, polling sync |
| 10-50 users | Add nginx in front for static file serving; SQLite still fine |
| 50+ users | SQLite WAL becomes a write bottleneck; migrate to PostgreSQL + pgvector |

**First bottleneck:** SQLite's single-writer lock. At household scale
this never triggers. If the app is ever opened to a larger audience,
replace SQLite with PostgreSQL and sqlite-vec with pgvector.

**Second bottleneck:** Embedding model on CPU. A single MiniLM encode
takes ~50-200ms. For large collections with concurrent import, move
embedding to a background worker process (e.g., arq or Celery). Not
needed at MVP scale.

## Sources

- sqlite-vec GitHub (asg017): https://github.com/asg017/sqlite-vec
  (MEDIUM confidence — pre-v1, actively developed, Raspberry Pi
  supported)
- FastAPI official docs, Background Tasks:
  https://fastapi.tiangolo.com/tutorial/background-tasks/
  (HIGH confidence)
- FastAPI official docs, Docker deployment:
  https://fastapi.tiangolo.com/deployment/docker/
  (HIGH confidence)
- Serving React with FastAPI (davidmuraya.com):
  https://davidmuraya.com/blog/serving-a-react-frontend-application-with-fastapi/
  (MEDIUM confidence — community article, pattern verified against
  FastAPI StaticFiles docs)
- Python plugin systems (oneuptime.com):
  https://oneuptime.com/blog/post/2026-01-30-python-plugin-systems/view
  (MEDIUM confidence — matches official Python importlib docs)
- recipe-scrapers GitHub (hhursev):
  https://github.com/hhursev/recipe-scrapers
  (HIGH confidence — actively maintained, v15.11.0 released Dec 2025)
- SQLite WAL mode official docs:
  https://sqlite.org/wal.html
  (HIGH confidence)
- sentence-transformers documentation:
  https://sbert.net/
  (HIGH confidence)

---
*Architecture research for: self-hosted recipe manager (eat-it)*
*Researched: 2026-02-23*
