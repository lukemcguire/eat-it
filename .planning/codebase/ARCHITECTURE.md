# Architecture

**Analysis Date:** 2026-02-23

## Pattern Overview

**Overall:** Layered Architecture with API-centric design

**Key Characteristics:**
- Separation of concerns into distinct layers (presentation, API, business,
  data)
- Backend API serving recipe management, search, and shopping list operations
- Frontend web application with responsive design for desktop and mobile
- Local-first data storage (SQLite or similar embedded database)
- Modular design enabling future extensibility

## Layers

**Presentation Layer (Frontend):**
- Purpose: User-facing web interface for recipe import, search, and shopping
  list management
- Location: `frontend/` (to be created; likely React, Vue, or Svelte)
- Contains: Components, pages, UI logic, responsive layouts
- Depends on: API Layer (HTTP/REST endpoints)
- Used by: Web browsers (desktop and mobile)

**API Layer (Backend):**
- Purpose: RESTful API exposing recipe, search, and shopping list operations
- Location: `src/api/` (to be created)
- Contains: Route handlers, request validation, response formatting
- Depends on: Service Layer
- Used by: Frontend application, potential future integrations

**Service/Business Logic Layer:**
- Purpose: Core business logic for recipe import, AI search, list generation,
  and collaboration
- Location: `src/services/` (to be created)
- Contains: Recipe service, search service, shopping list service, parser
  integration
- Depends on: Data Layer, external recipe parsers
- Used by: API Layer

**Data Layer (Persistence):**
- Purpose: Database abstraction and data access patterns
- Location: `src/data/` or `src/db/` (to be created)
- Contains: ORM models, database migrations, query builders
- Depends on: SQLite or embedded database
- Used by: Service Layer

**Integration Layer:**
- Purpose: External service integrations
- Location: `src/integrations/` (to be created)
- Contains: Recipe parser wrappers, export/import handlers
- Depends on: External libraries (recipe-scrapers, etc.)
- Used by: Service Layer

## Data Flow

**Recipe Import Flow:**

1. User provides recipe URL or manual recipe data via Frontend
2. API receives import request and validates input
3. Service Layer calls Recipe Parser (integration layer) to extract structured
   data
4. Parsed recipe is validated and transformed by Recipe Service
5. Data Layer saves recipe to SQLite database
6. Response returned to Frontend with success/failure status

**Search Flow:**

1. User enters natural language query (e.g., "vegetarian dinner") in Frontend
2. Frontend sends search request to API
3. Search Service processes query using AI/NLP component
4. Data Layer queries database for matching recipes
5. Results ranked by relevance and returned to Frontend
6. Frontend displays recipe cards with preview information

**Shopping List Generation Flow:**

1. User selects multiple recipes from search results in Frontend
2. Frontend sends selected recipe IDs to API
3. Shopping List Service retrieves recipes from Data Layer
4. Service deduplicates and aggregates ingredients from all recipes
5. Generated list stored in database with user association
6. List response returned to Frontend for editing and checkout
7. Changes to list items saved immediately on each update

**Multi-User Shopping List Sync:**

1. User A checks off item on shopping list (via mobile device)
2. Frontend sends update to API
3. Shopping List Service updates item status in database
4. Second user (User B) on different device fetches list
5. Data Layer returns current state including all previous updates
6. Frontend refreshes to show checked items from User A

**State Management:**

- Recipe state: Persisted in SQLite with immutable import timestamps
- Search state: Stateless API queries, client-side UI state in frontend
- Shopping list state: Persisted in SQLite with real-time item updates (sync
  on refresh, not websocket-based in MVP)
- User/collaboration state: Lightweight session or token-based for optional
  login

## Key Abstractions

**Recipe:**
- Purpose: Represents a single recipe with ingredients, instructions, and
  metadata
- Examples: `src/models/recipe.py`, recipe database schema
- Pattern: Data class/ORM model with structured ingredient and instruction
  lists

**Shopping List:**
- Purpose: Aggregates ingredients from multiple recipes into a unified list
  with purchase status tracking
- Examples: `src/models/shopping_list.py`, shopping list items model
- Pattern: Parent-child relationship (list contains items with checked status)

**Parser Interface:**
- Purpose: Abstract interface for recipe extraction from URLs or manual data
- Examples: `src/integrations/recipe_parser.py`
- Pattern: Strategy pattern allowing multiple parser implementations
  (fallback to manual entry if parsing fails)

**Search Index:**
- Purpose: Provides fast natural language and keyword-based recipe discovery
- Examples: `src/services/search_service.py`
- Pattern: Wrapper around AI/NLP component with fallback to simple keyword
  matching

## Entry Points

**Web Server Entry:**
- Location: `src/main.py` (to be created)
- Triggers: Application startup (Python process or container launch)
- Responsibilities: Initialize database, set up API routes, start HTTP server

**API Root:**
- Location: `src/api/__init__.py` (to be created)
- Routes: `/api/recipes`, `/api/search`, `/api/shopping-lists`
- Responsibilities: Route HTTP requests to appropriate handlers

**Frontend Entry:**
- Location: `frontend/index.html` (to be created)
- Triggers: User opens application URL in browser
- Responsibilities: Load frontend application, establish API communication

## Error Handling

**Strategy:** Graceful degradation with user feedback

**Patterns:**
- Recipe parsing errors return structured error response with fallback to
  manual entry option
- Search failures fall back to keyword-only search if AI/NLP component
  unavailable
- Database errors return 500 with generic message; details logged server-side
- Network errors on frontend trigger retry with exponential backoff
- Missing or invalid recipe data handled by validation layer before
  persistence

## Cross-Cutting Concerns

**Logging:** Python logging module to file or stdout; structured JSON logs for
debugging recipe imports, search queries, and list operations

**Validation:** Input validation at API layer (recipe fields, search queries,
list item edits); ORM-level validation at data layer

**Authentication:** Optional simple login or guest mode (single-user by
default); session/token-based if collaboration enabled; no OAuth required in
MVP

---

*Architecture analysis: 2026-02-23*
