# Phase 6: Frontend Integration - Research

**Researched:** 2026-03-07
**Domain:** React frontend integration with TanStack Query, React Router, and
WebSocket real-time updates
**Confidence:** HIGH

## Summary

This phase integrates Stitch-generated screen components with the existing
frontend infrastructure. The core work involves: (1) copying screen components
from `.planning/UI/src/components/` to `frontend/src/components/screens/`, (2)
migrating three mock hooks to real API calls using TanStack Query, (3)
implementing the modal-based recipe detail pattern with URL query parameters,
and (4) wiring up the complete navigation flow.

The existing `useRecipes` hook demonstrates the target pattern with TanStack
Query v5.60.0 - all other resource hooks should follow this same structure. The
backend APIs are complete and tested; the gap is purely frontend integration.

**Primary recommendation:** Follow the existing `useRecipes.ts` pattern exactly
when migrating `useShoppingList`, `useRecipeImport`, and `useRecipeBinder` to
real API calls.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Route Structure

- **Home:** `/` redirects to `/recipes` (recipe binder)
- **Recipe binder:** `/recipes` with modal overlay for detail
- **Recipe detail modal:** URL updates to `/recipes?recipe={id}` for
  shareability and refresh persistence
- **Shopping lists:** Multiple lists at `/shopping/:id` route
- **Search:** Dedicated `/search` route
- **Import:** Dedicated `/import` route

#### Recipe Detail Pattern

- **Modal overlay** on recipe binder page (not separate full page)
- **URL changes** with query param `?recipe={id}` when modal opens
- **In-place editing** within modal (no separate /edit route)
- **Hardware back button** closes modal, returns to binder

#### Hook Organization

- **Resource-based hooks:** useRecipes, useShoppingLists, useSearch, useImport
- **Replace mock hooks** with real API calls (no parallel mock+real pattern)
- **Error handling:** Global toast notifications via Sonner
- **Loading states:** Skeleton loaders + optimistic updates where safe

#### Search Implementation

- **Search mode:** Semantic-first with keyword fallback
- **Search trigger:** Manual (Enter key or button click, no live debounce)
- **UI:** Full page with search bar at top, results as recipe cards grid
- **Empty state (before search):** Recent recipes suggestions
- **No results state:** Friendly message with suggestions
- **Reuse RecipeBinderScreen** with search-focused state (not separate screen)

#### Shopping List

- **Multiple lists** with `/shopping/:id` route
- **Default list:** TBD (first list or user-selected default)

#### Navigation Flow

- **Bottom nav:** 4 items (Recipes, Shopping, Search, Import)
- **After recipe save:** Close modal, show toast, stay on binder
- **Add to shopping list:** Show toast, stay on recipe detail page
- **Desktop:** Sidebar navigation, collapsible below 1024px
- **Mobile:** Bottom nav (44px minimum tap targets per Phase 5)

#### Component Integration

- **Copy Stitch-generated screens** from `.planning/UI/src/components/` into
  `frontend/src/components/`
- **Use existing designs** with colors, typography, etc. to be replaced where
  necessary to be consistent with the Synchronized Blue theme as outlined in
  `.planning/UI/DESIGN.md`
- **Screens to integrate:** RecipeBinderScreen, RecipeDetailScreen,
  RecipeImportScreen, ShoppingListScreen

### Claude's Discretion

- Exact skeleton loader design
- Toast notification styling and positioning
- Error boundary implementation
- Loading spinner vs skeleton choice per component
- Default shopping list selection logic

### Deferred Ideas (OUT OF SCOPE)

- Live search with debounce (manual trigger is sufficient for MVP)
- Keyboard shortcuts (mobile-first app)
- PWA offline caching for shopping lists

