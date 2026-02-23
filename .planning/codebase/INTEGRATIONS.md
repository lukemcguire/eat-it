# External Integrations

**Analysis Date:** 2026-02-23

## APIs & External Services

**Recipe Parsing:**
- Open-source recipe parser (TBD during Phase 1)
  - SDK/Client: Recipe parsing library (e.g.,
    recipe-scrapers, pyrecipe, or equivalent)
  - Purpose: Extracts structured data (title,
    ingredients, instructions) from recipe URLs
  - Auth: None required (most open-source parsers
    use no credentials)

**AI/NLP Services:**
- Local AI/NLP for natural language search (planned)
  - Purpose: Enable queries like "vegetarian dinner
    for 4" to match saved recipes
  - Auth: None (running locally, not cloud-based)
  - Implementation: Local LLM or lightweight
    embeddings library (TBD)

## Data Storage

**Databases:**
- SQLite (planned, not yet implemented)
  - Purpose: Local storage for recipes, ingredients,
    shopping lists, user data
  - Connection: File-based (embedded in application)
  - Client: Python sqlite3 (stdlib) or ORM (e.g.,
    SQLAlchemy, TBD)
  - Location: Local filesystem only (no remote DB)

**File Storage:**
- Local filesystem only
  - No cloud storage providers integrated
  - Users can export/backup as JSON or CSV
    (manual export, not automated sync)

**Caching:**
- None currently specified
- May use in-memory caching for AI search index
  (TBD during implementation)

## Authentication & Identity

**Auth Provider:**
- Custom or minimal (TBD)
- Options per PRD:
  - Simple local login (password-based)
  - Single-user mode with optional shareable link
    or PIN for shopping list access
  - No third-party OAuth/SSO in MVP
- Implementation: Backend API will handle auth
  (details pending Phase 1)

## Monitoring & Observability

**Error Tracking:**
- None configured
- Application logging via Python logging module
  (configured via ruff LOG rules)

**Logs:**
- Standard Python logging approach (per ruff LOG
  and G rules enforcing best practices)
- Logs written to stdout/file (destination TBD)
- No external log aggregation (self-hosted
  philosophy)

## CI/CD & Deployment

**Hosting:**
- Self-hosted (user-deployed)
  - Docker Compose setup (planned)
  - Single binary or cloud-native deployment
    (TBD)
  - Minimal hardware requirements (Raspberry Pi
    compatible per PRD)

**CI Pipeline:**
- GitHub Actions (implied by .github presence in
  gitignore; not yet configured)
- No external SaaS CI configured yet

**Version Control:**
- GitHub repository:
  https://github.com/lukemcguire/eat-it

## Environment Configuration

**Required env vars:**
- TBD during implementation
- Likely: Database path, port, optional AI service
  endpoint (if cloud-based LLM used)
- No sensitive API keys required in MVP (all
  services local or public)

**Secrets location:**
- .env file (not tracked in git, in .gitignore)
- No secrets currently needed (self-hosted
  architecture)
- Future: Use environment variables for optional
  third-party integrations if added post-MVP

## Webhooks & Callbacks

**Incoming:**
- Recipe URL import webhook (potential future
  feature, not in MVP)
- No external webhooks in MVP

**Outgoing:**
- None currently planned
- Future: Optional opt-in usage telemetry (user
  can control via settings per PRD)

## Browser & Frontend APIs

**Client-Side Storage:**
- Browser localStorage (for temporary shopping list
  state, TBD)
- Session storage for user preferences (TBD)
- Considerations: Browser storage limits noted in
  PRD as edge case

**Frontend Framework APIs:**
- REST API endpoints served by backend
  - `/api/recipes/*` - Recipe import, retrieval,
    search
  - `/api/shopping-lists/*` - List management
  - Endpoints TBD during Phase 1

## Third-Party Dependencies (Post-MVP)

**Planned Integrations (Future Phases):**
- Grocery delivery/pickup platforms (Phase 3+, per
  PRD)
- Image OCR services (Phase 3+, for screenshot/PDF
  import)
- Native mobile app frameworks (iOS/Android,
  Phase 3+)

## Privacy & Data Control

**Data Residency:**
- All data stays on user's self-hosted instance
- No cloud backup (user-managed backups only)
- No telemetry or analytics in MVP (optional
  opt-in planned for Phase 3)

**Export & Interoperability:**
- JSON export for recipes and shopping lists
  (planned)
- CSV export for shopping lists (planned)
- Standard data formats to enable future
  integrations

---

*Integration audit: 2026-02-23*
