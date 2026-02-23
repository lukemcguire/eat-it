# Pitfalls Research

**Domain:** Self-hosted recipe app with local AI search
**Researched:** 2026-02-23
**Confidence:** MEDIUM (domain-specific research verified across
multiple sources; some findings from community discussions)

## Critical Pitfalls

### Pitfall 1: Embedding Index Out of Sync with Database

**What goes wrong:**
Recipes are added, edited, or deleted but the embedding index
(stored separately from SQLite or in a serialised file) is never
updated. Search results surface deleted recipes, miss new ones, or
return stale relevance scores. Worse: if the embedding model is
swapped for a better one, all existing vectors are incompatible and
a full re-index is required — but the code never triggers one
automatically.

**Why it happens:**
Developers treat embedding generation as a one-time setup step at
import time, not as a lifecycle concern. Index synchronisation is
not wired into the recipe create/update/delete paths. Model swaps
are treated like dependency updates — just bump the version.

**How to avoid:**
- Store embeddings in the database alongside recipes (a BLOB
  column on the `recipe` table), not in a separate file or
  in-memory structure. This keeps them transactionally consistent.
- Record the embedding model name and version in a `settings` or
  `schema_version` table. On startup, compare stored model version
  against current — trigger a background re-index if they differ.
- When a recipe is saved or updated, regenerate its embedding in
  the same transaction (or enqueue an immediate background task).
- Expose an admin endpoint `POST /admin/reindex` for manual
  full re-index during upgrades.

**Warning signs:**
- Search returns a recipe you deleted
- Search misses a recipe you just added
- Relevance quality drops after updating the sentence-transformers
  package without re-indexing
- `SELECT COUNT(*) FROM recipe` differs from embedding count

**Phase to address:** Phase 1 (Foundation) — schema design must
include the embedding column and model-version tracking before any
recipe import code is written.

---

### Pitfall 2: SQLite "database is locked" Under Concurrent Writes
in Docker

**What goes wrong:**
Multiple FastAPI requests (concurrent shopping list check-offs from
two shoppers, or a recipe import happening simultaneously with a
list update) hit the SQLite writer at the same time. Without WAL
mode and a busy timeout, one request immediately gets
`SQLITE_BUSY: database is locked`. The failure is intermittent —
works fine in development but surfaces in real grocery-run usage.

**Why it happens:**
SQLite's default journal mode (DELETE/rollback) blocks all readers
while a write is in progress, and writers block all other writers.
FastAPI's async nature means many coroutines can attempt writes
simultaneously. Python's SQLAlchemy/aiosqlite defaults do not set
a busy timeout, so a locked database raises an exception
immediately instead of waiting.

**How to avoid:**
- Enable WAL mode immediately after first connection:
  `PRAGMA journal_mode=WAL`
- Set a busy timeout of at least 5 seconds:
  `PRAGMA busy_timeout=5000`
- Use a single SQLAlchemy engine with `check_same_thread=False`
  and connection pool size of 1 for writes (serialise writes
  through a single connection or use async mutex).
- Mount the SQLite file on a Docker named volume (not a bind-mount
  to a Windows/macOS host filesystem). WAL mode requires shared
  memory between processes; network filesystems and cross-OS
  mounts break this.
- Never share the SQLite file across multiple Docker containers or
  replicas.

**Warning signs:**
- Sporadic 500 errors on `/shopping-list/items` PATCH endpoints
- "database is locked" in logs during peak usage
- Tests pass individually but fail when run in parallel
- Works on Linux Docker but breaks on Docker Desktop for macOS

**Phase to address:** Phase 1 (Foundation) — database setup code
must include WAL mode and busy timeout before any handler is
written.

---

### Pitfall 3: recipe-scrapers Partial Parse Fails Silently

**What goes wrong:**
`recipe-scrapers` returns a partially parsed recipe — title found,
ingredients missing, or instructions split incorrectly — without
raising an exception. The user sees a recipe with blank fields,
wonders if the app is broken, and abandons the import. Worse: if
the app auto-saves before the user reviews, bad data enters the
collection silently.

**Why it happens:**
`recipe-scrapers` raises `SchemaOrgException` or
`ElementNotFoundInWildMode` for completely unsupported sites, but
for sites it "supports" with outdated scrapers, methods like
`.ingredients()` may return an empty list rather than raising.
Developers test with 2–3 URLs and miss this because their test
sites happen to parse cleanly.

**How to avoid:**
- After every parse, validate required fields are non-empty:
  `title`, `ingredients` (list length > 0), `instructions`. If
  any required field is missing, treat the parse as a partial
  failure, not a success.
- Always show a preview/review screen before saving. Never
  auto-save a parsed recipe without user confirmation.
