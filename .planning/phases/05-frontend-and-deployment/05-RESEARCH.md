# Phase 5: Frontend and Deployment - Research

**Researched:** 2026-03-03
**Domain:** React SPA, Docker deployment, FastAPI static file serving
**Confidence:** HIGH

## Summary

This phase implements the mobile-optimized React SPA frontend and Docker
deployment for the Eat It recipe management application. The frontend uses React
18 with TypeScript, Vite 6 for builds, Tailwind CSS 3.4 with shadcn/ui
components, and TanStack Query v5 for API state management. The deployment uses
a single Docker container with multi-stage build: Node.js builds the Vite
frontend, Python serves both the static files and API via FastAPI's StaticFiles.

**Primary recommendation:** Use a multi-stage Dockerfile that builds the Vite
app in a Node stage, copies dist/ to the Python stage, and configures FastAPI to
serve static files at root with SPA fallback. Mount SQLite database as a volume
for persistence.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**UI Framework & Styling:**
- React + TypeScript + Vite
- Tailwind CSS + shadcn/ui (Radix primitives)
- Design system: Dark-mode Nordic-inspired (from `.planning/UI/DESIGN.md`)
- Existing screens: Shopping List, Recipe Detail, Recipe Binder, Recipe Import
- Integration: TanStack Query + fetch for API calls, caching
- Docker: Single container with FastAPI serving both static files and API via
  StaticFiles mount
- Multi-stage build: Vite builds `dist/`, then FastAPI serves it in production
- Environment variables for configuration (database path, port, etc.)
- No PWA: responsive-only, no offline support

**Navigation:**
- Nav items: Recipe Binder, Shopping List, Search, Add/Import (4 items)
- Settings: Header menu icon

**Mobile Optimization:**
- 44px minimum tap targets on all interactive elements
- Touch gestures: Drag-to-rearrange on shopping list items only
- No extra gestures needed for mobile-first app
- Keyboard shortcuts: None needed (mobile-first app)
- Continue bottom navigation pattern: Sidebar on desktop + bottom nav on mobile
- Collapsible sidebar (icons only below 1024px)
- Breakpoint: lg: 1024px (sidebar on desktop)
- Standard header with title + context actions (right)
- Modal/drawer pattern for recipe detail (full-screen on mobile, side panel on
  desktop)
- Empty states: Message + action button (e.g., "Add your first recipe")

**Docker Deployment:**
- Single container with multi-stage build
- FastAPI serves static files via StaticFiles + API endpoints
- Environment variables: `EAT_IT_DB_PATH`, `EAT_IT_PORT`

### Claude's Discretion

None explicitly stated - all major decisions locked.

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-02 | App can be self-hosted via Docker or a single binary with minimal setup steps | Docker multi-stage build pattern, FastAPI StaticFiles mount, environment variable configuration, volume mounting for SQLite persistence |

</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 18.3.1 | UI framework | Industry standard, existing prototypes use it |
| TypeScript | ~5.6.2 | Type safety | Already in project, prevents runtime errors |
| Vite | 6.0.1 | Build tool | Fast HMR, excellent DX, already configured |
| Tailwind CSS | 3.4.15 | Styling | Utility-first, matches design system, existing |
| shadcn/ui | Latest | Component library | Radix primitives for accessibility, already set up |
| TanStack Query | v5 | Server state management | Caching, deduplication, optimistic updates |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @radix-ui/react-* | Various | Accessible primitives | All interactive components |
| lucide-react | 0.460.0 | Icon library | Navigation, actions, status |
| class-variance-authority | 0.7.1 | Variant management | Button variants, component states |
| clsx + tailwind-merge | Latest | Class utilities | Conditional styling |

### Backend Integration

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | API framework | Already implemented, StaticFiles built-in |
| uvicorn | 0.30+ | ASGI server | Production-ready, already configured |
| SQLModel | 0.0.16+ | ORM | Existing database layer |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| TanStack Query | SWR | TanStack has better devtools, mutation support |
| shadcn/ui | Chakra UI | shadcn is more customizable, already configured |
| FastAPI StaticFiles | nginx reverse proxy | Single container simpler for self-hosting |
| Single container | Docker Compose | Simpler deployment, meets requirement |

**Installation:**

```bash
# Frontend (in .planning/UI/)
npm install @tanstack/react-query

# No additional backend packages needed - FastAPI StaticFiles is built-in
```

