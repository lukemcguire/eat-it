# Phase 2: Recipe Import and CRUD - Research

**Researched:** 2026-02-25
**Domain:** FastAPI REST API, recipe-scrapers, SQLModel CRUD, data export
**Confidence:** HIGH

## Summary

Phase 2 builds the backend API for recipe management on top of the Phase 1
foundation (SQLModel schemas, database layer, FastAPI app skeleton). The core
technical challenge is integrating the `recipe-scrapers` library for URL parsing
with proper error handling, while implementing standard CRUD patterns with
SQLModel sessions. Export functionality uses FastAPI's `StreamingResponse` for
memory-efficient file generation. The existing `ImporterRegistry` plugin system
already defines the interface for URL importers - we need to implement a
recipe-scrapers-based plugin and the CRUD endpoints.

**Primary recommendation:** Use recipe-scrapers with httpx for async URL parsing,
implement standard SQLModel CRUD patterns with separate Pydantic models for
create/update/public variants, and StreamingResponse for CSV/JSON export.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Import Flow

- **Stateless preview→save**: Client calls /parse, receives parsed data, then
  calls /recipes to save. No server-side preview caching.
- **Minimal parsing metadata**: Return parsed recipe data on success, or
  structured error on failure. No confidence scores or provenance.
- **Structured error responses**: Parsing failures return error code, message,
  and suggested action (e.g., MANUAL_ENTRY_REQUIRED).
- **Partial data handling**: Return what was parsed with null for missing
  required fields. Frontend highlights gaps for user to fill.

#### Duplicate Detection

- **URL-only matching**: Only exact URL match counts as duplicate. No title
  similarity checking.
- **Warning with override**: Return warning with existing recipe info, but allow
  save to proceed with force=true flag.
- **Full comparison data**: Return complete existing recipe when duplicate
  detected so user can compare before deciding.
- **Check at parse time**: Duplicate detection runs during /parse step so user
  sees warning in preview before attempting save.

#### Recipe Validation

- **Minimal required fields**: Only title is required. All other fields
  optional for maximum flexibility.
- **Plain text ingredients**: Ingredients stored as text strings. Schema has
  structured fields but validation doesn't require them (parser populates when
  possible).
- **Strict validation**: Return 422 with specific field errors for invalid
  data. No lenient coercion.
- **Separate annotation endpoints**: Rating and notes have dedicated endpoints
  (PATCH /recipes/{id}/rating, PATCH /recipes/{id}/notes) rather than being
  part of recipe CRUD.

#### Export Design

- **Single endpoint**: /recipes/export?format=json|csv with format as query
  parameter.
- **All fields included**: Export includes all recipe data including metadata.
  No field selection.
- **All recipes only**: No scoped export (no filtering, no selection). Export
  returns entire collection.
- **File download response**: Return with Content-Disposition header for
  browser download behavior.

### Claude's Discretion

- Exact error code values and message wording
- Ingredient text format in CSV export (newline handling)
- Response content type specifics for each format
- Pagination strategy for recipe listing endpoint

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RECIPE-01 | Import recipe by URL with preview and explicit save | recipe-scrapers library with scrape_html + httpx async |
| RECIPE-02 | Manual entry/edit when URL parsing fails | Standard SQLModel CRUD with Pydantic models |
| RECIPE-03 | Add private notes and rating to recipes | PATCH endpoints for rating/notes fields |
| RECIPE-04 | Clear error message and manual-entry fallback | Structured error responses with error codes |
| RECIPE-05 | Warning on duplicate URL import | URL lookup at parse time, warning response |
| RECIPE-06 | Preview parsed data before saving | /parse endpoint returns parsed data only |
| DATA-01 | Export recipes as JSON or CSV | StreamingResponse with Content-Disposition |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| recipe-scrapers | 15.x | URL recipe parsing | 500+ sites, active maintenance, schema.org fallback |
| httpx | 0.27+ | Async HTTP for fetching URLs | Native async, already in dependencies via FastAPI |
| FastAPI | 0.115+ | REST API framework | Already in use from Phase 1 |
| SQLModel | 0.0.16+ | ORM with Pydantic | Already in use from Phase 1 |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| io.StringIO | stdlib | In-memory CSV generation | Export endpoint |
| json | stdlib | JSON serialization | Export endpoint |
| datetime | stdlib | Timestamps | Already in use |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| recipe-scrapers | custom parser | recipe-scrapers handles 500+ sites, wild mode for schema.org |
| StreamingResponse | FileResponse | StreamingResponse for generated content, FileResponse for static files |
| httpx | aiohttp | httpx is already a FastAPI dependency, better API |

