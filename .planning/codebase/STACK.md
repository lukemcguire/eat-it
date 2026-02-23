# Technology Stack

**Analysis Date:** 2026-02-23

## Languages

**Primary:**
- Python 3.13+ - Core application language,
  backend API, recipe parsing, and AI search

## Runtime

**Environment:**
- Python 3.13 via `.venv` virtual environment
- Uses hatchling as build backend

**Package Manager:**
- Hatchling (via pyproject.toml PEP 517/518)
- Lockfile: Not present (dependencies currently empty,
  will be added during implementation)

## Frameworks

**Core:**
- FastAPI (planned) - REST API for recipe import,
  storage, search, and shopping list management
- React/Vue/Svelte (planned) - Frontend framework for
  responsive web interface (final choice pending)

**Build/Dev:**
- Ruff 0.15.1+ - Code linting and formatting (linter
  and formatter combined)
- pytest 8.0+ - Unit and integration test framework
- pytest-asyncio 0.23+ - Async test support
- pytest-cov 7.0.0+ - Test coverage reporting
- pytest-mock 3.12+ - Mocking support for tests
- pytest-timeout 2.4.0+ - Test timeout enforcement
- pytest-xdist 3.0+ - Parallel test execution
- mkdocs 1.6.1+ - Documentation generation
- mkdocs-material 9.7.1+ - Material theme for docs
- mkdocstrings 1.0.3+ - Auto API documentation
- mkdocstrings-python 2.0.2+ - Python docstring parsing
- ty 0.0.17+ - Type checking (see configuration in
  pyproject.toml)
- prek 0.3.2+ - Pre-commit framework integration

**Type Checking:**
- ty (static type analyzer, configured with Python
  3.13 environment)

## Key Dependencies

**Currently:**
- No production dependencies listed in pyproject.toml
  (empty dependencies array)

**Planned (from PRD):**
- Recipe parser library (e.g., recipe-scrapers or
  equivalent Python recipe parsing solution)
- SQLite or lightweight embedded database for local
  storage
- AI/NLP library for local search (TBD during
  implementation)
- Frontend framework package (React/Vue/Svelte)
- Backend API framework (FastAPI implied by ruff
  FAST rules)

## Configuration

**Environment:**
- Python version: 3.13 (specified in pyproject.toml
  line 6)
- Line length: 120 characters (ruff configuration)
- Environment variables: No .env file present;
  configuration approach TBD

**Build:**
- `pyproject.toml` at project root (`/home/luke/workspace/github.com/lukemcguire/eat-it/pyproject.toml`)
- Hatch build configuration in pyproject.toml
  `[tool.hatch.build.targets.wheel]`

**Linting & Formatting:**
- Ruff v0.15.0+ (pre-commit hook configured)
- Pre-commit configuration: `.pre-commit-config.yaml`

## Code Quality Standards

**Linting Rules (via Ruff):**
- Comprehensive rule set across 29+ rule categories:
  FastAPI, security (Bandit), type annotations,
  naming conventions, docstrings (Google style),
  complexity analysis (McCabe), import ordering,
  and more
- Google-style docstrings required via
  pydocstyle convention
- Tests use relaxed rules: docstrings, annotations,
  and bandit security checks disabled

**Pre-commit Hooks:**
- JSON formatting (pretty-format-json)
- TOML validation (check-toml)
- YAML validation (check-yaml)
- Case and merge conflict checks
- Trailing whitespace and EOL fixes
- Ruff linting and formatting

## Platform Requirements

**Development:**
- Python 3.13+
- Virtual environment (.venv)
- Unix-like shell (bash/zsh preferred; .pre-commit-config uses
  shell features)
- Git (for pre-commit hooks)

**Production:**
- Self-hosted deployment (Docker, binary, or cloud-native
  install planned)
- Minimal hardware: Raspberry Pi or equivalent (per PRD)
- Local storage only (no external cloud services required)

## Notes

- Project is in initial setup phase (commit history shows
  "setup config" and "Initial commit")
- No production dependencies yet; full tech stack will be
  finalized during Phase 1 of PRD implementation
- Strong emphasis on code quality, type safety, and testing
  (evidenced by extensive ruff rules and test framework setup)
- Self-hosted privacy-first architecture (no external
  dependencies for core functionality planned per PRD)

---

*Stack analysis: 2026-02-23*
