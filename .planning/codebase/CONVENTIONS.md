# Coding Conventions

**Analysis Date:** 2026-02-23

## Naming Patterns

**Files:**
- Snake case for all Python modules (e.g., `user_service.py`, `db_config.py`)
- Test files: `test_*.py` pattern (e.g., `test_user_service.py`)
- Directory names: lowercase with underscores

**Functions:**
- Snake case for all function names
- Private functions prefixed with underscore: `_private_function()`
- Test functions: `test_*` pattern (e.g., `test_user_creation`)

**Variables:**
- Snake case for all variable names
- Constants: UPPERCASE_WITH_UNDERSCORES
- Private attributes: prefixed with underscore `_private_attr`

**Types:**
- PascalCase for class names (enforced by N806)
- Type hints required on all functions and parameters (ANN enforcement)
- Docstring conventions: Google style (defined in ruff config)

## Code Style

**Formatting:**
- Tool: Ruff formatter (via pre-commit hook)
- Line length: 120 characters (`tool.ruff.line-length`)
- Automatic fix on commit: enabled (`fix = true`)
- Pre-commit: runs `ruff-format` automatically

**Linting:**
- Tool: Ruff with extensive rule set
- Config location: `pyproject.toml` [tool.ruff.lint]
- Pre-commit hook: `ruff-check` with `--exit-non-zero-on-fix`
- Auto-formatting: enabled at commit time

**Key linting rules:**
- ANN: All functions must have type annotations
- S: Security checks (bandit integration)
- BLE: No bare except clauses
- FBT: Boolean trap detection (no boolean parameters)
- B: Common bug patterns
- A: No Python builtin name shadowing
- C4: List/dict/set comprehension best practices
- DTZ: Timezone-aware datetime objects required
- T10: No debugger statements (pdb, breakpoint)
- SIM: Code simplification suggestions
- EM: Error message format consistency
- LOG: Proper logging usage
- PT: pytest-style best practices
- Q: Quote style consistency (single or double)
- TID: No relative imports
- UP: Modern Python syntax upgrades
- RUF: Additional ruff-specific rules

**Ignored rules:**
- E501: Line too long (line length handled by formatter)
- S311: Non-cryptographic random usage
- D107: Missing docstring in `__init__` (covered by convention)

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**Path conventions:**
- Absolute imports required (TID rule enforcement)
- No relative imports allowed (enforced by TID)
- Import aliases follow convention (ICN enforcement)
- Future annotations: use `from __future__ import annotations`

**Import aliases:**
- `import numpy as np` (conventional)
- `import pandas as pd` (conventional)
- Enforced by flake8-import-conventions (ICN)

## Error Handling

**Patterns:**
- Never use bare `except:` (BLE001 violation)
- Catch specific exceptions: `except ValueError as e:`
- Use context managers for resource management
- All exceptions must be handled with proper error messages (EM rules)
- No generic exception catching without proper logging

**Error messages:**
- Use f-strings in error messages (FLY conversion encouraged)
- Format: descriptive message with context
- Example: `raise ValueError(f"Invalid user ID: {user_id}")`

## Logging

**Framework:** Python standard library `logging` module

**Patterns:**
- Use standard `logging.getLogger(__name__)` pattern
- Never use `print()` for output (enforce via logging)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Format strings properly (LOG rules enforced)
- No string formatting in logging calls - use lazy evaluation

**Example pattern:**
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing user: %s", user_id)
```

## Comments

**When to Comment:**
- Use for WHY not WHAT
- Add context for non-obvious logic
- Explain design decisions
- TODO/FIXME comments flagged by TD/FIX rules in linter

**Docstrings:**
- Google style docstrings required (pydocstyle)
- Applied to all public modules, functions, and classes
- Format: summary line, blank line, detailed description
- Include Args, Returns, Raises sections
- Enforced by D rules (pydocstyle) in ruff

**Example docstring:**
```python
def process_recipe(recipe_id: str) -> dict[str, Any]:
    """Process a recipe by ID.

    Args:
        recipe_id: The unique recipe identifier.

    Returns:
        Dictionary containing processed recipe data.

    Raises:
        ValueError: If recipe_id is invalid.
    """
```

## Function Design

**Size:** Keep functions small and focused (complexity checked via C90/mccabe)

**Parameters:**
- Type annotations required (ANN enforcement)
- Avoid boolean parameters (FBT trap detection)
- Maximum 3-5 positional parameters recommended
- Use keyword-only arguments for optional parameters

**Return Values:**
- Explicit type hints required
- Use type unions for multiple return types
- Prefer `None` return to implicit `None`
- No bare return statements without value

**Example:**
```python
def get_user(user_id: str) -> dict[str, Any] | None:
    """Retrieve user by ID.

    Args:
        user_id: The unique user identifier.

    Returns:
        User data dictionary or None if not found.
    """
    if not user_id:
        return None
    return {"id": user_id}
```

## Module Design

**Exports:**
- Define `__all__` in modules exporting public interfaces
- Use explicit exports, not implicit

**Barrel Files:**
- Use `__init__.py` for package exports
- Re-export main public classes/functions
- Example pattern in `__init__.py`:

```python
from .user_service import UserService
from .db import get_connection

__all__ = ["UserService", "get_connection"]
```

## Code Organization

**Datetime handling:**
- All datetime objects must be timezone-aware (DTZ rules)
- Use `datetime.datetime.now(datetime.UTC)` not `.now()`
- Avoid naive datetime comparisons

**Path handling:**
- Use `pathlib.Path` instead of `os.path` (PTH rules)
- Example: `Path("config") / "settings.json"` not `os.path.join()`

**Comprehensions:**
- Follow C4 (flake8-comprehensions) best practices
- Use generator expressions for large datasets
- Use dict/set comprehensions appropriately

---

*Convention analysis: 2026-02-23*
