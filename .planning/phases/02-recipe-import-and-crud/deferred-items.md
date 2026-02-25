# Deferred Items

Issues discovered during plan execution that are out of scope.

## 02-04: Recipe Annotation Endpoints

### Pre-existing Bug: Parse endpoint model validation

**File:** `src/eat_it/routers/recipes.py` (line 121)
**Test:** `tests/test_recipe_parse.py::test_parse_duplicate_warning`
**Issue:** `RecipePublic.model_validate(existing_recipe)` fails with validation
error because Recipe is a SQLModel instance, not a dict.
**Error:** `pydantic_core._pydantic_core.ValidationError: 1 validation error for
RecipePublic - Input should be a valid dictionary or instance of RecipePublic`
**Fix needed:** Use `RecipePublic.model_validate(existing_recipe.model_dump())` or
`RecipePublic.from_orm(existing_recipe)` pattern.
**Status:** Deferred - not related to annotation endpoints task.