- Classify parse outcomes as: SUCCESS (all required fields),
  PARTIAL (some fields missing — show with warnings), FAILURE
  (exception raised or title missing — show manual entry form
  pre-filled with what was found).
- Test against a fixture set of 20+ diverse URLs from AllRecipes,
  BBC Good Food, Serious Eats, NYT Cooking, and food blogs. Run
  this as a CI check that allows known-partial results.
- Anti-bot measures mean some sites block server-side fetches;
  add a User-Agent header matching a real browser.

**Warning signs:**
- Import "succeeds" but ingredient list is empty
- Instructions are a single string instead of steps
- Certain popular sites always produce blank fields
- Users report "it imported but everything is blank"

**Phase to address:** Phase 1 (Recipe Import) — validation and
preview screen must be built before the happy path is considered
done.

---

### Pitfall 4: Ingredient Text Stored as Raw Strings Blocks
Shopping List Aggregation

**What goes wrong:**
Recipes import ingredient lines as raw strings like `"2 cups all-
purpose flour"` and `"16 oz all-purpose flour"`. The shopping list
generator tries to merge these — they refer to the same ingredient
but string equality fails. The user gets two separate line items
instead of one. Quantity summing is impossible without parsing the
unit and amount out of free text.

**Why it happens:**
Parsing a structured ingredient model (quantity + unit + name +
preparation note) is deferred as "a future enhancement." Raw
strings are fast to store. By the time shopping list aggregation
is built, the schema is already in production and migration is
painful.

**How to avoid:**
- Define a structured ingredient model from day one:
  `{ quantity: float | null, unit: str | null, name: str,
  preparation: str | null, raw: str }`. Store `raw` as the
  fallback for display, but always attempt to parse the
  structured fields at import time.
- Use `ingredient-parser-py` (Python) or NLP to extract quantity,
  unit, and name at import time. Store the result. Accept ~80%
  accuracy — always allow the user to edit.
- Shopping list aggregation: match on normalized `name` (lowercase,
  singular). Sum quantities only when units are compatible (cups +
  cups = OK; cups + oz = show separately with a note). Never
  silently discard unit mismatches.
- Store `canonical_unit` and `canonical_quantity` as nullable
  fields alongside `raw`. If null, display raw and skip
  aggregation for that item.

**Warning signs:**
- Shopping list has 15 items where 6 are duplicate ingredients
  with different units
- "1 can tomatoes" and "14 oz tomatoes" appear as separate items
- Users manually editing every shopping list item after generation

**Phase to address:** Phase 1 (Data Schema) — ingredient model
must be specified in the schema design task, before any recipe
storage or shopping list feature is built.

---

### Pitfall 5: Plugin Directory Scanned at Import Time Causes
Startup Failures and Security Issues

**What goes wrong:**
The plugin discovery mechanism uses `importlib` to scan a
directory and import every Python file it finds. A single
malformed plugin file causes the entire application to fail to
start. A plugin with a name conflict shadows a core module. In a
multi-user deployment, a less-technical user drops a `.py` file in
the plugin folder and crashes the server.

**Why it happens:**
Plugin loading via directory scan or `importlib.import_module` is
simple to implement but fragile. Errors in plugin `__init__` code
propagate to the application startup sequence. No sandboxing or
isolation exists.

**How to avoid:**
- Wrap each plugin load in a `try/except` that logs the error and
  skips the plugin — never let one bad plugin kill startup.
- Use a registry pattern: plugins call `register(plugin_class)`
  rather than being auto-instantiated on import.
- Define a strict interface (abstract base class or Protocol) for
  each plugin type (Importer, Exporter, SearchProvider). Validate
  the interface at registration time, reject non-conforming
  plugins with a clear error log entry.
- For MVP: use Python entry points (`pyproject.toml`
  `[project.entry-points]`) for first-party plugins rather than
  directory scanning. Directory scanning can be added in Phase 2
  with proper sandboxing.
- Document that the plugin directory is trusted code execution.
  Do not expose it to untrusted network paths.

**Warning signs:**
- App fails to start after adding a new plugin
- A plugin's import error message refers to an unrelated module
- `AttributeError` at startup because a plugin didn't implement
  the full interface

