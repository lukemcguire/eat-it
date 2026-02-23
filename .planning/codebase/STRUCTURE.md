# Codebase Structure

**Analysis Date:** 2026-02-23

## Directory Layout

```
eat-it/
├── .planning/              # Planning and documentation
│   ├── PRD/               # Product requirements
│   └── codebase/          # Architecture documentation
├── frontend/              # Web UI (React, Vue, or Svelte)
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── services/      # API client services
│   │   ├── hooks/         # Custom React hooks (if using React)
│   │   ├── styles/        # Global CSS/styling
│   │   └── App.tsx        # Root application component
│   ├── index.html         # Entry HTML file
│   └── package.json       # Frontend dependencies
├── src/                   # Backend Python code
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── api/               # API route handlers
│   │   ├── __init__.py
│   │   ├── routes.py      # Route definitions
│   │   ├── recipes.py     # Recipe endpoints
│   │   ├── search.py      # Search endpoints
│   │   └── shopping_lists.py  # Shopping list endpoints
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── recipe_service.py
│   │   ├── search_service.py
│   │   ├── shopping_list_service.py
│   │   └── parser_service.py
│   ├── models/            # ORM models and data structures
│   │   ├── __init__.py
│   │   ├── recipe.py
│   │   ├── shopping_list.py
│   │   ├── user.py
│   │   └── base.py        # Base model class
│   ├── db/                # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py  # Database initialization
│   │   ├── migrations/    # Alembic migrations (if using)
│   │   └── repository.py  # Data access patterns
│   ├── integrations/      # External service integrations
│   │   ├── __init__.py
│   │   ├── recipe_parser.py  # Recipe parser interface
│   │   └── exporters.py   # Export/import handlers (JSON, CSV)
│   ├── middleware/        # API middleware
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication/session middleware
│   │   └── validation.py  # Request validation
│   ├── utils/             # Shared utilities
│   │   ├── __init__.py
│   │   ├── logger.py      # Logging configuration
│   │   ├── validators.py  # Input validation functions
│   │   └── formatters.py  # Data formatting helpers
│   └── config.py          # Configuration and environment variables
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures and configuration
│   ├── unit/              # Unit tests
│   │   ├── test_recipe_service.py
│   │   ├── test_search_service.py
│   │   ├── test_shopping_list_service.py
│   │   └── test_parsers.py
│   ├── integration/       # Integration tests
│   │   ├── test_recipe_api.py
│   │   ├── test_search_api.py
│   │   └── test_shopping_list_api.py
│   └── fixtures/          # Test data and factories
│       ├── recipes.py
│       └── users.py
├── docs/                  # User and developer documentation
│   ├── index.md
│   ├── setup.md           # Installation and self-hosting guide
│   ├── api.md             # API documentation
│   └── architecture.md    # Architecture details
├── docker/                # Container and deployment
│   ├── Dockerfile         # Application image
│   └── docker-compose.yml # Multi-service orchestration
├── scripts/               # Utility scripts
│   ├── setup_db.py        # Database initialization
│   └── seed_recipes.py    # Sample recipe loading
├── .pre-commit-config.yaml    # Git hooks configuration
├── .gitignore             # Git ignore patterns
├── pyproject.toml         # Python project configuration
├── README.md              # Project overview
└── LICENSE                # MIT license
```

## Directory Purposes

**frontend/:**
- Purpose: User-facing web application
- Contains: React/Vue/Svelte components, styling, API integration
- Key files: `frontend/src/App.tsx`, `frontend/src/pages/` (recipe import,
  search, shopping list pages)

**src/:**
- Purpose: Backend Python application code
- Contains: All business logic, API routes, database models, integrations
- Key files: `src/main.py` (entry), `src/api/` (routes), `src/services/`
  (logic)

**tests/:**
- Purpose: Automated test suite
- Contains: Unit tests, integration tests, test fixtures
- Key files: `tests/conftest.py` (pytest configuration),
  `tests/unit/` (isolated tests), `tests/integration/` (API/end-to-end)

**docs/:**
- Purpose: User and developer documentation
- Contains: Setup guides, API reference, architecture explanations
- Key files: `docs/setup.md` (self-hosting), `docs/api.md` (endpoint docs)

