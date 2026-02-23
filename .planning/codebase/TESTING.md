# Testing Patterns

**Analysis Date:** 2026-02-23

## Test Framework

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` [tool.pytest.ini_options]

**Assertion Library:**
- pytest built-in assertions (assert statements)

**Async Testing:**
- pytest-asyncio >= 0.23
- asyncio_mode: auto (runs async tests automatically)

**Run Commands:**
```bash
pytest                          # Run all tests
pytest -m "not integration"     # Run unit tests only
pytest -v                       # Verbose output
pytest --cov                    # With coverage report
pytest -x                       # Stop on first failure
pytest -n auto                  # Parallel execution (pytest-xdist)
```

## Test File Organization

**Location:**
- Co-located with source code: same directory structure
- Dedicated tests directory: `/tests/` (testpaths configured)

**Naming:**
- Pattern: `test_*.py` (e.g., `test_user_service.py`)
- Test functions: `test_*` (e.g., `test_user_creation_success`)
- Test classes: `Test*` (e.g., `TestUserService`)

**Structure:**
```
tests/
├── test_user_service.py       # Unit tests for UserService
├── test_db_config.py          # Unit tests for database config
├── integration/
│   ├── test_user_workflow.py  # Integration tests
│   └── test_recipe_flow.py
└── fixtures/
    ├── conftest.py            # Shared fixtures
    └── factory.py             # Test data factories
```

## Test Structure

**Suite Organization:**

All tests use pytest's function-based and class-based patterns:

```python
# Function-based tests
def test_user_creation_with_valid_data() -> None:
    """Test creating user with valid parameters."""
    user = create_user(name="John", email="john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

# Class-based tests for organization
class TestUserService:
    """Tests for UserService class."""

    def test_get_user_success(self) -> None:
        """Test successful user retrieval."""
        # Arrange
        user_id = "123"
        # Act
        user = UserService().get_user(user_id)
        # Assert
        assert user is not None

    def test_get_user_not_found(self) -> None:
        """Test user not found returns None."""
        user = UserService().get_user("nonexistent")
        assert user is None
```

**Patterns:**
- Arrange/Act/Assert (AAA pattern) - structure test logic
- Test one thing per test function
- Use descriptive test names that explain the scenario
- Setup fixtures for shared test data
- Teardown handled via pytest fixtures with yield

**Fixtures Pattern:**

```python
import pytest
from pytest_mock import MockerFixture

@pytest.fixture
def mock_database() -> Generator[MagicMock, None, None]:
    """Provide mocked database connection."""
    with patch('module.get_connection') as mock_db:
        yield mock_db

@pytest.fixture
async def user_data() -> dict[str, Any]:
    """Provide test user data."""
    return {"id": "123", "name": "Test User"}
```

## Mocking

**Framework:** pytest-mock >= 3.12

**Patterns:**
```python
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, patch, call

def test_service_calls_database(mocker: MockerFixture) -> None:
    """Test service calls database correctly."""
    # Mock the dependency
    mock_db = mocker.patch('module.database.get_connection')
    mock_db.return_value = {"status": "ok"}

    # Call the code under test
    result = service.get_data()

    # Assert the mock was called correctly
    mock_db.assert_called_once()
    assert result == {"status": "ok"}

def test_multiple_calls(mocker: MockerFixture) -> None:
    """Test multiple calls to mocked function."""
    mock_logger = mocker.patch('module.logger.info')

    some_function()

    # Verify call count and arguments
    assert mock_logger.call_count == 2
    mock_logger.assert_any_call("First log")
    mock_logger.assert_any_call("Second log")
```

**What to Mock:**
- External API calls (HTTP requests)
- Database connections
- File I/O operations
- External services
- System calls

**What NOT to Mock:**
- Core business logic
- Data structures
- Utilities that are part of the code under test
- Standard library functions (unless testing error handling)
- Internal application logic

## Fixtures and Factories

**Test Data:**

Use pytest fixtures for setup and factories for complex objects:

```python
# fixtures/conftest.py
import pytest
from datetime import datetime, timezone

@pytest.fixture
def user_fixture() -> dict[str, Any]:
    """Standard user test data."""
    return {
        "id": "user-123",
        "name": "Test User",
        "email": "test@example.com",
        "created_at": datetime.now(timezone.utc)
    }

@pytest.fixture
def recipe_fixture() -> dict[str, Any]:
    """Standard recipe test data."""
    return {
        "id": "recipe-456",
        "title": "Test Recipe",
        "ingredients": ["flour", "sugar"],
        "servings": 4
    }

# Factory pattern for complex objects
class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        name: str = "Default User",
        email: str | None = None
    ) -> User:
        """Create a User instance with defaults."""
        return User(
            name=name,
            email=email or f"{name.lower()}@example.com"
        )
