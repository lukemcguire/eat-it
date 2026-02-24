# Requirements: Eat It

**Defined:** 2026-02-23
**Core Value:** All your recipes and shopping lists live on your own hardware,
searchable in plain English, with no ads, no accounts required, and no data
leaving your network.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Recipe Management (RECIPE)

- [ ] **RECIPE-01**: User can import a recipe by pasting a URL (parsed via
  open-source library, previewed, then explicitly saved)
- [ ] **RECIPE-02**: User can enter or edit a recipe manually when URL parsing
  fails or is unavailable
- [ ] **RECIPE-03**: User can add private notes and a rating to any recipe
- [ ] **RECIPE-04**: User receives a clear error message and manual-entry
  fallback when URL parsing fails
- [ ] **RECIPE-05**: User is warned when importing a duplicate URL (detection
  on import)
- [ ] **RECIPE-06**: User can preview parsed recipe data before saving
  (preview-before-confirm flow)

### Search (SEARCH)

- [ ] **SEARCH-01**: User can search recipes using natural language queries
  (e.g., "vegetarian dinner for 4") powered by local embeddings — no internet
  or API key required
- [ ] **SEARCH-02**: User can search by keyword or tag as a fallback when
  embedding search is unavailable

### Shopping Lists (SHOP)

- [ ] **SHOP-01**: User can select one or more recipes and generate a shopping
  list with ingredients deduplicated and quantities summed
- [ ] **SHOP-02**: User can add, remove, edit, and adjust quantities of items
  on a shopping list
- [ ] **SHOP-03**: User can check off items on a mobile-optimized list view
  with large tap targets (44px minimum)
- [ ] **SHOP-04**: Shopping list is accessible from multiple browsers/devices
  on the same local network or a cloud-hosted self-install
- [ ] **SHOP-05**: A second user can view and check off items from a shared
  shopping list (sync on refresh; no websockets in MVP)
- [ ] **SHOP-06**: User can share a shopping list via a simple link or PIN
  (no mandatory account creation)

### Data & Deployment (DATA)

- [ ] **DATA-01**: User can export recipes and shopping lists as JSON or CSV
- [ ] **DATA-02**: App can be self-hosted via Docker or a single binary with
  minimal setup steps

### Architecture (ARCH)

- [ ] **ARCH-01**: Recipe importers follow a provider/strategy pattern so new
  parsers can be added without touching core logic
- [x] **ARCH-02**: A plugin directory is scanned at startup to register
  importers, exporters, and enhancers
- [ ] **ARCH-03**: Recipe and shopping list schemas include a versioned
  `metadata` field to support future plugin data without schema hacks

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enhanced Features

- **SERVE-01**: User can scale recipe quantities by serving size multiplier
- **SHOP-07**: Shopping list items are grouped by ingredient category
  (produce, dairy, pantry)
- **SHOP-08**: Shopping list caches offline for use in low-signal stores (PWA)
- **RECIPE-07**: User can organize recipes into collections/cookbooks

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Image, video, or file upload/import | Deferred to post-MVP; significant storage complexity |
| Real-time collaborative editing (websockets) | Deferred to post-MVP; adds infra complexity for household scale |
| Native mobile apps | Responsive web is sufficient for MVP; native adds 3-5x cost |
| Third-party grocery/delivery integration | Privacy-hostile; contradicts self-hosted value prop |
| Custom recipe parser development | Will rely entirely on open-source recipe-scrapers library |
| External AI APIs for core search | Local embeddings only; privacy-first stance |
| Meal planning calendar | Medium value, high UX complexity; not core to shopping list workflow |
| Nutritional calculations | Requires ingredient database linkage; low value for MVP |
| Grocery store aisle ordering | Complex per-store configuration; negligible value for household scale |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RECIPE-01 | 2 | Pending |
| RECIPE-02 | 2 | Pending |
| RECIPE-03 | 2 | Pending |
| RECIPE-04 | 2 | Pending |
| RECIPE-05 | 2 | Pending |
| RECIPE-06 | 2 | Pending |
| SEARCH-01 | 3 | Pending |
| SEARCH-02 | 3 | Pending |
| SHOP-01 | 4 | Pending |
| SHOP-02 | 4 | Pending |
| SHOP-03 | 4 | Pending |
| SHOP-04 | 4 | Pending |
| SHOP-05 | 4 | Pending |
| SHOP-06 | 4 | Pending |
| DATA-01 | 2 | Pending |
| DATA-02 | 5 | Pending |
| ARCH-01 | 1 | Pending |
| ARCH-02 | 1 | Complete |
| ARCH-03 | 1 | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-02-23*
*Last updated: 2026-02-23 after roadmap creation*
