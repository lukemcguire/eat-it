# Phase 5: Frontend and Deployment - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

A mobile-optimized React SPA with responsive design and Docker deployment with
minimal setup.

</domain>

<decisions>
## UI Framework & Styling
- React + TypeScript + Vite
- Tailwind CSS + shadcn/ui (Radix primitives)
- Design system: Dark-mode Nordic-inspired (from `.planning/UI/DESIGN.md`)
- **Existing screens:** Shopping List, Recipe Detail, Recipe Binder, Recipe Import
- **Integration:** TanStack Query + fetch for API calls, caching
- **Docker:** Single container with FastAPI serving both static files and API via StaticFiles mount
- **Multi-stage build:** Vite builds `dist/`, then FastAPI serves it in production
- **Environment variables** for configuration (database path, port, etc.)
- **No PWA:** responsive-only, no offline support

- **Nav items:** Recipe Binder, Shopping List, Search, Add/Import (4 items, Recipe binder, Shopping List, Search, Add/Import (via FAB inside recipes)
- **Settings:** Header menu icon

### Mobile Optimization
- **44px minimum tap targets** on all interactive elements (per ROADMAP requirement)
- **Touch gestures:** Drag-to-rearrange on shopping list items only
- **No extra gestures** needed for mobile-first app
- **Keyboard shortcuts:** None needed (mobile-first app)
- **Continue bottom navigation pattern:** Sidebar on desktop + bottom nav on mobile
- **Collapsible sidebar** (icons only below 1024px)
- **Breakpoint:** lg: 1024px (sidebar on desktop)
- **Standard header** with title + context actions (right)
- **Modal/drawer pattern for recipe detail (full-screen on mobile, side panel on desktop)
- **Empty states:** Message + action button (e.g., "Add your first recipe")

### Docker Deployment
- **Single container** with multi-stage build
- **FastAPI serves static files via StaticFiles + API endpoints
- **Environment variables:** `EAT_IT_DB_PATH`, `EAT_IT_PORT`, `EAT_IT_PORT`

</decisions>

<specifics>
## Specific Ideas

- Continue the existing design system (`.planning/UI/DESIGN.md`) and Google Stitch patterns
- **Bottom nav on mobile** with 4 items (Recipes, Shopping, Search, Add/Import)
- **Settings in header menu** (not in nav)
- **Sidebar on desktop** with collapsible icons at 1024px breakpoint
- **Recipe cards:** Single column on mobile, 2+ column grid on desktop
- **Recipe detail:** Modal/drawer pattern, full-screen on mobile, side panel on desktop
- **Empty states:** Message + action button (e.g., "Add your first recipe")
- **Drag-to-rearrange:** shopping list items ( intuitive gesture
- **No keyboard shortcuts needed:** mobile-first app

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-frontend-and-deployment*
*Context gathered: 2026-03-03*
*Context gathered: 2026-03-03*
---
