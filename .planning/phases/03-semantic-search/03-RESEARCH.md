# Phase 3: Semantic Search - Research

**Researched:** 2026-03-03
**Domain:** Local vector embeddings with sqlite-vec for semantic recipe search
**Confidence:** HIGH

## Summary

Phase 3 implements natural language recipe search using local embeddings stored in
sqlite-vec virtual tables. The project already has the infrastructure in place:
sentence-transformers loaded at startup (all-MiniLM-L6-v2) and sqlite-vec extension
loaded in the database connection. The implementation requires adding an embedding
column strategy, creating a vec0 virtual table for KNN search, and building a search
endpoint that falls back to keyword search when semantic returns no results.

**Primary recommendation:** Use a separate vec0 virtual table (recipe_embeddings) that
stores recipe_id as the rowid and 384-dimensional float vectors from all-MiniLM-L6-v2.
Generate embeddings synchronously on recipe save (title + description + instructions
concatenated). Search endpoint tries semantic first, falls back to existing keyword
search if no results.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Search Input Mode**
- Single unified search field that handles both semantic and keyword queries
- System auto-detects intent (no mode toggle)
- Simple placeholder text ("Search recipes...") - no example hints
- No autocomplete suggestions
- No pre-filtering options - search queries all recipes

**Results Presentation**
- Show top 20 results with relevance score cutoff
- Each result displays: recipe name, source URL, picture thumbnail
- Results sorted by relevance only (no sort options)
- Simple "No recipes found" message when no results

**Fallback Behavior**
- Automatic fallback to keyword search when semantic returns no results
- Silent fallback - user not notified which search type was used
- Fall back to keyword search if semantic search unavailable (e.g., model
  fails to load)
- Search only recipes with embeddings for semantic results; unembedded
  recipes found via keyword fallback

**Embedding UX**
- Generate embeddings immediately when recipe is saved
- Silent generation - no progress indicator or status display
- Recipes are searchable immediately after save (keyword fallback handles
  unembedded state)
- Regenerate embeddings automatically when recipe content changes
- No manual regenerate option

### Claude's Discretion

- Exact relevance score threshold for result cutoff
- How to combine/hybridize results when partial embedding coverage
- Embedding field selection (title only, title + ingredients, full text)
- Keyword search implementation (LIKE queries vs FTS5)

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SEARCH-01 | User can search recipes using natural language queries (e.g., "vegetarian dinner for 4") powered by local embeddings - no internet or API key required | sentence-transformers + sqlite-vec KNN search |
| SEARCH-02 | User can search by keyword or tag as a fallback when embedding search is unavailable | Existing LIKE-based keyword search in list_recipes endpoint |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite-vec | >=0.1.0 | Vector search SQLite extension | Already installed; only local vector DB option for SQLite |
| sentence-transformers | >=3.0 | Local embedding generation | Already installed; all-MiniLM-L6-v2 loaded at startup |
| all-MiniLM-L6-v2 | - | Embedding model (384 dimensions) | Already configured in EAT_IT_EMBEDDING_MODEL; fast + good quality |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| struct | stdlib | Serialize floats to binary for sqlite-vec | When inserting vectors into vec0 table |

**Installation:**
Already installed in pyproject.toml. No new dependencies needed.

## Architecture Patterns

### Recommended Project Structure

```
src/eat_it/
├── services/
│   └── embedding.py       # Embedding generation service
├── routers/
│   └── search.py          # Search endpoint (or extend recipes.py)
└── models/
    └── recipe.py          # Recipe model (no changes needed - uses virtual table)
```

### Pattern 1: Separate vec0 Virtual Table for Embeddings

**What:** Store embeddings in a separate vec0 virtual table with recipe_id as rowid.

**When to use:** When you need fast KNN search without modifying the main schema.

**Example:**

```sql
-- Create virtual table for recipe embeddings
-- 384 dimensions for all-MiniLM-L6-v2
CREATE VIRTUAL TABLE IF NOT EXISTS recipe_embeddings USING vec0(
  embedding FLOAT[384]
);

-- Insert embedding with recipe_id as rowid
INSERT INTO recipe_embeddings(rowid, embedding)
VALUES (1, serialize_f32([0.1, 0.2, ...]));

-- KNN search with JOIN back to recipes
WITH knn AS (
  SELECT rowid as recipe_id, distance
  FROM recipe_embeddings
  WHERE embedding MATCH serialize_f32(query_embedding)
  ORDER BY distance
  LIMIT 20
)
SELECT r.*, k.distance
FROM knn k
JOIN recipes r ON r.id = k.recipe_id
WHERE k.distance < :threshold;
```

Source: https://github.com/asg017/sqlite-vec/blob/main/site/features/knn.md

### Pattern 2: Embedding Generation Service

**What:** Centralized service for generating embeddings using the loaded model.

**When to use:** When multiple places need to generate embeddings.

**Example:**