## Architecture Patterns

### Recommended Project Structure

```text
src/eat_it/
├── main.py              # FastAPI app + StaticFiles mount
├── config.py            # Settings with EAT_IT_ prefix
├── routers/
│   ├── recipes.py       # /recipes/* endpoints
│   ├── shopping.py      # /shopping/* endpoints (Phase 4)
│   └── health.py        # /health endpoint
└── ...

.planning/UI/
├── src/
│   ├── components/
│   │   ├── ui/          # Shared UI components
│   │   ├── shadcn/      # shadcn/ui components
│   │   ├── layout/      # AppLayout, Sidebar, BottomNav, Header
│   │   ├── screens/     # Page components
│   │   └── features/    # Feature-specific components
│   ├── hooks/
│   │   ├── useApi.ts    # TanStack Query configuration
│   │   └── use*.ts      # Feature hooks
│   ├── lib/
│   │   └── api.ts       # Fetch client with base URL
│   └── App.tsx          # Router + QueryClient setup
├── dist/                # Vite build output (copied to container)
└── package.json

docker/
├── Dockerfile           # Multi-stage build
└── .dockerignore

docker-compose.yml       # Optional: volume mount + port config
```

### Pattern 1: FastAPI StaticFiles Mount

**What:** Serve Vite-built React SPA from FastAPI using StaticFiles with SPA
fallback.

**When to use:** Single-container deployment where API and static files share
the same origin.

**Example:**

```python
# src/eat_it/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # ... other startup
    yield

app = FastAPI(title="Eat It", lifespan=lifespan)

# API routes (must come before static files)
app.include_router(health_router)
app.include_router(recipes_router, prefix="/recipes")
app.include_router(shopping_router, prefix="/shopping")

# Serve static files in production
# Static files are at /static/* (JS, CSS, assets)
# SPA fallback to index.html for client-side routing
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve index.html for client-side routing."""
        return FileResponse("static/index.html")
```

**Source:** FastAPI StaticFiles documentation

### Pattern 2: TanStack Query Setup

**What:** Configure TanStack Query with custom fetch client for API calls.

**When to use:** All API interactions need caching, deduplication, and loading
states.

**Example:**

```typescript
// src/lib/api.ts
const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

// src/hooks/useRecipes.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export function useRecipes() {
  return useQuery({
    queryKey: ['recipes'],
    queryFn: () => apiClient<Recipe[]>('/recipes'),
  });
}

export function useRecipe(id: string) {
  return useQuery({
    queryKey: ['recipes', id],
    queryFn: () => apiClient<Recipe>(`/recipes/${id}`),
  });
}
```

**Source:** TanStack Query v5 documentation

### Pattern 3: Multi-Stage Dockerfile

**What:** Build Vite app in Node stage, copy to Python stage for serving.

**When to use:** Single-container production deployment.

**Example:**

```dockerfile
# docker/Dockerfile

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY .planning/UI/package*.json ./
RUN npm ci
COPY .planning/UI/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.13-slim
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir .

# Copy backend code
COPY src/ ./src/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist ./static

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "eat_it.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Source:** Docker multi-stage builds documentation

### Pattern 4: Responsive Navigation

**What:** Bottom nav on mobile, collapsible sidebar on desktop.

**When to use:** Mobile-first app with desktop support.

**Example:**

```typescript
// src/components/layout/AppLayout.tsx
export function AppLayout({ children }: { children: React.ReactNode }) {
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  return (
    <div className="min-h-screen bg-background">
      {isDesktop ? <Sidebar /> : null}
      <main className={cn(
        "pb-20 lg:pb-0", // Bottom padding for mobile nav
        isDesktop && "lg:ml-64" // Sidebar offset on desktop
      )}>
        <Header />
        {children}
      </main>
      {!isDesktop && <BottomNav />}
    </div>
  );
}
```

### Anti-Patterns to Avoid

- **Serving static files before API routes:** 404s for API endpoints - always
  mount API routers first
- **Hardcoded API URLs:** Use environment variables or relative paths
- **Missing SPA fallback:** Direct navigation to /recipes/123 returns 404
- **Ignoring tap target size:** Touch targets under 44px fail accessibility
- **Docker volume at /app/data:** Must persist SQLite database file

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API state management | Custom fetch + useState | TanStack Query | Caching, deduplication, retry logic |
| Accessible components | Custom buttons/inputs | shadcn/ui + Radix | ARIA compliance, keyboard nav |
| Responsive navigation | Custom media queries | Tailwind responsive prefixes | Consistent breakpoints |
| Docker deployment | Custom scripts | Multi-stage Dockerfile | Reproducible, cacheable builds |
| Environment config | Custom .env parsing | Pydantic Settings | Type validation, defaults |
| SPA routing fallback | Custom middleware | FastAPI catch-all route | Simple, one handler |

**Key insight:** The app uses standard patterns for React SPA + FastAPI backend.
Custom solutions add complexity without value.

## Common Pitfalls

### Pitfall 1: API Routes Return 404

**What goes wrong:** Static file handler catches API requests before they reach
routers.

**Why it happens:** FastAPI processes routes in order; `app.mount()` with
catch-all path matches everything.

**How to avoid:** Always register API routers BEFORE mounting StaticFiles. Use
specific path for static mount (`/static`) and catch-all only for unmatched
paths.

**Warning signs:** `/recipes` returns HTML instead of JSON.

### Pitfall 2: SQLite Database Lost on Container Restart

**What goes wrong:** Database file is inside container filesystem and lost when
container is replaced.

**Why it happens:** Containers are ephemeral; filesystem changes don't persist.

**How to avoid:** Mount volume at database path. Default is `./data/eat-it.db`,
so mount volume at `/app/data`.

```yaml
# docker-compose.yml
volumes:
  - eat-it-data:/app/data