**.planning/:**
- Purpose: Project planning and analysis
- Contains: Product requirements, architecture decisions, roadmap
- Key files: `PRD/PRD.md` (requirements), `codebase/ARCHITECTURE.md` (design)

## Key File Locations

**Entry Points:**
- `src/main.py`: Backend API server initialization and startup
- `frontend/index.html`: Frontend HTML entry point
- `frontend/src/App.tsx`: Root frontend React/Vue/Svelte component

**Configuration:**
- `pyproject.toml`: Python dependencies, build config, tool configurations
- `frontend/package.json`: Frontend dependencies (if using Node.js-based
  framework)
- `src/config.py`: Application settings and environment variables

**Core Logic:**
- `src/services/recipe_service.py`: Recipe creation, retrieval, deletion
- `src/services/search_service.py`: Natural language and keyword search
- `src/services/shopping_list_service.py`: Shopping list generation and
  management
- `src/integrations/recipe_parser.py`: Recipe URL parsing and extraction

**Data Models:**
- `src/models/recipe.py`: Recipe ORM model and schema
- `src/models/shopping_list.py`: Shopping list and item models
- `src/models/user.py`: User/session model (if authentication enabled)

**Testing:**
- `tests/conftest.py`: Pytest configuration, shared fixtures
- `tests/unit/`: Isolated unit tests for services and utilities
- `tests/integration/`: Full API and workflow integration tests
- `tests/fixtures/`: Test data factories and sample recipes

## Naming Conventions

**Files:**
- Service files: `{domain}_service.py` (e.g., `recipe_service.py`,
  `search_service.py`)
- Model files: `{entity}.py` (e.g., `recipe.py`, `shopping_list.py`)
- API route files: `{resource}.py` (e.g., `recipes.py`, `shopping_lists.py`)
- Test files: `test_{module_name}.py` (e.g., `test_recipe_service.py`)

**Directories:**
- Functional modules: lowercase with underscores (e.g., `src/services/`,
  `src/integrations/`)
- Test grouping: by test type (e.g., `tests/unit/`, `tests/integration/`)
- Feature grouping in frontend: by domain (e.g., `frontend/src/pages/`,
  `frontend/src/components/`)

**Python Modules:**
- Classes: PascalCase (e.g., `RecipeService`, `ShoppingList`)
- Functions: snake_case (e.g., `import_recipe_from_url()`,
  `search_recipes()`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RECIPES_PER_LIST`,
  `PARSE_TIMEOUT_SECONDS`)

## Where to Add New Code

**New Feature:**
- Primary code: Implement service in `src/services/`, create models in
  `src/models/` if needed
- API endpoints: Add routes to appropriate file in `src/api/` (e.g., new
  search type in `src/api/search.py`)
- Tests: Add unit tests to `tests/unit/`, integration tests to
  `tests/integration/`
- Frontend: Add components to `frontend/src/components/`, pages to
  `frontend/src/pages/`, API service to `frontend/src/services/`

**New Component/Module:**
- Implementation: Create service file in `src/services/{name}_service.py`
- Models: Create ORM models in `src/models/{name}.py`
- Tests: Create test file in `tests/unit/test_{name}_service.py`
- Documentation: Add endpoint docs to `docs/api.md`

**Utilities:**
- Shared helpers: Place in `src/utils/` (e.g., validators, formatters,
  loggers)
- Frontend utilities: Place in `frontend/src/utils/` or domain-specific
  subdirectories
- Constants: Define in `src/config.py` or module-specific files

## Special Directories

**__pycache__/ and *.pyc:**
- Purpose: Python bytecode cache
- Generated: Yes (automatic)
- Committed: No (in .gitignore)

**.venv/:**
- Purpose: Python virtual environment for development
- Generated: Yes (created by `python -m venv`)
- Committed: No (in .gitignore)

**node_modules/ (if frontend uses Node.js):**
- Purpose: Frontend dependencies
- Generated: Yes (created by npm/yarn)
- Committed: No (in .gitignore)

**migrations/ (Alembic, if used):**
- Purpose: Database schema version control
- Generated: No (manually created for each schema change)
- Committed: Yes (tracks database evolution)

**.pytest_cache/ and .coverage:**
- Purpose: Test runtime artifacts and coverage reports
- Generated: Yes (created by pytest)
- Committed: No (in .gitignore)

---

*Structure analysis: 2026-02-23*