**Installation:**

```bash
uv add recipe-scrapers httpx
```

## Architecture Patterns

### Recommended Project Structure

```
src/eat_it/
├── models/
│   ├── recipe.py          # Existing Recipe, Ingredient, IngredientGroup
│   └── __init__.py
├── routers/
│   ├── health.py          # Existing
│   ├── recipes.py         # NEW: CRUD + export endpoints
│   └── __init__.py
├── services/
│   ├── importer_registry.py  # Existing plugin system
│   ├── recipe_parser.py      # NEW: recipe-scrapers wrapper
│   └── __init__.py
├── schemas/
│   ├── recipe.py          # NEW: Pydantic request/response models
│   └── __init__.py
├── main.py                # Add recipes router
├── database.py            # Existing
└── config.py              # Existing
```

### Pattern 1: SQLModel CRUD with Separate Pydantic Models

**What:** Use separate models for Create, Update, and Public (response) variants
to control what fields are accepted/exposed at each operation.

**When to use:** All CRUD endpoints to prevent over-posting and control response
shape.

**Example:**

```python
# schemas/recipe.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Base fields shared across variants
class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    instructions: str = Field(..., min_length=1)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

# Create: all optional fields truly optional, no id/timestamps
class RecipeCreate(RecipeBase):
    pass

# Update: all fields optional for partial updates
class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    instructions: Optional[str] = Field(None, min_length=1)
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None

# Public: includes id and timestamps
class RecipePublic(RecipeBase):
    id: int
    rating: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Source: https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/
```

### Pattern 2: Recipe Parser Service with Error Codes

**What:** Wrap recipe-scrapers in a service class that returns structured
responses with error codes matching CONTEXT.md decisions.

**When to use:** /parse endpoint for URL import.

**Example:**

```python
# services/recipe_parser.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import httpx
from recipe_scrapers import scrape_html, WebsiteNotImplementedError, NoSchemaFoundInWildMode

class ParseErrorCode(str, Enum):
    UNSUPPORTED_WEBSITE = "UNSUPPORTED_WEBSITE"
    NO_RECIPE_FOUND = "NO_RECIPE_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    MANUAL_ENTRY_REQUIRED = "MANUAL_ENTRY_REQUIRED"

@dataclass
class ParseError:
    code: ParseErrorCode
    message: str
    suggested_action: str

@dataclass
class ParseResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[ParseError] = None
    duplicate_warning: Optional[dict] = None  # Existing recipe if URL match

class RecipeParser:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; EatIt/0.1)"}

    async def parse_url(self, url: str) -> ParseResult:
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            scraper = scrape_html(response.text, org_url=url, supported_only=False)

            if not scraper.title():
                return ParseResult(
                    success=False,
                    error=ParseError(
                        code=ParseErrorCode.NO_RECIPE_FOUND,
                        message="No recipe data found at this URL",
                        suggested_action="Enter recipe manually"
                    )
                )

            return ParseResult(
                success=True,
                data=self._scraper_to_dict(scraper, url)
            )

        except httpx.HTTPError as e:
            return ParseResult(
                success=False,
                error=ParseError(
                    code=ParseErrorCode.NETWORK_ERROR,
                    message=f"Failed to fetch URL: {str(e)}",
                    suggested_action="Check the URL or enter recipe manually"
                )
            )
        except (WebsiteNotImplementedError, NoSchemaFoundInWildMode):
            return ParseResult(
                success=False,
                error=ParseError(
                    code=ParseErrorCode.MANUAL_ENTRY_REQUIRED,
                    message="This website is not supported for automatic import",
                    suggested_action="Enter recipe manually using the form"
                )
            )

    def _scraper_to_dict(self, scraper, url: str) -> dict:
        return {
            "title": scraper.title(),
            "description": scraper.description(),
            "instructions": scraper.instructions(),
            "ingredients": scraper.ingredients(),
            "prep_time": scraper.prep_time(),
            "cook_time": scraper.cook_time(),
            "servings": self._parse_yields(scraper.yields()),
            "source_url": url,
            "image_url": scraper.image(),
            "tags": list(scraper.keywords() or []),
        }

    def _parse_yields(self, yields: Optional[str]) -> Optional[int]:
        if not yields:
            return None
        # Parse "8 servings" or "24 cookies" -> extract number
        import re
        match = re.search(r'(\d+)', yields)
        return int(match.group(1)) if match else None
```