```

**Warning signs:** Data disappears after `docker-compose down && docker-compose
up`.

### Pitfall 3: Vite Base Path Mismatch

**What goes wrong:** Built app tries to load assets from wrong path (e.g.,
`/assets/index.js` instead of `/static/assets/index.js`).

**Why it happens:** Vite default `base` is `/` but static files served from
`/static`.

**How to avoid:** Either set `base: '/static/'` in vite.config.ts OR serve
static files at root (recommended - simpler).

```typescript
// vite.config.ts
export default defineConfig({
  base: '/', // Default - static files served at root
});
```

Then mount at root in FastAPI or copy to a path that matches.

**Warning signs:** Browser console 404s for JS/CSS files.

### Pitfall 4: Tap Targets Too Small

**What goes wrong:** Interactive elements under 44px fail mobile accessibility.

**Why it happens:** Default component sizes from desktop-first libraries.

**How to avoid:** Add `min-h-[44px] min-w-[44px]` to all buttons, links,
checkboxes. Use Tailwind's `touch` variant for touch-specific sizing.

**Warning signs:** Difficult to tap items on mobile, accessibility audit
failures.

### Pitfall 5: CORS Errors in Development

**What goes wrong:** Frontend dev server (port 5173) can't reach backend (port
8000).

**Why it happens:** Browser blocks cross-origin requests by default.

**How to avoid:** Configure CORS in FastAPI for development:

```python
from fastapi.middleware.cors import CORSMiddleware

if settings.environment == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

**Warning signs:** Browser console shows "CORS policy" errors.

## Code Examples

### Environment Variable Configuration

```python
# src/eat_it/config.py - Add port and environment
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EAT_IT_",
        env_file=".env",
    )

    database_url: str = "sqlite:///./data/eat-it.db"
    embedding_model: str = "all-MiniLM-L6-v2"
    port: int = 8000
    environment: str = "production"
```

```bash
# .env or environment variables
EAT_IT_DATABASE_URL=sqlite:///./data/eat-it.db
EAT_IT_PORT=8000
EAT_IT_ENVIRONMENT=production
```

### Docker Compose for Easy Deployment

```yaml
# docker-compose.yml
version: "3.8"

services:
  eat-it:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "${EAT_IT_PORT:-8000}:8000"
    volumes:
      - eat-it-data:/app/data
    environment:
      - EAT_IT_DATABASE_URL=sqlite:///./data/eat-it.db
      - EAT_IT_PORT=8000
    restart: unless-stopped

volumes:
  eat-it-data:
```

### TanStack Query Provider Setup

```typescript
// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayout>
        <Routes>
          <Route path="/" element={<RecipeBinder />} />
          <Route path="/recipes/:id" element={<RecipeDetail />} />
          <Route path="/shopping" element={<ShoppingList />} />
          <Route path="/search" element={<Search />} />
          <Route path="/import" element={<RecipeImport />} />
        </Routes>
      </AppLayout>
    </QueryClientProvider>
  );
}
```

