# Phase 4: Shopping List - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate and manage collaborative shopping lists from recipes, with ingredient
deduplication, mobile-optimized checking, and simple sharing without accounts.
Users can select recipes, get a combined shopping list, check off items on
mobile, and share with household members via link.

</domain>

<decisions>
## Implementation Decisions

### Ingredient Combining

- **Smart combining**: Parse quantities, normalize units, sum amounts for the
  same ingredient across multiple recipes
- **Unit normalization**: Convert between compatible units when possible
  (e.g., 1 cup + 8 oz = 1.5 cups for the same ingredient)
- **Similar ingredients stay separate**: "onion" and "red onion" remain as
  distinct items — user decides on substitutions
- **Preparation ignored**: "1 onion (chopped)" and "1 onion (diced)" combine
  to just "2 onions" — prep doesn't matter at the grocery store

### List Organization

- **Multiple named lists**: Users can have multiple shopping lists
  (e.g., "Weekly groceries", "Party supplies")
- **Group by store section**: Items grouped by store section (Produce, Dairy,
  Meat, etc.) for efficient store navigation
- **Hybrid section model**: Start with predefined sections (Produce, Dairy,
  Meat, Bakery, Pantry, Frozen, Other), allow user to add/edit/remove
- **Manual reordering**: Users can drag to reorder items within sections

### Sharing Mechanics

- **Link = full access**: Anyone with the link can view AND edit the list
  (no separate view-only mode)
- **Random string links**: Format like `/list/abc123xyz` — easy to share via
  text/email, no naming conflicts
- **Auto-expire**: Links expire after a set period (e.g., 7 days) — prevents
  stale access while supporting ongoing household use
- **Unlimited concurrent users**: No cap on simultaneous access

### Sync Strategy

- **Real-time via WebSockets**: Changes appear instantly across all devices
  for the best collaborative experience
- **Last-write-wins**: Simple conflict resolution — the last change takes
  precedence (appropriate for grocery lists where conflicts are rare)
- **Offline handling**: Show offline warning, prevent edits until
  reconnected (simpler than queuing)
- **Completed items**: Checked-off items move to a "completed" section at
  the bottom of the list (not hidden, not crossed out in place)

### Claude's Discretion

- Default store sections and their ordering
- Auto-categorization logic for common ingredients
- Exact WebSocket implementation details
- Link expiration duration (suggest 7 days as default)
- Completed section behavior (clear all? auto-hide after time?)

</decisions>

<specifics>
## Specific Ideas

- Focus on the grocery store context — users are buying items, not buying
  them prepared. Preparation notes are noise at the store.
- Store section grouping helps users navigate efficiently — no backtracking
  across the store.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-shopping-list*
*Context gathered: 2026-03-03*