### Pattern 3: Streaming CSV/JSON Export

**What:** Use StreamingResponse with generator for memory-efficient export of
large collections.

**When to use:** /recipes/export endpoint.

**Example:**

```python
# routers/recipes.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import io
import csv
import json

from eat_it.database import get_session
from eat_it.models import Recipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/export")
def export_recipes(
    format: str = Query(..., pattern="^(json|csv)$"),
    session: Session = Depends(get_session)
):
    recipes = session.exec(select(Recipe)).all()

    if format == "json":
        def generate_json():
            data = [recipe.model_dump() for recipe in recipes]
            yield json.dumps(data, indent=2, default=str)

        return StreamingResponse(
            generate_json(),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=recipes.json"
            }
        )

    elif format == "csv":
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)

            # Header
            writer.writerow([
                "id", "title", "description", "instructions",
                "prep_time", "cook_time", "servings", "source_url",
                "image_url", "tags", "rating", "notes",
                "created_at", "updated_at"
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

            # Rows
            for recipe in recipes:
                writer.writerow([
                    recipe.id,
                    recipe.title,
                    recipe.description,
                    recipe.instructions.replace("\n", "\\n"),  # Escape newlines
                    recipe.prep_time,
                    recipe.cook_time,
                    recipe.servings,
                    recipe.source_url,
                    recipe.image_url,
                    "|".join(recipe.tags),  # Pipe-separated tags
                    recipe.rating,
                    recipe.notes,
                    recipe.created_at.isoformat(),
                    recipe.updated_at.isoformat(),
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=recipes.csv"
            }
        )
```

### Anti-Patterns to Avoid

- **Returning ORM models directly:** Always use Pydantic response models to
  control what's exposed and avoid lazy-loading issues.
- **Storing parsed data without validation:** recipe-scrapers may return None
  for missing fields - validate before persisting.
- **Synchronous HTTP in async endpoints:** Use httpx async, not requests
  library.
- **Loading all recipes into memory for export:** Use StreamingResponse
  generator pattern to avoid memory issues with large collections.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Recipe URL parsing | Custom HTML parser | recipe-scrapers | Handles 500+ sites, edge cases, schema.org |
| Async HTTP requests | requests + asyncio | httpx | Native async, connection pooling |
| CSV generation | String concatenation | csv module + StringIO | Proper escaping, newline handling |
| File download response | Manual headers | StreamingResponse | Handles chunking, content-length |

**Key insight:** recipe-scrapers has years of accumulated edge-case handling for
recipe sites. Don't underestimate the complexity of parsing diverse HTML
structures.

## Common Pitfalls

### Pitfall 1: Missing recipe-scrapers Wild Mode

**What goes wrong:** Scraper fails on unsupported sites even when they have
schema.org markup.

**Why it happens:** Default `supported_only=True` rejects unknown sites.

**How to avoid:** Always use `supported_only=False` to enable wild mode:

```python
scraper = scrape_html(html, org_url=url, supported_only=False)
```

**Warning signs:** `WebsiteNotImplementedError` for sites that clearly have
recipe markup.

### Pitfall 2: Recipe Model Missing Rating/Notes Fields

**What goes wrong:** CONTEXT.md requires rating and notes endpoints but Recipe
model from Phase 1 doesn't have these fields.

**Why it happens:** Phase 1 model was minimal for schema foundation.

**How to avoid:** Add migration for rating (int, 1-5) and notes (text) fields
to Recipe model before implementing endpoints.

**Warning signs:** 422 errors when trying to set rating/notes.

### Pitfall 3: Ingredient Handling Mismatch

**What goes wrong:** recipe-scrapers returns ingredients as strings but Recipe
model has structured Ingredient/IngredientGroup tables.

**Why it happens:** Parser returns plain strings, not structured data.

**How to avoid:** CONTEXT.md says "plain text ingredients" - store as JSON
array of strings in Recipe model or create a separate path for structured
parsing in Phase 4.

**Warning signs:** Trying to populate Ingredient tables from parser output.

### Pitfall 4: Duplicate Detection Race Condition

