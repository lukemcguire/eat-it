# Codebase Concerns

**Analysis Date:** 2026-02-23

## Pre-Implementation Architectural Risks

**Extensibility Foundation (Critical):**
- Issue: PRD and future features planning explicitly emphasize extensibility
  (plugin API, modular handlers), but implementation has not yet begun. Risk
  is high that quick MVP shortcuts (ad-hoc data fields, tightly coupled
  imports, monolithic handlers) will be taken under 4-week deadline, making
  future plugins and AI/OCR extensions costly to retrofit.
- Impact: Blocks Phases 2–3 roadmap (OCR import, real-time collab, plugin
  API). Forces major refactoring once plugins are attempted.
- Fix approach: Before any implementation, design and document core data
  schemas (Recipe, ShoppingList with metadata/extras fields), API handler
  registry pattern, and plugin discovery/event system. Build one dummy
  plugin during MVP to validate extensibility (even if not shipped).

**Data Schema Underspecification (High):**
- Issue: PRD lists requirements for recipes (title, ingredients, steps,
  notes, ratings) and shopping lists (items, quantities, units, check-off
  state) but does not define how ingredient normalization, unit conversion,
  or deduplication logic will work at the schema level.
- Impact: Without clear ingredient format, shopping list aggregation will
  fail (e.g., "2 cups flour" vs "16 oz flour" won't merge). Will force
  mid-sprint rewrites.
- Fix approach: Spec ingredient model before building: decide on canonical
  units, quantity representation, source parser field to trace origin, and
  metadata structure for AI tagging. Consider schema migration support from
  day one (versioned models).

## Tech Stack & Parser Integration Risks

**Recipe Parser Dependency (High):**
- Issue: PRD specifies "use existing open-source recipe parsers" but does
  not select or evaluate which parser library to integrate (e.g.,
  recipe-scrapers Python package, Node.js alternatives). No fallback parser
  strategy.
- Impact: If chosen parser has low success rate or poor license
  compatibility, will consume days of integration time late in sprint.
  Parser errors must degrade gracefully to manual entry; unclear how.
- Fix approach: Spike parser selection and integration immediately. Test
  against 20+ real recipe URLs from target sites (AllRecipes, Food Network,
  Serious Eats, etc.). Document parse success rates and error modes. Plan
  fallback UI for partial parses.

**Lightweight AI Search (High):**
- Issue: PRD requires "AI-powered natural language search" but does not
  specify implementation (embedding model, local vs. cloud, search
  algorithm). "Local/integrated AI" suggests on-device, but feasibility
  unclear for self-hosted Raspberry Pi.
- Impact: Embedding generation, vector database, or simple keyword fallback
  are radically different implementations. Choosing wrong approach blocks
  search feature entirely.
- Fix approach: Prototype search with two approaches: (1) lightweight local
  embeddings (e.g., sentence-transformers + FAISS or SQLite FTS), (2)
  keyword + metadata filters. Measure performance and accuracy on 100+
  recipes. Decide before MVP implementation starts.

**Database Choice (Medium):**
- Issue: PRD mentions "SQLite, flat files" but does not decide. Flat-file
  JSON will scale poorly past ~100 recipes; SQLite may be overkill for MVP
  and requires setup on self-hosted environments.
- Impact: Late switch between JSON and SQLite mid-sprint. File I/O
  concurrency issues on multi-user access.
- Fix approach: Select SQLite early—it's battle-tested for self-hosting,
  has no external dependencies, and supports concurrent reads. Design
  schema to allow future document-style storage (JSON fields for extensibility).

## Data Privacy & Compliance Gaps

**Browser Storage Security (Medium):**
- Issue: PRD requires multi-device access ("accessible from multiple
  browsers/devices") and implies in-browser state management for
  collaboration. No mention of localStorage encryption, session
  token/cookie security, or XSS prevention.
- Impact: User recipes and shopping lists stored in plain-text browser
  storage or cookies. Risk of data leakage if device is shared, or if
  front-end is compromised.
- Fix approach: Use secure, httpOnly cookies for session tokens (not
  localStorage). Encrypt sensitive data at rest if stored client-side.
  Document security model for self-hosters. Add HTTPS enforcement for
  self-hosted deployments.

**User Data Export & Deletion (Medium):**
- Issue: PRD mentions "export/backup" but does not specify format, retention
  policy, or deletion mechanism. Users expect to be able to export all data
  as JSON/CSV and delete accounts cleanly.
- Impact: Missing API endpoints or no clear data cleanup path on user request.
  Could create user frustration and compliance issues if adopted widely.
- Fix approach: Build export endpoint (JSON + CSV) into MVP. Design account
  deletion to cascade-delete all user recipes and list items. Add data
  retention policy to docs.

## Testing & Quality Coverage Gaps

**Parser Failure Resilience (High):**
- Issue: PRD states "errors are handled gracefully" but does not define
  test coverage or error handling strategy. Recipe import is a critical
  user flow; no mention of unit tests for parser mocking or fallback paths.
- Impact: Parser crashes will kill imports. Users cannot complete manual
  fallback if error pages are opaque.
- Fix approach: Test strategy must include: parser success/failure mocking,
  partial parse recovery (UI shows fields, user edits), and user-facing error
  messages. Aim for 100% test coverage on import handler.

**Multi-User / Concurrency Testing (Medium):**
- Issue: PRD requires shared shopping list access from multiple devices,
  but no test plan exists for concurrent edits (two users checking items
  simultaneously, conflicting updates).
- Impact: Lost updates, race conditions, or data corruption if testing is
  deferred. "Refresh to sync" behavior is implicit but untested.
- Fix approach: Define concurrency model early (last-write-wins, or
  transaction isolation). Write integration tests for simultaneous list
  updates from multiple clients. Document expected behavior (e.g., "if you
  and a partner both check item X, last to submit wins").

**Mobile Browser Compatibility (Medium):**
- Issue: PRD emphasizes "mobile-first" and "shopping-optimized," but no
  browser/device test matrix. Shopping list uses "tap to check" and large
  tap targets—must be tested on real devices (iOS Safari, Android Chrome).
- Impact: Shopping list unusable on some devices (e.g., iOS Safari quirks,
  touch event handling). User frustration during MVP launch.
- Fix approach: Test on minimum 3 devices/browsers: iOS Safari, Android
  Chrome, mobile Firefox. Use BrowserStack or local devices. Validate
  touch-event handling and tap-target sizes (minimum 44x44px).

## Deployment & Self-Hosting Friction

**Docker / Single-Binary Distribution (Medium):**
- Issue: PRD targets self-hosters and mentions "docker-compose, single
  binary" deployment, but no decision made. No Dockerfile, compose file,
  or build pipeline in repo yet.
- Impact: "Simple setup" is promised but not de-risked. If deployment is
  complex, adoption stalls immediately.
- Fix approach: Publish docker-compose.yml in MVP. Test end-to-end deploy
  on fresh machine. Document required ports, environment variables, initial
  setup steps. Consider multi-architecture builds (x86, ARM for Raspberry
  Pi).

**Backup & Restore Mechanism (Medium):**
- Issue: PRD mentions users want backups/exports, but no mechanism designed.
  If user loses self-hosted instance, all recipes/lists are gone.
- Impact: Users lose trust if data is not recoverable. No simple backup
  diminishes self-hosting appeal.
- Fix approach: Implement automated daily/weekly backups (snapshot SQLite
  DB). Provide one-click restore. Document manual backup export (JSON dump).
  Consider S3 or similar optional cloud backup path for future (not MVP).

## Scaling & Performance Assumptions

**Search Performance Limits (Medium):**
- Issue: PRD specifies "fast, <1s search for up to several thousand saved
  recipes," but no perf testing plan. Embedding-based search can be slow
  without proper indexing.
- Impact: If search takes >2s on 500 recipes, UX breaks and MVP is
  perceived as slow.
- Fix approach: Load test search with 500–1000 recipes during dev.
  Implement caching or pre-indexed embeddings. Profile and optimize hot
  paths. Publish perf benchmarks in docs.

**Concurrent User Capacity (Low):**
- Issue: PRD targets "5–10 concurrent users per self-host" but does not
  define load test targets or connection pooling. SQLite has single-writer
  limitation.
- Impact: If many users check off list items simultaneously, SQLite write
  locks could cause timeouts.
- Fix approach: Test with simulated 10+ concurrent users checking items.
  Document expected behavior and upgrade path if load increases. Consider
  WAL (Write-Ahead Logging) mode for SQLite to improve concurrency.

## Future-Proofing Shortcomings

**Plugin System Not Designed (Medium):**
- Issue: Future roadmap demands plugin/extension API for OCR, AI tagging,
  video parsing, but MVP has no plugin discovery or registration mechanism
  planned.
- Impact: Once MVP ships, retrofitting a plugin system is expensive. Early
  shortcuts (monolithic handlers, magic string fields) will break plugins.
- Fix approach: Design lightweight plugin registry even if not exposed in
  MVP. Define handler interfaces (importer, exporter, search provider,
  event subscriber). Use Python entry points or Node.js-style module
  loading to support future plugin loading.

**AI/Tagging Metadata Structure (Medium):**
- Issue: Stretch roadmap includes AI tagging (cuisine, difficulty,
  allergen, cook time), but MVP schema does not reserve space for metadata.
  Recipe model will likely have only title, ingredients, steps, notes.
- Impact: If metadata is crammed into notes or a generic "extras" field
  without structure, future AI tagger will parse unreliable formats.
- Fix approach: Define Recipe.metadata field with schema versioning.
  Reserve fields for future: cuisine (list), difficulty (enum), cook_time
  (minutes), prep_time, allergens, dietary_restrictions, etc. Initialize
  as null/empty. Document for future extension.

**Video Recipe Parsing Not Considered (Low):**
- Issue: Developer's reordered roadmap includes "automatic parsing from
  video recipes (Instagram/TikTok/YouTube)" but technical approach is
  undefined and likely very complex (video downloading, frame extraction,
  OCR or ML).
- Impact: If promising users video import before MVP architecture supports
  it, implementation becomes nearly impossible.
- Fix approach: Do not promise video import in MVP or early phases. Design
  API layer to allow future video importer plugin, but spike OCR image
  import first (Phase 1 stretch goal). Document video import as Phase 4+.

## Development Process & Team Risks

**4-Week MVP Timeline Pressure (High):**
- Issue: Project targets "2–4 weeks" solo build for Recipe import, storage,
  search, shopping list, mobile UI, testing, and docs. This is aggressive
  and leaves no buffer for parser integration delays or QA blockers.
- Impact: Shortcuts on testing, docs, or extensibility. Burnout if parser
  selection or search implementation slips.
- Fix approach: Identify critical path: (1) parser spike, (2) data schema &
  DB setup, (3) core APIs, (4) UI, (5) testing. Run parser spike in week 0
  (before week 1 starts). If parser integration takes >2 days, descope AI
  search to keyword-only and defer to Phase 2.

**No Test Environment Strategy (Medium):**
- Issue: PRD does not mention CI/CD, test environment setup, or
  staging/production separation. pyproject.toml includes pytest and ruff,
  but no GitHub Actions or test database fixture plan.
- Impact: Tests may pass locally but fail in CI. Multi-user testing cannot
  happen without staging environment. Deployment is manual and error-prone.
- Fix approach: Set up GitHub Actions CI to run pytest + ruff on each
  commit. Use pytest fixtures for in-memory DB or temp SQLite for tests.
  Define staging deploy target (separate from production) for manual
  multi-user testing before release.

**Documentation Debt (Medium):**
- Issue: PRD targets "simple setup instructions" and promises "API docs for
  future add-ons" but no doc plan exists. MVP likely ships without
  architecture docs, API reference, or plugin guide.
- Impact: Users struggle with self-hosting setup. Future contributors
  cannot understand extensibility architecture. Community adoption slows.
- Fix approach: Build docs as code (mkdocs in pyproject.toml is ready).
  Maintain: architecture overview, API endpoint reference, data schema
  diagram, self-hosting guide, and plugin template. Ship with MVP.

## Known Unknowns & Decisions Pending

**Recipe Import Workflow Decision (High Priority):**
- PRD explicitly flags: "Should newly parsed recipes be added
  automatically (user can remove), or require explicit save action?"
  Decision impacts UX complexity and error handling flow.
- Fix approach: Decide before UI implementation. Recommend "auto-add with
  review screen" (parsed recipe shown; user edits fields, then clicks
  save). Balances speed with accuracy.

**User Authentication / Multi-Tenancy (Medium Priority):**
- PRD mentions "optional local login or single-user mode with shareable
  link/PIN," but no design for multi-user isolation or auth mechanism.
- Fix approach: Decide: (1) single-user mode (no login, recipes/lists are
  global), or (2) optional local user account with PIN/basic password. If
  multi-user, add user_id foreign key to recipes/lists. Design token/cookie
  flow for shopping list sharing link.

---

*Concerns audit: 2026-02-23*
