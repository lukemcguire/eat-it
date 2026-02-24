# Phase 1: Foundation and Data Layer - Research

**Researched:** 2026-02-23
**Domain:** SQLite database setup with WAL mode, SQLModel schemas, Alembic
migrations, FastAPI application structure with plugin architecture
**Confidence:** HIGH

## Summary

Phase 1 establishes the database foundation and application skeleton for the
Eat It recipe management system. The core technologies are SQLite with WAL mode
for reliable concurrent access, sqlite-vec for vector embeddings (pre-v1 but
stable enough for local use), SQLModel for Pydantic-native ORM, Alembic for
migrations, and FastAPI with modular routers and lifespan context management.

The plugin architecture uses Python's standard entry_points mechanism via
pyproject.toml's `[project.entry-points]` configuration, which works seamlessly
with uv package manager. This approach is industry-standard (used by pytest,
flake8) and supports runtime discovery without modifying core logic.

**Primary recommendation:** Start with database initialization including WAL
mode and PRAGMA settings, then define all SQLModel schemas in a single
well-organized module, create initial Alembic migration, and finally implement
the FastAPI application structure with lifespan context and importer registry.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Ingredient Schema

- Five-field structured model: `quantity`, `unit`, `name`, `preparation`,
  `raw`
- `unit` can be null for unit-less ingredients ("salt to taste")
- `raw` stores the original unparsed string for reference
- Unit conversion is deferred to Phase 4 (shopping list phase)-store as-is
  for now, add normalization layer later when aggregating shopping lists

#### Ingredient Groups

- Nested structure: recipe has ingredient groups, each containing
  ingredients
- Groups have a `name` (e.g., "For the sauce:") and an `ingredients` array
- This preserves recipe hierarchy even if v1 doesn't display groups
  prominently

#### Recipe Schema Fields

- Standard set: `title`, `description`, `ingredients` (nested groups),
  `instructions`, `prep_time`, `cook_time`, `servings`, `source_url`,
  `image_url`, `tags`
- Timestamps: `created_at` and `updated_at` on all tables

#### Shopping List Schema

- Simple relationship: List -> Items
- Items are generated from recipes but become independent (no back-link to
  source recipe)
- Item fields: `name`, `quantity`, `unit`, `checked` status

#### Database & Storage

- Location: `./data/eat-it.db` (project-relative, works with Docker volume
  mounts)
- Deletes: Hard deletes-self-hosted means users own their data and can
  re-import if needed
- Timestamps: `created_at` + `updated_at` on all tables

#### Importer Registry & Plugin Architecture

- Registry pattern: importers register themselves via entry points
- App calls `registry.parse(url)` - simple, testable, allows runtime
  registration
- Plugin discovery via Python entry_points (user uses `uv` for package
  management, not pip)

#### Configuration

- Environment variables only (12-factor app style)
- Examples: `EAT_IT_DATABASE_URL`, `EAT_IT_EMBEDDING_MODEL`

#### Embedding Model

- Default: `all-MiniLM-L6-v2` from sentence-transformers
- Model name and version tracked in Settings table
- Eager load at app startup (in lifespan context)
- Fully configurable via environment

#### FastAPI Application Structure

- Modular routers (separate routers for recipes, shopping lists, etc.)
- Lifespan context handles: database initialization, embedding model
  loading, importer registry setup
- Structured JSON error responses with error codes, messages, and details

#### Testing Strategy

- In-memory SQLite (`:memory:`) per test for isolation
- Fast, no cleanup needed, each test gets fresh database

### Claude's Discretion

- Alembic migration organization (single vs multiple migrations)
- Settings table structure (key-value vs typed columns)
- Versioned metadata field structure (keep minimal-just version number
  and empty object)
- Exact indexing strategy
- Lifespan context implementation details

### Deferred Ideas (OUT OF SCOPE)

None-discussion stayed within phase scope.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ARCH-01 | Recipe importers follow a provider/strategy pattern so new parsers can be added without touching core logic | Entry points pattern with `importlib.metadata` enables runtime discovery |
| ARCH-02 | A plugin directory is scanned at startup to register importers, exporters, and enhancers | Use `[project.entry-points."eat_it.plugins"]` in pyproject.toml |
| ARCH-03 | Recipe and shopping list schemas include a versioned metadata field to support future plugin data without schema hacks | SQLModel JSON column with `{"version": 1, "data": {}}` structure |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLModel | 0.0.16+ | ORM with Pydantic integration | Combines SQLAlchemy power with Pydantic validation, native FastAPI support |
| Alembic | 1.13+ | Database migrations | Official SQLAlchemy migration tool, autogenerate from models |
| FastAPI | 0.115+ | Web framework | Async-first, automatic OpenAPI, built-in dependency injection |
| sqlite-vec | 0.1.0+ | Vector search extension | Zero-dependency, runs anywhere SQLite runs, supports float/int8/binary vectors |
| sentence-transformers | 3.0+ | Embedding generation | All-MiniLM-L6-v2 is default, runs locally without API keys |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| aiosqlite | 0.20+ | Async SQLite driver | Required for async FastAPI with SQLite |
| uvicorn | 0.30+ | ASGI server | Production and development |
| pydantic-settings | 2.0+ | Environment variable configuration | 12-factor app configuration |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SQLModel | SQLAlchemy + Pydantic separately | SQLModel reduces boilerplate by combining both |
| sqlite-vec | Chromadb, Qdrant | Those require separate services; sqlite-vec is embedded |
| entry_points | Manual plugin scanning | entry_points is Python standard, works with pip/uv |