**What goes wrong:** Two parses of same URL both show "no duplicate", then both
saves succeed creating duplicates.

**Why it happens:** Check-then-act pattern without transaction isolation.

**How to avoid:** Check at parse time (per CONTEXT.md), but also add unique
constraint on source_url at database level as defense in depth.

**Warning signs:** Multiple recipes with same source_url in database.

## Code Examples

### Full CRUD Endpoint Pattern

```python
# routers/recipes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from eat_it.database import get_session
from eat_it.models import Recipe
from eat_it.schemas.recipe import RecipeCreate, RecipeUpdate, RecipePublic

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/", response_model=RecipePublic, status_code=status.HTTP_201_CREATED)
def create_recipe(
    *,
    session: Session = Depends(get_session),
    recipe: RecipeCreate
):
    """Create a new recipe manually or from parsed URL data."""
    db_recipe = Recipe.model_validate(recipe)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe

@router.get("/", response_model=list[RecipePublic])
def list_recipes(
    *,
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    q: Optional[str] = Query(None, description="Search in title/description")
):
    """List recipes with pagination and optional keyword search."""
    query = select(Recipe).offset(offset).limit(limit).order_by(Recipe.created_at.desc())
    if q:
        query = query.where(
            Recipe.title.contains(q) | Recipe.description.contains(q)
        )
    return session.exec(query).all()

@router.get("/{recipe_id}", response_model=RecipePublic)
def get_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int
):
    """Get a single recipe by ID."""
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.patch("/{recipe_id}", response_model=RecipePublic)
def update_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int,
    recipe: RecipeUpdate
):
    """Update a recipe (partial update)."""
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    update_data = recipe.model_dump(exclude_unset=True)
    db_recipe.sqlmodel_update(update_data)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    *,
    session: Session = Depends(get_session),
    recipe_id: int
):
    """Delete a recipe."""
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    session.delete(recipe)
    session.commit()
```

### Parse Endpoint with Duplicate Detection

```python
@router.get("/parse")
async def parse_recipe_url(
    url: str = Query(..., description="Recipe URL to parse"),
    session: Session = Depends(get_session)
):
    """Parse recipe from URL with duplicate detection."""
    parser = RecipeParser()

    # Check for existing recipe with this URL
    existing = session.exec(
        select(Recipe).where(Recipe.source_url == url)
    ).first()

    result = await parser.parse_url(url)

    if not result.success:
        return {
            "success": False,
            "error": {
                "code": result.error.code.value,
                "message": result.error.message,
                "suggested_action": result.error.suggested_action
            }
        }

    response = {
        "success": True,
        "data": result.data
    }

    if existing:
        response["duplicate_warning"] = {
            "existing_recipe": RecipePublic.model_validate(existing).model_dump()
        }

    return response
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| recipe-scrapers scrape_me() | scrape_html() with httpx | 2024+ | Better async support, explicit HTTP control |
| requests library | httpx async | FastAPI era | Native async, no thread pool overhead |

**Deprecated/outdated:**
- `scrape_me()`: Fetches HTML synchronously, not suitable for async FastAPI

## Open Questions

1. **Should Recipe model add rating/notes fields?**
   - What we know: CONTEXT.md requires PATCH endpoints for these
   - What's unclear: Phase 1 Recipe model doesn't have them
   - Recommendation: Add migration for rating (int nullable, 1-5) and notes
     (text nullable) fields

2. **How to handle ingredients from parser?**
   - What we know: recipe-scrapers returns list of strings
   - What's unclear: Schema has Ingredient/IngredientGroup tables
   - Recommendation: Per CONTEXT.md "plain text ingredients", store as JSON
     array on Recipe model (may need migration) or defer structured parsing
     to Phase 4

## Sources

### Primary (HIGH confidence)

- /hhursev/recipe-scrapers - scrape_html, async usage, error handling
- /fastapi/fastapi - StreamingResponse, dependency injection
- /websites/sqlmodel_tiangolo - CRUD patterns with FastAPI

### Secondary (MEDIUM confidence)

- Project codebase - existing models, database layer, importer registry

### Tertiary (LOW confidence)

- None - all critical information from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - recipe-scrapers is the de-facto standard, well-maintained
- Architecture: HIGH - SQLModel CRUD patterns are well-documented
- Pitfalls: HIGH - based on library documentation and common patterns

**Research date:** 2026-02-25
**Valid until:** 2026-03-25 (libraries are stable)