**Phase to address:** Phase 1 (Architecture) — plugin interface
and loading mechanism must be designed before any concrete
importer is written; the first importer IS the validation of the
plugin system.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Store embeddings in a flat `.npy` file | Fast to ship | Desync from DB on crash; hard to query partially; full reload on restart | Never — store in DB from day 1 |
| Raw ingredient strings only | Simple import | Shopping list aggregation impossible without migration | Never — parse at import, store both raw and structured |
| Skip Alembic, use `CREATE TABLE IF NOT EXISTS` | No migration tooling | Cannot evolve schema on existing installs without data loss | MVP only if schema is certain not to change; add Alembic before first public release |
| Single SQLite connection (no WAL) | Simple setup | Concurrent requests deadlock | Never in Docker deployment |
| Load embedding model on first search request | Simple startup | 5–30s delay on first search, poor UX | Only in dev; pre-load on startup in production |
| Ingredient strings, no structured parse | Fastest import | Aggregation broken, search quality degraded | Never — parse at import time even if imperfect |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| recipe-scrapers | Catch only exceptions; treat empty lists as success | Validate all required fields post-parse; classify as SUCCESS, PARTIAL, or FAILURE |
| recipe-scrapers | Fetch URL in same process as API handler | Fetch with httpx async client; set browser User-Agent; set timeout; handle SSL errors and bot blocks |
| sentence-transformers | Import model at module level (blocks startup) | Load model lazily on first call but pre-warm on startup with a dummy encode |
| sentence-transformers | Ship container without model pre-downloaded | Bake model into Docker image or volume-mount model cache; never rely on Hugging Face download at runtime on Raspberry Pi |
| SQLite + Docker | Bind-mount DB file to macOS/Windows host directory | Use named Docker volume on Linux filesystem; document this constraint explicitly |
| Alembic + SQLite | Use `op.alter_column()` directly | Always use `with op.batch_alter_table()` context manager for any column change in SQLite |
| Alembic + SQLite | Migrate TEXT to JSON column with CAST | Copy column data directly without CAST; SQLite maps `CAST(x AS JSON)` to `0`, causing data loss |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full embedding re-index on every startup | Startup takes 2–10 min on Raspberry Pi for 500+ recipes | Store model version; only re-index on model change | 200+ recipes |
| Synchronous embedding generation during HTTP request | Import endpoint times out; UI spinner forever | Generate embedding in background task after save; return recipe immediately | Any collection size |
| `np.dot` similarity computed in Python loop over all recipes | Search takes >5s for 1000 recipes | Use `numpy` vectorized cosine similarity over full embedding matrix; keep matrix in memory | 500+ recipes |
| No SQLite WAL mode, single writer | Intermittent 500 errors under multi-user shopping | Enable WAL + busy timeout before first write | 2+ concurrent users |
| Model loaded from Hugging Face on first request (no cache) | First search after cold start takes 30–120s | Pre-download model into Docker image layer | Every cold start |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Shopping list share link is a sequential integer ID (`/list/42`) | Any user who guesses IDs can read other families' lists | Use UUIDs or short random tokens (8+ chars) for share links |
| Plugin directory writable via Docker volume mount exposed to network | Remote code execution if network share is compromised | Plugin directory should be read-only at runtime; document that it requires trusted file access |
| Recipe import fetches arbitrary URLs without validation | SSRF: attacker pastes internal network URL (`http://192.168.1.1/admin`) | Validate that import URLs are public HTTP/HTTPS; block RFC1918 ranges; set aggressive fetch timeout |
| No HTTPS enforcement on self-hosted instance | Shopping list credentials and session tokens sent in plain text on LAN | Document HTTPS setup; provide example Caddy/nginx reverse proxy config; warn if running HTTP in production |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Check-off state lost on page refresh (stored only in React state) | Shopper loses progress if they switch apps during grocery run | Persist check-off to server immediately on tap; optimistic UI update with background sync |
| Tap target for check-off is the checkbox only (16px) | Impossible to tap accurately while holding groceries | Make the entire list item row the tap target (min 44px height per Apple HIG) |
| Shopping list sorted alphabetically by default | Shopper walks back and forth in store following alphabetical order | Group by grocery category or aisle; allow manual reordering |
| Import preview shows raw JSON from parser | Confusing for non-technical users | Show a clean form pre-filled from parsed fields; highlight empty/missing fields in orange |
| Search returns zero results for "pasta dinner" when recipe is titled "Spaghetti Carbonara" | User thinks search is broken | Embedding search handles semantic mismatch; ensure embeddings are generated from full recipe text (title + ingredients + description), not title only |
| Mobile keyboard pushes shopping list items off screen | Items above keyboard are unreachable | Use `dvh` CSS units or explicit viewport height handling; test on iOS Safari specifically |

---

## "Looks Done But Isn't" Checklist

- [ ] **Recipe import:** Partial parse (empty ingredients) shows
  success — verify validation rejects empty required fields
- [ ] **Search:** Works with 5 recipes — verify with 500 recipes
  that embedding matrix is loaded into memory, not re-computed per
  query