**Installation:**

```bash
# Core dependencies
uv add sqlmodel alembic fastapi uvicorn aiosqlite sqlite-vec sentence-transformers pydantic-settings

# Development dependencies
uv add --dev pytest pytest-asyncio httpx
```

## Architecture Patterns

### Recommended Project Structure

```
src/eat_it/
├── __init__.py
├── main.py              # FastAPI app with lifespan
├── config.py            # Pydantic settings from env vars
├── database.py          # Engine, session management, WAL setup
├── models/
│   ├── __init__.py
│   ├── recipe.py        # Recipe, IngredientGroup, Ingredient
│   ├── shopping_list.py # ShoppingList, ShoppingListItem
│   └── settings.py      # Settings key-value store
├── routers/
│   ├── __init__.py
│   ├── recipes.py       # Recipe CRUD endpoints
│   ├── shopping_lists.py
│   └── health.py        # Health check endpoint
├── services/
│   ├── __init__.py
│   └── importer_registry.py  # Plugin discovery and management
└── plugins/
    └── __init__.py      # Built-in importers (Phase 2)
alembic/
├── env.py               # Alembic config with SQLModel metadata
├── versions/
│   └── 001_initial.py   # Initial migration
└── alembic.ini
tests/
├── conftest.py          # In-memory DB fixtures
└── test_models.py
```

### Pattern 1: FastAPI Lifespan Context

**What:** Manages application startup/shutdown with async context manager
**When to use:** For database initialization, embedding model loading, plugin
discovery

```python
# Source: FastAPI docs + web search verification
from contextlib import asynccontextmanager
from fastapi import FastAPI
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Initialize database with WAL mode
    from eat_it.database import init_db
    init_db()

    # Startup: Load embedding model
    from sentence_transformers import SentenceTransformer
    app.state.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # Startup: Discover plugins
    from eat_it.services.importer_registry import ImporterRegistry
    app.state.importer_registry = ImporterRegistry()
    app.state.importer_registry.discover_plugins()

    yield  # Application runs here

    # Shutdown: Cleanup (if needed)
    # SQLite handles connection cleanup automatically

app = FastAPI(lifespan=lifespan)
```

### Pattern 2: SQLite WAL Mode Configuration

**What:** Enables concurrent readers with writers, critical for web apps
**When to use:** Always for production SQLite with any concurrent access

```python
# Source: Multiple web sources, verified pattern
import sqlite3
from sqlmodel import create_engine

def init_db():
    engine = create_engine("sqlite:///./data/eat-it.db")

    # Enable WAL mode and other optimizations
    with engine.connect() as conn:
        conn.execute(sqlite3.connect, "PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA wal_autocheckpoint=1000;")

    SQLModel.metadata.create_all(engine)
    return engine
```

### Pattern 3: SQLModel JSON Column for Versioned Metadata

**What:** Stores extensible plugin data without schema changes
**When to use:** For ARCH-03 requirement (versioned metadata field)

```python
# Source: SQLModel docs + web search verification
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import datetime

class RecipeBase(SQLModel):
    title: str
    description: Optional[str] = None
    # ... other fields ...

    # Versioned metadata for plugin extensibility (ARCH-03)
    # Structure: {"version": 1, "data": {...plugin-specific data...}}
    metadata_: dict = Field(
        default_factory=lambda: {"version": 1, "data": {}},
        sa_column=Column("metadata", JSON)
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Recipe(RecipeBase, table=True):
    __tablename__ = "recipes"
    id: Optional[int] = Field(default=None, primary_key=True)
```

### Pattern 4: Entry Points Plugin Discovery

**What:** Standard Python mechanism for runtime plugin discovery
**When to use:** For ARCH-01 and ARCH-02 (plugin architecture)

