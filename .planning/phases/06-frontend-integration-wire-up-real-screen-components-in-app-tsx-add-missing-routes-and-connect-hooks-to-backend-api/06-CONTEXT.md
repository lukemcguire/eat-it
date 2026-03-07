# Phase 6: Frontend Integration - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire up real screen components in App.tsx, add missing routes, and connect hooks
to backend API. Replace placeholder screens with Stitch-generated components,
migrate from mock data to real API calls, and implement complete navigation
flow with modal-based recipe detail.

</domain>

<decisions>
## Implementation Decisions

### Route Structure

- **Home:** `/` redirects to `/recipes` (recipe binder)
- **Recipe binder:** `/recipes` with modal overlay for detail
- **Recipe detail modal:** URL updates to `/recipes?recipe={id}` for
  shareability and refresh persistence
- **Shopping lists:** Multiple lists at `/shopping/:id` route
- **Search:** Dedicated `/search` route
- **Import:** Dedicated `/import` route

### Recipe Detail Pattern

- **Modal overlay** on recipe binder page (not separate full page)
- **URL changes** with query param `?recipe={id}` when modal opens
- **In-place editing** within modal (no separate /edit route)
- **Hardware back button** closes modal, returns to binder

### Hook Organization

- **Resource-based hooks:** useRecipes, useShoppingLists, useSearch, useImport
- **Replace mock hooks** with real API calls (no parallel mock+real pattern)
- **Error handling:** Global toast notifications via Sonner
- **Loading states:** Skeleton loaders + optimistic updates where safe

### Search Implementation

- **Search mode:** Semantic-first with keyword fallback
- **Search trigger:** Manual (Enter key or button click, no live debounce)
- **UI:** Full page with search bar at top, results as recipe cards grid
- **Empty state (before search):** Recent recipes suggestions
- **No results state:** Friendly message with suggestions
- **Reuse RecipeBinderScreen** with search-focused state (not separate screen)

### Shopping List

- **Multiple lists** with `/shopping/:id` route
- **Default list:** TBD (first list or user-selected default)

### Navigation Flow

- **Bottom nav:** 4 items (Recipes, Shopping, Search, Import)
- **After recipe save:** Close modal, show toast, stay on binder
- **Add to shopping list:** Show toast, stay on recipe detail page
- **Desktop:** Sidebar navigation, collapsible below 1024px
- **Mobile:** Bottom nav (44px minimum tap targets per Phase 5)

### Component Integration

- **Copy Stitch-generated screens** from `.planning/UI/src/components/`
  into `frontend/src/components/`
- **Use existing designs** with minor color tweaks for Synchronized Blue theme
  consistency
- **Screens to integrate:** RecipeBinderScreen, RecipeDetailScreen,
  RecipeImportScreen, ShoppingListScreen

### Claude's Discretion

- Exact skeleton loader design
- Toast notification styling and positioning
- Error boundary implementation
- Loading spinner vs skeleton choice per component
- Default shopping list selection logic

</decisions>

<specifics>
## Specific Ideas

- Recipe detail modal should feel like in-place editing (not a separate page)
- URL should update when modal opens for shareability
- Use Synchronized Blue theme consistently across all screens
- Search reuses binder grid layout for familiarity
- Global toast notifications for API errors

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets (Stitch-generated in .planning/UI/src/components/)

- `RecipeBinderScreen.tsx`: Recipe grid with search/filter bar
- `RecipeDetailScreen.tsx`: Full recipe view with ingredients/instructions
- `RecipeImportScreen.tsx`: URL input + preview-before-save
- `ShoppingListScreen.tsx`: Mobile-optimized list with sections

### Existing Hooks (frontend/src/hooks/)

- `useRecipes.ts`: Connected to real API (list, get, create, update,
  delete, parse)
- `useRecipeImport.ts`: Mock data (needs API connection)
- `useShoppingList.ts`: Mock data (needs API connection)
- `useRecipeBinder.ts`: Mock data (needs API connection)
- `useIngredients.ts`: Built for ingredient editing (Phase 05.1)

### Layout Components (frontend/src/components/layout/)

- `AppLayout.tsx`: Wrapper with Outlet for nested routes
- `Header.tsx`: Top bar with title + context actions
- `BottomNav.tsx`: Mobile navigation (hidden on desktop)
- `Sidebar.tsx`: Desktop navigation (hidden on mobile)

### API Client (frontend/src/lib/api.ts)

- `apiClient<T>()`: Generic fetch wrapper with error handling
- `ApiError` class: Status code + message for error handling

### Integration Points

- Backend API: `/api/recipes`, `/api/shopping-lists`, `/api/search`
- TanStack Query for caching and invalidation
- React Router for navigation and modal state

</code_context>

<deferred>
## Deferred Ideas

- Live search with debounce (manual trigger is sufficient for MVP)
- Keyboard shortcuts (mobile-first app)
- PWA offline caching for shopping lists

</deferred>

---

*Phase: 06-frontend-integration*
*Context gathered: 2026-03-06*