```python
# src/eat_it/services/embedding.py
import struct
from typing import List

from fastapi import Request


def serialize_f32(vector: List[float]) -> bytes:
    """Serialize a list of floats into compact binary format for sqlite-vec."""
    return struct.pack("%sf" % len(vector), *vector)


def generate_embedding(text: str, request: Request) -> List[float]:
    """Generate embedding for text using the loaded model.

    Args:
        text: Text to embed (concatenated recipe content)
        request: FastAPI request with app.state.embedding_model

    Returns:
        List of 384 floats (all-MiniLM-L6-v2 dimensions)
    """
    model = request.app.state.embedding_model
    if model is None:
        raise RuntimeError("Embedding model not loaded")

    # encode() returns numpy array; convert to list
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def recipe_to_text(recipe) -> str:
    """Convert recipe to text for embedding.

    Combines title, description, and instructions for semantic search.
    Ingredients are excluded to keep embedding focused on dish identity.
    """
    parts = [recipe.title]
    if recipe.description:
        parts.append(recipe.description)
    parts.append(recipe.instructions)
    return " ".join(parts)
```

Source: https://context7.com/huggingface/sentence-transformers/llms.txt

### Pattern 3: Semantic Search with Keyword Fallback

**What:** Try semantic search first, fall back to keyword search if no results.

**When to use:** When you need graceful degradation and partial embedding coverage.

**Example:**

```python
# In search endpoint
async def search_recipes(q: str, session: Session, request: Request) -> List[dict]:
    results = []

    # 1. Try semantic search if model available
    if request.app.state.embedding_model:
        try:
            query_embedding = generate_embedding(q, request)
            query_binary = serialize_f32(query_embedding)

            conn = session.connection().connection
            rows = conn.execute("""
                SELECT rowid as recipe_id, distance
                FROM recipe_embeddings
                WHERE embedding MATCH ?
                ORDER BY distance
                LIMIT 20
            """, [query_binary]).fetchall()

            if rows:
                recipe_ids = [r[0] for r in rows]
                # Fetch recipes by IDs, preserving order
                results = session.exec(
                    select(Recipe).where(Recipe.id.in_(recipe_ids))
                ).all()
        except Exception:
            pass  # Fall through to keyword search

    # 2. Fallback to keyword search
    if not results:
        results = session.exec(
            select(Recipe)
            .where(col(Recipe.title).contains(q) | col(Recipe.description).contains(q))
            .limit(20)
        ).all()

    return results
```

Source: https://github.com/asg017/sqlite-vec/blob/main/examples/nbc-headlines/3_search.ipynb

### Anti-Patterns to Avoid

- **Storing embeddings in the Recipe table as BLOB:** vec0 virtual tables are required
  for KNN search; regular BLOB columns cannot be queried with MATCH
- **Using raw_connection without cleanup:** Always use try/finally to close raw
  connections; context managers don't work with SQLite raw_connection
- **Generating embeddings asynchronously on save:** CONTEXT.md specifies immediate
  synchronous generation; background tasks add complexity without user benefit
- **FTS5 for keyword search:** Existing LIKE queries work; FTS5 adds migration
  complexity for minimal benefit at current scale

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vector similarity search | Custom distance functions | sqlite-vec vec0 MATCH | Optimized C implementation; handles binary serialization |
| Embedding generation | Custom model loading | sentence-transformers | Already loaded in app.state; proven quality |
| Binary vector serialization | Manual byte packing | struct.pack("%sf" % len, *vector) | sqlite-vec expects this exact format |

**Key insight:** sqlite-vec is pre-v1 with potential API changes. The project already
has it working; stick to documented patterns from Context7 examples.

## Common Pitfalls

### Pitfall 1: sqlite-vec API Changes

**What goes wrong:** Code written for older sqlite-vec versions may break.

**Why it happens:** sqlite-vec is pre-v1 with stated breaking-change policy.

**How to avoid:** Use the exact patterns from Context7 docs (already verified); check
vec_version() in tests.

**Warning signs:** Tests failing with "no such function" or "near MATCH: syntax error"

### Pitfall 2: Raw Connection Lifecycle

**What goes wrong:** Unclosed raw connections cause database lock errors.

**Why it happens:** SQLAlchemy's raw_connection() doesn't support context managers.

**How to avoid:** Always use try/finally to close raw connections.

**Example:**

```python
conn = session.connection().connection.dbapi_connection
try:
    conn.execute(...)
finally:
    conn.close()  # NOT in __enter__/__exit__
```

### Pitfall 3: Embedding Dimension Mismatch

**What goes wrong:** Creating vec0 with wrong dimension count causes insert failures.

**Why it happens:** Different models have different output dimensions.

**How to avoid:** all-MiniLM-L6-v2 produces 384 dimensions; hardcode FLOAT[384].

**Warning signs:** "vector dimension mismatch" errors on insert

### Pitfall 4: Missing Embeddings for Existing Recipes

**What goes wrong:** Recipes created before Phase 3 have no embeddings.

**Why it happens:** Embedding generation only runs on save.

**How to avoid:** CONTEXT.md specifies keyword fallback handles unembedded recipes;
no migration needed. Consider a background migration script for bulk embedding.

## Code Examples

### Create vec0 Virtual Table (Migration)