```python
# Plugin definition in pyproject.toml
# [project.entry-points."eat_it.importers"]
# recipe_scrapers = "eat_it.plugins.recipe_scrapers:RecipeScrapersImporter"

# Source: Python importlib.metadata docs + web verification
from importlib.metadata import entry_points
from typing import Protocol, Dict

class ImporterPlugin(Protocol):
    name: str
    def can_parse(self, url: str) -> bool: ...
    async def parse(self, url: str) -> Recipe: ...

class ImporterRegistry:
    def __init__(self):
        self._importers: Dict[str, ImporterPlugin] = {}

    def discover_plugins(self) -> None:
        """Discover and register all plugins via entry points."""
        eps = entry_points(group="eat_it.importers")
        for entry_point in eps:
            try:
                importer_class = entry_point.load()
                importer = importer_class()
                self._importers[importer.name] = importer
            except Exception as e:
                # Log error but don't crash on plugin load failure
                print(f"Failed to load plugin {entry_point.name}: {e}")

    async def parse(self, url: str) -> Optional[Recipe]:
        """Find appropriate importer and parse URL."""
        for importer in self._importers.values():
            if importer.can_parse(url):
                return await importer.parse(url)
        return None
```

### Pattern 5: SQLModel with Alembic

**What:** Integrate SQLModel metadata with Alembic autogenerate
**When to use:** For all schema migrations

```python
# alembic/env.py
# Source: SQLModel + Alembic integration guides
from sqlmodel import SQLModel
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Import all models so Alembic can see them
from eat_it.models.recipe import Recipe, IngredientGroup, Ingredient
from eat_it.models.shopping_list import ShoppingList, ShoppingListItem
from eat_it.models.settings import Settings

target_metadata = SQLModel.metadata

# In alembic.ini:
# sqlalchemy.url = sqlite:///./data/eat-it.db
```

### Anti-Patterns to Avoid

- **Using `@app.on_event("startup")`**: Deprecated in FastAPI 0.93+, use
  lifespan context instead
- **Creating JSON fields without version key**: Makes future migration
  impossible; always include `version` field
- **Forgetting `PRAGMA foreign_keys=ON`**: SQLite doesn't enforce FKs by
  default
- **Using `metadata` as column name**: Reserved by SQLAlchemy; use `metadata_`
  with `sa_column=Column("metadata", ...)`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Plugin discovery | Manual directory scanning | `importlib.metadata.entry_points()` | Standard, works with pip/uv, handles dependencies |
| JSON schema migrations | Custom migration logic | Version field in metadata | Backward-compatible, explicit versioning |
| Database connection management | Global connection variable | SQLModel Session/engine pattern | Thread-safe, connection pooling |
| Environment configuration | Custom env parsing | `pydantic-settings.BaseSettings` | Type-safe, validation, .env support |
| Error responses | Plain text strings | FastAPI `HTTPException` with JSON | Consistent API, automatic OpenAPI docs |

**Key insight:** Python's standard library and Pydantic ecosystem solve most
configuration and plugin problems. Entry points are the industry-standard
approach used by pytest, flake8, and other major projects.

## Common Pitfalls

### Pitfall 1: SQLite Concurrent Access Without WAL

**What goes wrong:** `SQLITE_BUSY` errors when multiple requests try to write
**Why it happens:** Default rollback journal locks the entire database file
**How to avoid:** Always enable WAL mode at database initialization
**Warning signs:** Intermittent 500 errors under load, "database is locked"
messages

### Pitfall 2: sqlite-vec Pre-v1 Breaking Changes

**What goes wrong:** API changes between versions break vector operations
**Why it happens:** sqlite-vec is pre-v1 with stated breaking change policy
**How to avoid:** Pin version in pyproject.toml, test upgrade before
deploying
**Warning signs:** `vec_version()` returns different format, virtual table
syntax errors

### Pitfall 3: Entry Points Not Found with uv

**What goes wrong:** `entry_points(group="...")` returns empty after `uv add`
**Why it happens:** Entry points only register after package install, not
during development
**How to avoid:** Use `uv pip install -e .` to install project in editable
mode
**Warning signs:** Plugin registry empty at startup, importers not discovered

### Pitfall 4: SQLModel JSON Column with Pydantic

**What goes wrong:** OpenAPI schema generation fails with JSON columns
**Why it happens:** SQLAlchemy Column objects aren't JSON-serializable by
Pydantic
**How to avoid:** Use `Field(sa_column=Column(...))` not just `Column(...)`
**Warning signs:** `/openapi.json` returns 500, swagger UI fails to load

### Pitfall 5: Missing Model Imports in Alembic

**What goes wrong:** `alembic revision --autogenerate` creates empty migration
**Why it happens:** Models not imported in `alembic/env.py`, so metadata is
empty
**How to avoid:** Explicitly import all model classes in env.py
**Warning signs:** Migration file has empty `upgrade()` and `downgrade()`