### 44px Tap Target Component

```typescript
// src/components/ui/TouchButton.tsx
interface TouchButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
}

export function TouchButton({
  className,
  variant = 'primary',
  ...props
}: TouchButtonProps) {
  return (
    <button
      className={cn(
        // Minimum 44px tap target
        'min-h-[44px] min-w-[44px]',
        // Padding ensures comfortable tap area
        'px-4 py-3',
        // Other styles based on variant
        variantStyles[variant],
        className
      )}
      {...props}
    />
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Create React App | Vite | 2020+ | Faster builds, better DX |
| Global useState for API | TanStack Query | 2021+ | Automatic caching, loading states |
| Custom fetch wrappers | Native fetch + TanStack | 2022+ | Simpler, fewer dependencies |
| Docker single-stage | Multi-stage builds | 2018+ | Smaller images, better caching |
| nginx reverse proxy | FastAPI StaticFiles | 2023+ | Simpler single-container deploy |

**Deprecated/outdated:**

- **Create React App:** Use Vite instead - faster, modern defaults
- **SWR:** TanStack Query has better mutation support and devtools
- **Separate containers for frontend/backend:** Single container simpler for
  self-hosted apps

## Open Questions

1. **Binary Distribution (alternative to Docker)**

   - What we know: Requirement mentions "Docker or single binary"
   - What's unclear: Binary distribution adds complexity (PyInstaller, platform
     builds)
   - Recommendation: Start with Docker only. Add binary distribution in v2 if
     requested. Docker covers the "minimal setup" requirement.

2. **CDN for Static Assets**

   - What we know: Not mentioned in requirements
   - What's unclear: Whether self-hosted users expect CDN performance
   - Recommendation: Skip for MVP. Self-hosted = local network or VPS with
     reasonable latency.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Vitest (frontend) + pytest (backend) |
| Config file | `vitest.config.ts` + `pyproject.toml` |
| Quick run command (frontend) | `npm run test -- --run` |
| Quick run command (backend) | `pytest tests/ -x -q` |
| Full suite command | `npm run test && pytest` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| DATA-02 | Docker container builds successfully | integration | `docker build -t eat-it .` | Wave 0 |
| DATA-02 | Static files served at root | integration | `pytest tests/test_staticfiles.py -x` | Wave 0 |
| DATA-02 | SPA fallback returns index.html | integration | `pytest tests/test_staticfiles.py::test_spa_fallback -x` | Wave 0 |
| DATA-02 | SQLite persists across restarts | integration | `pytest tests/test_docker_volume.py -x` | Wave 0 |
| SHOP-03 | Tap targets are 44px minimum | unit | `npm run test -- --run tap-targets` | Wave 0 |

### Sampling Rate

- **Per task commit:** `npm run test -- --run` or `pytest tests/ -x -q`
- **Per wave merge:** Full suite: `npm run test && pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_staticfiles.py` - covers static file serving, SPA fallback
- [ ] `tests/test_docker_volume.py` - covers data persistence
- [ ] `.planning/UI/src/__tests__/tap-targets.test.ts` - covers 44px minimum
- [ ] `vitest.config.ts` - frontend test configuration
- [ ] Framework install: `npm install -D vitest @testing-library/react` - if not
  present

## Sources

### Primary (HIGH confidence)

- TanStack Query v5 documentation - installation, setup, query patterns
- FastAPI StaticFiles documentation - mounting static files, SPA patterns
- Docker multi-stage builds documentation - build patterns, best practices
- shadcn/ui Vite installation guide - component setup

### Secondary (MEDIUM confidence)

- `.planning/UI/DESIGN.md` - design system tokens, component patterns
- `.planning/UI/package.json` - current dependency versions
- `src/eat_it/main.py` - existing FastAPI structure
- `src/eat_it/config.py` - existing configuration pattern
- `pyproject.toml` - Python dependencies, test configuration

### Tertiary (LOW confidence)

- None - all critical information from primary or secondary sources

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - All libraries already in use or well-documented
- Architecture: HIGH - Patterns are standard for React SPA + FastAPI
- Pitfalls: HIGH - Common issues well-documented in official docs

**Research date:** 2026-03-03
**Valid until:** 2026-04-03 (30 days - stable patterns, but verify versions)
