# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Eat It is a recipe storage and smart shopping list application built with
FastAPI and SQLModel. It supports parsing recipes from URLs using
recipe-scrapers, semantic search via embeddings, and a plugin system for
extensible importers.

## Commands

```bash
# Install dependencies (requires uv)
uv sync

# Run the development server
uv run fastapi dev src/eat_it/main.py

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_recipes_crud.py

# Run a specific test
uv run pytest tests/test_recipes_crud.py::test_create_recipe

# Run tests excluding integration tests
uv run pytest -m "not integration"

# Lint and format
uv run ruff check --fix
uv run ruff format

# Type check
uv run ty check

# Create a new database migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

## Architecture

### Layered Structure

- `src/eat_it/models/` - SQLModel ORM classes (database tables)
- `src/eat_it/schemas/` - Pydantic schemas (API request/response validation)
- `src/eat_it/routers/` - FastAPI route handlers
- `src/eat_it/services/` - Business logic (parsing, embeddings, plugins)

The separation between models and schemas follows FastAPI best practices: models
define database structure, schemas define API contracts.

### Database

- SQLite with WAL mode for concurrent access
- `sqlite-vec` extension for vector similarity search
- Alembic for migrations
- Engine configured in `database.py` with PRAGMA settings

### Embedding Service

The application loads a sentence-transformers model at startup (configured via
`EAT_IT_EMBEDDING_MODEL`, defaults to `all-MiniLM-L6-v2`). The model is stored
in `app.state.embedding_model` and used for semantic recipe search. See
`services/embedding.py` for utilities.

### Plugin System

Importer plugins are discovered via Python entry points under
`eat_it.importers`. Plugins must implement the `ImporterPlugin` protocol defined
in `services/importer_registry.py`. Register new importers in `pyproject.toml`
under `[project.entry-points."eat_it.importers"]`.

### Recipe Parsing

`services/recipe_parser.py` uses the `recipe-scrapers` library with "wild mode"
to parse any website with schema.org structured data. The `/recipes/parse`
endpoint returns structured data with duplicate detection.

### Application Lifespan

The FastAPI app uses an async lifespan context manager (in `main.py`) to:

1. Initialize the database
2. Load the embedding model
3. Discover importer plugins

Tests bypass this via `noop_lifespan` to avoid loading the heavy model.

## Configuration

Environment variables (prefix: `EAT_IT_`):

- `EAT_IT_DATABASE_URL` - SQLite URL (default: `sqlite:///./data/eat-it.db`)
- `EAT_IT_EMBEDDING_MODEL` - Model name (default: `all-MiniLM-L6-v2`)

## Testing

Tests use in-memory SQLite with `StaticPool` for thread-safety with
`TestClient`. The `conftest.py` fixture clears all tables before each test. The
embedding model is not loaded during tests (uses `noop_lifespan`).

### Backend

- **Framework:** pytest with FastAPI TestClient
- **Test location:** `tests/` directory
- **Naming:** `test_*.py` files, `Test*` classes, `test_*` methods
- **Run tests:** `uv run pytest`
- **Run single test:** `uv run pytest tests/test_recipes_crud.py::TestCreateRecipe::test_create_recipe`
- **Exclude integration tests:** `uv run pytest -m "not integration"`

#### Available Fixtures

From `conftest.py`:

- `test_engine` — In-memory SQLite engine with StaticPool and sqlite-vec
- `test_session` — SQLModel Session for direct database operations
- `client` — FastAPI TestClient with dependency overrides
- `clean_database` — Autouse fixture that clears tables before each test

#### Test Organization

Tests are organized by endpoint/feature using class-based structure:

```python
class TestListRecipes:
    """Tests for GET /recipes endpoint."""

    def test_list_recipes_empty(self, client: TestClient) -> None:
        """GET /recipes returns empty list when no recipes."""
        ...

    def test_list_recipes(self, client: TestClient, test_session: Session) -> None:
        """GET /recipes returns list with pagination."""
        ...
```

### Philosophy: Never mock what you can use for real

Prefer real implementations over mocks. Mocks are a last resort, not a default.

Use real implementations for:

- SQLite: Use `:memory:` databases with StaticPool (see `conftest.py`)
- recipe-scrapers: Use the real library to parse HTML fixtures
- Filesystem: Use temp directories (`tmp_path` fixture) for file I/O tests
- SQLModel: Use real models and sessions, not mocks

Only mock when the real thing has unacceptable side effects:

- Embedding model: Heavy model loading (~100MB) is bypassed via `noop_lifespan`
- External network requests: Recipe URL fetching is flaky in CI; use HTML
  fixtures instead
- External AI services: API calls with real costs and latency

When mocking is truly necessary, document WHY in a comment at the top of the
test file.