## Code Examples

### Complete SQLModel Schema with All Requirements

```python
# src/eat_it/models/recipe.py
from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import Optional, List
from datetime import datetime

class Ingredient(SQLModel, table=True):
    """Single ingredient with structured parsing."""
    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="ingredient_groups.id")

    quantity: Optional[float] = None
    unit: Optional[str] = None  # Can be null ("salt to taste")
    name: str
    preparation: Optional[str] = None  # "diced", "minced", etc.
    raw: str  # Original unparsed string

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IngredientGroup(SQLModel, table=True):
    """Group of ingredients (e.g., "For the sauce:")."""
    __tablename__ = "ingredient_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipes.id")
    name: Optional[str] = None

    ingredients: List[Ingredient] = Relationship(back_populates="group")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Recipe(SQLModel, table=True):
    """Complete recipe with nested ingredient groups."""
    __tablename__ = "recipes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    instructions: str
    prep_time: Optional[int] = None  # Minutes
    cook_time: Optional[int] = None  # Minutes
    servings: Optional[int] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Versioned metadata for plugin extensibility (ARCH-03)
    metadata_: dict = Field(
        default_factory=lambda: {"version": 1, "data": {}},
        sa_column=Column("metadata", JSON)
    )

    groups: List[IngredientGroup] = Relationship(back_populates="recipe")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Database Initialization with WAL

```python
# src/eat_it/database.py
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path
import sqlite3

DATABASE_PATH = Path("./data/eat-it.db")

def get_engine():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{DATABASE_PATH}")

    # Configure SQLite for production use
    @engine.event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA wal_autocheckpoint=1000")
        cursor.close()

    return engine

engine = get_engine()

def get_session():
    return Session(engine)
```

### pyproject.toml Entry Points Configuration

```toml
# pyproject.toml
[project]
name = "eat-it"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "sqlmodel>=0.0.16",
    "alembic>=1.13",
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "aiosqlite>=0.20",
    "sqlite-vec>=0.1.0",
    "sentence-transformers>=3.0",
    "pydantic-settings>=2.0",
]

# Plugin entry points (ARCH-02)
# Third-party packages can register importers by adding:
# [project.entry-points."eat_it.importers"]
# my_importer = "my_package.importer:MyImporter"
[project.entry-points."eat_it.importers"]
# Built-in importers will be added in Phase 2

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` | `lifespan` context manager | FastAPI 0.93 (2023) | Better async handling, cleaner resource management |
| `pkg_resources` | `importlib.metadata` | Python 3.8+ (2019) | Faster import, no setuptools dependency |
| `setup.py` | `pyproject.toml` | PEP 621 (2021) | Standardized, tool-agnostic configuration |
| rollback journal | WAL mode | SQLite 3.7.0 (2010) | Concurrent readers, better performance |

**Deprecated/outdated:**
- `@app.on_event()`: Use `lifespan` context manager instead
- `pkg_resources`: Use `importlib.metadata` for entry point discovery
- `setup.py` with `entry_points` dict: Use `pyproject.toml`
  `[project.entry-points]`

## Open Questions

1. **Settings table structure**
   - What we know: User left this to Claude's discretion
   - Options: Key-value (flexible) vs typed columns (type-safe)
   - Recommendation: Key-value with JSON values for flexibility; only a
     few settings exist in v1

2. **Migration organization**
   - What we know: User left single vs multiple to discretion
   - Options: Single initial migration vs separate per-model migrations
   - Recommendation: Single initial migration for Phase 1 (simpler), add
     per-feature migrations in later phases

3. **Indexing strategy**
   - What we know: User left to discretion
   - What's unclear: Which fields need indexes for Phase 3 search
   - Recommendation: Index `source_url` for duplicate detection,
     `created_at` for listing; defer vector index to Phase 3

## Sources

### Primary (HIGH confidence)

- FastAPI documentation - lifespan context pattern
- SQLModel documentation - JSON columns, relationships
- Python `importlib.metadata` documentation - entry points discovery
- sqlite-vec GitHub repository - installation and usage

### Secondary (MEDIUM confidence)

- Multiple web sources confirming SQLite WAL mode configuration
- Web sources confirming pyproject.toml entry points syntax with uv
- Web sources confirming Alembic + SQLModel integration patterns

### Tertiary (LOW confidence)

- None - all critical patterns verified with multiple sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries are mature with current documentation
- Architecture: HIGH - Patterns are industry-standard (FastAPI, pytest style)
- Pitfalls: HIGH - Based on common issues documented across multiple sources

**Research date:** 2026-02-23
**Valid until:** 30 days (stable technologies, but sqlite-vec pre-v1 status
may change)