- [ ] **Search:** Model loads on first query — verify model is
  pre-warmed on startup so first user doesn't wait 30s
- [ ] **Shopping list check-off:** Optimistic UI works — verify
  that a page refresh after check-off restores checked state from
  server, not just local state
- [ ] **Shopping list sharing:** Link works — verify link token is
  a UUID/random string, not a sequential integer
- [ ] **Docker deployment:** Works on developer machine — verify
  on a named Docker volume (not bind-mount to macOS host filesystem)
  with WAL mode enabled
- [ ] **Plugin loading:** First plugin registers — verify that a
  malformed second plugin does not crash startup
- [ ] **Schema migration:** Initial migration runs — verify that
  adding a `metadata` JSON column to `recipe` table with existing
  rows uses batch mode and does not lose data
- [ ] **Embedding consistency:** Embeddings exist — verify that
  adding/editing/deleting a recipe updates the embedding in the
  same transaction

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Stale embedding index | LOW | Add model-version check to startup; trigger `POST /admin/reindex`; runs in background |
| Raw-string-only ingredients already in production | HIGH | Migration required: re-parse all ingredient strings, add structured columns, backfill; accept ~20% nulls for unparseable items |
| SQLite corrupt after Docker volume issue | MEDIUM | Restore from SQLite backup file (`.backup` API); document backup schedule in ops guide |
| Plugin crash on startup | LOW | Wrap load in try/except; bad plugin skipped; logged clearly; app starts normally |
| Shopping list state lost (no server persistence) | MEDIUM | Add server-side check-off persistence; existing users lose in-progress lists once (acceptable tradeoff) |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-----------------|--------------|
| Embedding index out of sync | Phase 1 — schema design | Recipe CRUD triggers embedding update; delete removes embedding; startup checks model version |
| SQLite locked under Docker | Phase 1 — DB setup | Integration test: 10 concurrent PATCH requests to shopping list items with zero 500 errors |
| Partial parse silent success | Phase 1 — recipe import | Unit test: parse result with empty ingredients is classified PARTIAL; preview screen shows warning |
| Raw ingredient strings block aggregation | Phase 1 — schema design | Shopping list with 2 recipes sharing an ingredient shows 1 merged line, not 2 |
| Plugin crash kills startup | Phase 1 — plugin architecture | Test: malformed plugin in directory; app starts; error logged; plugin skipped |
| Embedding cold start 30s | Phase 1 — startup | Server startup logs model load time; first search completes in <2s after startup |
| iOS Safari check-off lost on refresh | Phase 2 — shopping list | Manual test on iOS Safari: check 3 items, reload page, items remain checked |
| Alembic/SQLite JSON column data loss | Phase 1 — migrations | Migration test: seed 10 recipes with metadata, run migration, verify all metadata intact |
| SSRF via recipe import URL | Phase 1 — recipe import | Unit test: internal network URL returns 400 Bad Request |
| Share link as sequential integer | Phase 2 — collaboration | Code review: share token generation uses `secrets.token_urlsafe(8)` or UUID4 |

---

## Sources

- recipe-scrapers GitHub issues tracker (partial parse failure
  patterns, site-specific breakage): https://github.com/hhursev/recipe-scrapers/issues
- SQLite WAL mode official documentation:
  https://sqlite.org/wal.html
- "SQLite concurrent writes and database is locked errors":
  https://tenthousandmeters.com/blog/sqlite-concurrent-writes-and-database-is-locked-errors/
- "How to Run SQLite in Docker" (volume and WAL mode pitfalls):
  https://oneuptime.com/blog/post/2026-02-08-how-to-run-sqlite-in-docker-when-and-how/view
- Alembic batch migrations for SQLite documentation:
  https://alembic.sqlalchemy.org/en/latest/batch.html
- Alembic issue #697 — TEXT to JSON migration data loss in SQLite:
  https://github.com/sqlalchemy/alembic/issues/697
- Mealie discussion — ingredient parsing accuracy limits (~80%)
  and structured schema approach:
  https://github.com/mealie-recipes/mealie/discussions/694
- Python plugin architecture pitfalls (entry points, stale data,
  load failures): https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
- DagShub — common vector database pitfalls (model version /
  dimension mismatch, stale embeddings):
  https://dagshub.com/blog/common-pitfalls-to-avoid-when-using-vector-databases/
- PWA iOS Safari limitations (touch events, data persistence, no
  auto install prompt): https://brainhub.eu/library/pwa-on-ios
- sentence-transformers on Raspberry Pi (model pre-download, local
  path loading): https://pypi.org/project/sentence-transformers/

---
*Pitfalls research for: self-hosted recipe app with local
AI search (Eat It)*
*Researched: 2026-02-23*