```python
# Alembic migration
def upgrade():
    # Get raw connection for DDL
    op.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS recipe_embeddings
        USING vec0(embedding FLOAT[384])
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS recipe_embeddings")
```

### Generate and Store Embedding on Recipe Save

```python
# In create_recipe endpoint
from eat_it.services.embedding import generate_embedding, serialize_f32, recipe_to_text

@router.post("/", response_model=RecipePublic, status_code=201)
def create_recipe(
    *,
    session: Session = Depends(get_session),
    request: Request,
    recipe: RecipeCreate,
) -> Recipe:
    # Create recipe
    db_recipe = Recipe.model_validate(recipe)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)

    # Generate and store embedding
    if request.app.state.embedding_model:
        try:
            text = recipe_to_text(db_recipe)
            embedding = generate_embedding(text, request)
            embedding_binary = serialize_f32(embedding)

            conn = session.connection().connection.dbapi_connection
            try:
                conn.execute(
                    "INSERT INTO recipe_embeddings(rowid, embedding) VALUES (?, ?)",
                    [db_recipe.id, embedding_binary]
                )
            finally:
                conn.close()
        except Exception:
            pass  # Recipe still searchable via keyword fallback

    return db_recipe
```

Source: https://context7.com/asg017/sqlite-vec/llms.txt

### Search Endpoint with Fallback

```python
# In routers/search.py or extend routers/recipes.py
@router.get("/search", response_model=list[RecipePublic])
def search_recipes(
    *,
    session: Session = Depends(get_session),
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> list[Recipe]:
    """Search recipes with semantic-then-keyword fallback."""
    results: list[Recipe] = []

    # Try semantic search
    if request.app.state.embedding_model:
        try:
            query_embedding = generate_embedding(q, request)
            query_binary = serialize_f32(query_embedding)

            conn = session.connection().connection.dbapi_connection
            try:
                rows = conn.execute(
                    """
                    SELECT rowid as recipe_id, distance
                    FROM recipe_embeddings
                    WHERE embedding MATCH ?
                    ORDER BY distance
                    LIMIT ?
                    """,
                    [query_binary, limit]
                ).fetchall()

                if rows:
                    # Filter by distance threshold
                    THRESHOLD = 1.5  # L2 distance; tune based on testing
                    recipe_ids = [r[0] for r in rows if r[1] < THRESHOLD]

                    if recipe_ids:
                        # Fetch recipes preserving KNN order
                        id_to_distance = {r[0]: r[1] for r in rows}
                        recipes = session.exec(
                            select(Recipe).where(Recipe.id.in_(recipe_ids))
                        ).all()
                        # Sort by distance
                        results = sorted(recipes, key=lambda r: id_to_distance[r.id])
            finally:
                conn.close()
        except Exception:
            pass  # Fall through to keyword

    # Fallback to keyword search
    if not results:
        results = list(session.exec(
            select(Recipe)
            .where(
                col(Recipe.title).contains(q) |
                col(Recipe.description).contains(q) |
                col(Recipe.instructions).contains(q)
            )
            .limit(limit)
        ).all())

    return results
```

Source: https://context7.com/huggingface/sentence-transformers/llms.txt

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| sqlite-vss with Faiss | sqlite-vec pure C | 2024 | Simpler deployment; no external dependencies |
| Cloud embedding APIs | Local sentence-transformers | 2023+ | Privacy-first; no API keys needed |

**Deprecated/outdated:**
- sqlite-vss: Replaced by sqlite-vec; heavier dependency on Faiss

## Open Questions

1. **Distance threshold for relevance cutoff**
   - What we know: L2 distance from sqlite-vec; typical values 0-2 for similar texts
   - What's unclear: Exact threshold for "good enough" recipe matches
   - Recommendation: Start with 1.5, tune based on testing

2. **Embedding text composition**
   - What we know: title + description + instructions is standard
   - What's unclear: Whether to include ingredients (adds noise about components vs identity)
   - Recommendation: Start with title + description + instructions; ingredients excluded

3. **Update vs insert on recipe edit**
   - What we know: CONTEXT.md says regenerate on content change
   - What's unclear: Whether to use UPDATE or DELETE+INSERT in vec0
   - Recommendation: vec0 supports REPLACE (DELETE+INSERT); use recipe_id as rowid

## Sources

### Primary (HIGH confidence)

- /asg017/sqlite-vec (Context7) - KNN patterns, Python serialization, metadata filtering
- /huggingface/sentence-transformers (Context7) - encode() API, all-MiniLM-L6-v2 usage

### Secondary (MEDIUM confidence)

- Existing codebase: main.py (embedding model loading), database.py (sqlite-vec extension),
  routers/recipes.py (existing keyword search pattern)

### Tertiary (LOW confidence)

- N/A - All findings verified with Context7 or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Already installed and working
- Architecture: HIGH - Context7 examples directly applicable
- Pitfalls: HIGH - Based on STATE.md warnings and Context7 docs

**Research date:** 2026-03-03
**Valid until:** 30 days (sqlite-vec pre-v1 may have API changes)