```

**Location:**
- Shared fixtures: `tests/conftest.py` (pytest discovers automatically)
- Module-specific fixtures: in test file or `tests/fixtures/`
- Factories: `tests/fixtures/factory.py`

## Coverage

**Requirements:** Not strictly enforced in config

**Tool:** pytest-cov >= 7.0.0

**View Coverage:**
```bash
pytest --cov                    # Display coverage summary
pytest --cov --cov-report=html  # Generate HTML report
pytest --cov=src                # Coverage for specific module
```

**Configuration:**
- Branch coverage enabled (`branch = true`)
- Source coverage: everything (`source = ["."]`)
- Skip empty files (`skip_empty = true`)

## Test Types

**Unit Tests:**
- Test individual functions/methods in isolation
- Use mocks for external dependencies
- Location: `tests/test_*.py`
- Fast execution
- High coverage expected

**Integration Tests:**
- Test interaction between components
- Use real database or in-memory alternatives
- Location: `tests/integration/`
- Marked with `@pytest.mark.integration`
- Run separately: `pytest -m integration`

**E2E Tests:**
- Not currently configured
- Can be added using pytest and external tools

## Markers

**Custom Markers:**

Defined in `pyproject.toml`:
- `integration`: Marks tests as integration tests
  - Usage: `@pytest.mark.integration`
  - Run: `pytest -m integration`
  - Exclude: `pytest -m "not integration"`

## Test Timeouts

**Configuration:**
- Timeout: 60 seconds per test (pytest-timeout)
- Prevents hanging tests
- Configure via `addopts = "--timeout=60"`

## Async Testing

**Pattern:**

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation() -> None:
    """Test async function."""
    result = await async_function()
    assert result is not None

# Or without decorator (asyncio_mode = "auto")
async def test_auto_async() -> None:
    """Async test runs automatically."""
    result = await some_async_call()
    assert result == expected
```

## Common Patterns

**Testing Exceptions:**
```python
def test_invalid_input_raises_error() -> None:
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError, match="Invalid ID"):
        process_user("")

def test_database_error_handling() -> None:
    """Test handling of database errors."""
    with pytest.raises(DatabaseError):
        service.get_data()
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("input_val,expected", [
    ("123", 123),
    ("abc", ValueError),
    ("", ValueError),
])
def test_parse_id(input_val: str, expected: Any) -> None:
    """Test ID parsing with multiple inputs."""
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            parse_id(input_val)
    else:
        assert parse_id(input_val) == expected
```

**Testing with Fixtures:**
```python
def test_user_service_with_fixture(
    user_fixture: dict[str, Any],
    mocker: MockerFixture
) -> None:
    """Test using fixture and mock."""
    mock_db = mocker.patch('db.get_user')
    mock_db.return_value = user_fixture

    service = UserService()
    user = service.get_user("123")

    assert user["name"] == "Test User"
    mock_db.assert_called_once_with("123")
```

## Import Mode

**Configuration:**
- Import mode: `importlib` (not default namespace)
- Ensures proper sys.path handling
- Allows absolute imports from project root

## Pre-commit Integration

**Linting Rules for Tests:**

Tests have relaxed linting rules in `pyproject.toml` [tool.ruff.lint.per-file-ignores]:
- D: Docstring requirements relaxed (tests don't need docstrings)
- S101: `assert` statements allowed (pytest assertion)
- ANN: Type annotations optional for test code
- BLE: Bare except allowed in test error handling
- SLF001: Private member access allowed for testing
- S603: subprocess calls allowed without shell=False
- ARG001/ARG002: Unused arguments allowed (mock signatures)
- DTZ001/DTZ005: Naive datetime allowed in fixtures
- PT011: Broad pytest.raises allowed
- RUF059: Unpacked variable unused allowed

---

*Testing analysis: 2026-02-23*