</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| react-router-dom | ^7.13.1 | Routing, navigation, modal URL state | Locked in CONTEXT.md, supports useSearchParams for modal pattern |
| @tanstack/react-query | ^5.60.0 | Data fetching, caching, invalidation | Already in useRecipes, established pattern |
| sonner | (to add) | Toast notifications | Locked in CONTEXT.md, lightweight, accessible |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| lucide-react | ^0.460.0 | Icons | UI components |
| @radix-ui/react-* | various | Accessible primitives | Existing UI components |
| @dnd-kit/* | various | Drag and drop | Ingredient editing (Phase 5.1) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sonner | react-hot-toast | Sonner is lighter, better positioned API |
| useSearchParams | useLocation + URL | useSearchParams is more idiomatic in React Router v7 |

**Installation:**

```bash
cd frontend && npm install sonner
```

## Architecture Patterns

### Recommended Project Structure

```
frontend/src/
├── components/
│   ├── layout/           # AppLayout, Header, BottomNav, Sidebar
│   ├── screens/          # Stitch-generated screens (new)
│   │   ├── RecipeBinderScreen.tsx
│   │   ├── RecipeDetailScreen.tsx
│   │   ├── RecipeImportScreen.tsx
│   │   └── ShoppingListScreen.tsx
│   └── ui/               # Button, Card, Input, etc.
├── hooks/
│   ├── useRecipes.ts     # API-connected (complete)
│   ├── useShoppingList.ts  # Mock -> API migration needed
│   ├── useRecipeImport.ts  # Mock -> API migration needed
│   └── useRecipeBinder.ts  # Mock -> API migration needed
├── lib/
│   └── api.ts            # apiClient generic fetch wrapper
├── types/
│   └── recipe.ts         # TypeScript interfaces
└── App.tsx               # Route definitions
```

### Pattern 1: TanStack Query Hook Pattern

**What:** Standard pattern for API-connected hooks using TanStack Query
**When to use:** All resource-based data fetching hooks
**Example:**

```typescript
// Source: frontend/src/hooks/useRecipes.ts (existing)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

// Query hook
export function useRecipes(params?: { offset?: number; limit?: number; q?: string }) {
  return useQuery({
    queryKey: ['recipes', params],
    queryFn: () => apiClient<Recipe[]>(`/recipes`),
  });
}

// Mutation hook
export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recipe: RecipeCreate) =>
      apiClient<Recipe>('/recipes/', {
        method: 'POST',
        body: JSON.stringify(recipe),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
    },
  });
}
```

### Pattern 2: Modal with Query Parameters

**What:** Modal overlay that updates URL for shareability without navigation
**When to use:** Recipe detail modal on binder page
**Example:**

```typescript
// Source: React Router v7 pattern
import { useSearchParams, useNavigate } from 'react-router-dom';

function RecipeBinderScreen() {
  const [searchParams, setSearchParams] = useSearchParams();
  const recipeId = searchParams.get('recipe');

  const openRecipe = (id: number) => {
    setSearchParams({ recipe: String(id) });
  };

  const closeModal = () => {
    setSearchParams({});
  };

  return (
    <>
      <RecipeGrid onRecipeClick={openRecipe} />
      {recipeId && (
        <RecipeDetailModal
          recipeId={Number(recipeId)}
          onClose={closeModal}
        />
      )}
    </>
  );
}
```

### Pattern 3: WebSocket Real-time Updates

**What:** Subscribe to shopping list changes via WebSocket
**When to use:** Shopping list screen for collaborative updates
**Example:**

```typescript
// Backend endpoint: /shopping-lists/ws/{list_id}
// Messages: {"type": "item_updated", "item": {...}}
// Messages: {"type": "item_deleted", "item_id": 123}

function useShoppingListWebSocket(listId: number) {
  const queryClient = useQueryClient();
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://${host}/shopping-lists/ws/${listId}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'item_updated' || data.type === 'item_deleted') {
        queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
      }
    };
    setSocket(ws);
    return () => ws.close();
  }, [listId]);

  return socket;
}
```

### Anti-Patterns to Avoid

- **Parallel mock+real hooks:** CONTEXT.md explicitly forbids this - replace
  mocks completely, not alongside
- **Stale mock data imports:** Remove `import { mockData }` after migration
- **Client-side search for recipe binder:** Backend has semantic search - use it
- **Full-page recipe detail:** CONTEXT.md locks modal pattern with query params

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Toast notifications | Custom toast system | sonner | Accessible, positioning, promise support |
| API state management | useState + useEffect | @tanstack/react-query | Caching, invalidation, loading states |
| URL query params | URLSearchParams manually | useSearchParams from react-router-dom | Type-safe, reactive |
| WebSocket reconnection | Custom WS logic | Native WebSocket + useEffect cleanup | Keep simple for MVP |

**Key insight:** The existing `useRecipes.ts` demonstrates all patterns needed.
Copy its structure for other hooks.

## Common Pitfalls

### Pitfall 1: Mock Data Still Imported After Migration

**What goes wrong:** Hook uses TanStack Query but still imports mock types from
`../data/mockData`
**Why it happens:** Incremental migration without cleanup
**How to avoid:** Remove all mock data imports, update types to match API
responses
**Warning signs:** TypeScript errors about type mismatches between mock and API
types

### Pitfall 2: Query Key Collisions

**What goes wrong:** Multiple hooks use same query key, causing incorrect cache
invalidation
**Why it happens:** Using `['recipes']` for both list and detail queries
**How to avoid:** Include all relevant params in key: `['recipes', id]` for
detail, `['recipes', params]` for list
**Warning signs:** Updating one item causes entire list to refetch, or vice
versa

### Pitfall 3: Modal URL Not Updating

**What goes wrong:** Modal opens but URL stays at `/recipes`, breaking
shareability
**Why it happens:** Using local state instead of useSearchParams
**How to avoid:** Always use setSearchParams to update URL when modal opens
**Warning signs:** Refreshing page with modal open shows 404 or loses modal
state

### Pitfall 4: WebSocket Memory Leak

**What goes wrong:** WebSocket connections accumulate, causing memory issues
**Why it happens:** Not closing WebSocket in useEffect cleanup
**How to avoid:** Always return cleanup function: `return () => ws.close();`
**Warning signs:** Multiple "ping" messages in network tab, degraded
performance

## Code Examples

### Shopping List Hook Migration

```typescript
// Source: Pattern from useRecipes.ts, backend API from shopping_lists.py
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface ShoppingListItem {
  id: number;
  name: string;
  quantity: string | null;
  unit: string | null;
  section_id: number | null;
  checked: boolean;
  display_order: number;
}

export interface ShoppingList {
  id: number;
  name: string;
  items: ShoppingListItem[];
  created_at: string;
  updated_at: string;
}

// List all shopping lists (without items)
export function useShoppingLists() {
  return useQuery({
    queryKey: ['shopping-lists'],
    queryFn: () => apiClient<{ data: ShoppingList[]; count: number }>('/shopping-lists/'),
  });
}

// Get single list with items
export function useShoppingList(id: number) {
  return useQuery({
    queryKey: ['shopping-list', id],
    queryFn: () => apiClient<ShoppingList>(`/shopping-lists/${id}`),
    enabled: !!id,
  });
}

// Update item (toggle checked)
export function useUpdateShoppingListItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ listId, itemId, data }: {
      listId: number;
      itemId: number;
      data: Partial<ShoppingListItem>;
    }) =>
      apiClient<ShoppingListItem>(`/shopping-lists/${listId}/items/${itemId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { listId }) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
    },
  });
}
```

### Search Hook

```typescript
// Source: Backend /search endpoint from search.py
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { Recipe } from '@/types/recipe';

export function useSearch(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () => apiClient<Recipe[]>(`/search?q=${encodeURIComponent(query)}`),
    enabled: enabled && query.trim().length > 0,
  });
}
```

### Recipe Import Hook

```typescript
// Source: Backend /recipes/parse endpoint from recipes.py
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { Recipe, ParseResponse, RecipeCreate } from '@/types/recipe';

export function useParseRecipeUrl() {
  return useMutation({
    mutationFn: (url: string) =>
      apiClient<ParseResponse>(`/recipes/parse?url=${encodeURIComponent(url)}`),
  });
}

export function useSaveRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recipe: RecipeCreate) =>
      apiClient<Recipe>('/recipes/', {
        method: 'POST',
        body: JSON.stringify(recipe),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
    },
  });
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| useState + fetch | TanStack Query | Phase 5 | Automatic caching, loading states |
| react-hot-toast | sonner | Phase 6 (this) | Lighter, better API |
| Full-page detail | Modal + query params | Phase 6 (this) | Better UX, shareable URLs |

**Deprecated/outdated:**
- `useShoppingList` mock data: Replace with TanStack Query + API
- `useRecipeImport` mock data: Replace with parse endpoint + create recipe
- `useRecipeBinder` mock data: Replace with useRecipes + useSearch

## Open Questions

1. **Default shopping list selection logic**
   - What we know: Multiple lists at `/shopping/:id`, first list or user-selected
   - What's unclear: Should we store user's last-used list in localStorage?
     Redirect to first list if none specified?
   - Recommendation: Redirect `/shopping` to `/shopping/1` (first list), store
     last-used in localStorage for future visits

2. **Error boundary granularity**
   - What we know: Global toast for API errors
   - What's unclear: Should each screen have its own error boundary, or one
     global boundary?
   - Recommendation: One global error boundary in App.tsx, toast notifications
     for recoverable API errors

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | vitest ^2.1.5 with @testing-library/react ^16.0.1 |
| Config file | `frontend/vitest.config.ts` |
| Quick run command | `cd frontend && npm test` |
| Full suite command | `cd frontend && npm test -- --coverage` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| Route-01 | Home redirects to /recipes | unit | `npm test -- App.test.tsx` | Yes |
| Route-02 | Modal updates URL with ?recipe={id} | unit | `npm test -- RecipeBinder.test.tsx` | No - Wave 0 |
| Route-03 | Shopping list route /shopping/:id | unit | `npm test -- App.test.tsx` | Partial |
| Hook-01 | useShoppingList fetches from API | unit | `npm test -- useShoppingList.test.tsx` | No - Wave 0 |
| Hook-02 | useSearch calls /search endpoint | unit | `npm test -- useSearch.test.tsx` | No - Wave 0 |
| Hook-03 | useRecipeImport uses parse endpoint | unit | `npm test -- useRecipeImport.test.tsx` | No - Wave 0 |
| Toast-01 | API errors show toast notification | unit | `npm test -- Toast.test.tsx` | No - Wave 0 |
| WS-01 | WebSocket invalidates on message | unit | `npm test -- useShoppingListWS.test.tsx` | No - Wave 0 |

### Sampling Rate

- **Per task commit:** `npm test -- --run`
- **Per wave merge:** `npm test -- --run --coverage`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `frontend/src/__tests__/hooks/useShoppingList.test.tsx` - covers Hook-01
- [ ] `frontend/src/__tests__/hooks/useSearch.test.tsx` - covers Hook-02
- [ ] `frontend/src/__tests__/hooks/useRecipeImport.test.tsx` - covers Hook-03
- [ ] `frontend/src/__tests__/components/screens/RecipeBinder.test.tsx` -
  covers Route-02
- [ ] `frontend/src/__tests__/components/Toast.test.tsx` - covers Toast-01
- [ ] Framework install: `npm install sonner` - dependency missing

## Sources

### Primary (HIGH confidence)

- `frontend/src/hooks/useRecipes.ts` - Existing TanStack Query pattern
- `frontend/src/lib/api.ts` - API client implementation
- `src/eat_it/routers/recipes.py` - Backend recipe endpoints
- `src/eat_it/routers/search.py` - Backend search endpoint
- `src/eat_it/routers/shopping_lists.py` - Backend shopping list + WebSocket
- `.planning/06-CONTEXT.md` - Locked user decisions

### Secondary (MEDIUM confidence)

- `frontend/src/__tests__/useRecipes.test.tsx` - Test pattern for hooks
- `frontend/vitest.config.ts` - Test configuration
- `.planning/UI/DESIGN.md` - Design system reference

### Tertiary (LOW confidence)

- None - all research based on codebase inspection

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All dependencies already installed except sonner
- Architecture: HIGH - Existing useRecipes.ts demonstrates target pattern
- Pitfalls: HIGH - Based on common React/TanStack Query patterns

**Research date:** 2026-03-07
**Valid until:** 30 days - Stable patterns, no rapidly-changing dependencies
