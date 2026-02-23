# Eat It

## What This Is

Eat It is a self-hosted, privacy-first web app for storing, searching,
and organizing recipes, and for managing collaborative shopping lists.
Built for home cooks and families who value data sovereignty, it parses
recipes from URLs using open-source libraries, enables natural language
recipe search via local embeddings, and generates smart shopping lists
from selected recipes — all without sending data to third-party services.

## Core Value

All your recipes and shopping lists live on your own hardware, searchable
in plain English, with no ads, no accounts required, and no data leaving
your network.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Recipe Management**
- [ ] User can import a recipe by pasting a URL (parsed via open-source
  library, previewed, then explicitly saved)
- [ ] User can enter or edit a recipe manually when URL parsing fails or
  is unavailable
- [ ] User can add private notes and a rating to any recipe
- [ ] User receives a clear error message and manual-entry fallback when
  URL parsing fails

**Search**
- [ ] User can search recipes using natural language queries (e.g.,
  "vegetarian dinner for 4") powered by local embeddings — no internet
  or API key required
- [ ] User can search by keyword or tag as a fallback when embedding
  search is unavailable

**Shopping Lists**
- [ ] User can select one or more recipes and generate a shopping list
  with ingredients deduplicated and quantities summed
- [ ] User can add, remove, edit, and adjust quantities of items on a
  shopping list
- [ ] User can check off items on a mobile-optimized list view with
  large tap targets

**Collaboration & Multi-Device**
- [ ] Shopping list is accessible from multiple browsers/devices on the
  same local network or a cloud-hosted self-install
- [ ] A second user can view and check off items from a shared shopping
  list (sync on refresh; no websockets in MVP)
- [ ] User can share a shopping list via a simple link or PIN (no
  mandatory account creation)

**Data & Deployment**
- [ ] User can export recipes and shopping lists as JSON or CSV
- [ ] App can be self-hosted via Docker or a single binary with minimal
  setup steps

**Extensibility (Architecture)**
- [ ] Recipe importers follow a provider/strategy pattern so new parsers
  can be added without touching core logic
- [ ] A plugin directory is scanned at startup to register importers,
  exporters, and enhancers
- [ ] Recipe and shopping list schemas include a versioned `metadata`
  field to support future plugin data without schema hacks

### Out of Scope

- Image, video, or file upload/import — deferred to post-MVP
- Real-time collaborative editing (websockets) — deferred to post-MVP
- Native mobile apps — responsive web is sufficient for MVP
- Third-party grocery/delivery integration — out of scope for v1
- Custom recipe parser — will rely entirely on open-source libraries
- External AI APIs for core search — local embeddings only

## Context

- **Codebase state:** Python 3.13 project structure exists with dev
  tooling configured (Ruff, pytest, pre-commit, mkdocs). No production
  dependencies or implemented features yet.
- **Extensibility intent:** Future milestone roadmap prioritizes
  image/OCR import, real-time collaboration, and advanced AI features.
  The modular architecture must support these without rewrites.
- **User persona:** Maria — family chef, self-hosting on a home server,
  sharing a shopping list with her partner during grocery runs.
- **Privacy stance:** No telemetry or analytics by default. Users have
  full read/write/export access to all their data.
- **Scale target:** Up to 5–10 concurrent users per self-hosted instance
  (household use case). Must run on a Raspberry Pi or equivalent.

## Constraints

- **Tech — Backend:** Python 3.13 + FastAPI (project already configured
  for this)
- **Tech — Frontend:** React + TypeScript + Vite + Tailwind CSS +
  shadcn/ui (decided)
- **Tech — Database:** SQLite (local embedded; no external database
  server)
- **Tech — AI search:** Local embeddings only (sentence-transformers or
  equivalent; no OpenAI/Anthropic API required for core search)
- **Tech — Parser:** Open-source recipe-scrapers library (no custom
  parser development)
- **Performance:** Search response <1s for collections up to several
  thousand recipes
- **Timeline:** MVP target 4 weeks, solo builder

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Preview then save on import | Avoids polluting collection with bad parses; user confirms before committing | — Pending |
| Local embeddings for search | Privacy-first; fully offline; no API keys; acceptable quality for recipe search | — Pending |
| React + TS + Vite + Tailwind + shadcn/ui | Largest ecosystem, strong typing, component library accelerates mobile-first UI | — Pending |
| SQLite for storage | Zero-config, file-based, runs on Raspberry Pi, sufficient for household scale | — Pending |
| Provider pattern for importers | Enables future parsers (OCR, video) without touching core; extensibility from day one | — Pending |

---
*Last updated: 2026-02-23 after initialization*
