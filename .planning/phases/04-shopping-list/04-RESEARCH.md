# Phase 4: Shopping List - Research

**Researched:** 2026-03-03
**Domain:** Collaborative shopping lists with ingredient combining and real-time sync
**Confidence:** HIGH

## Summary

This phase implements collaborative shopping lists generated from recipes, with
ingredient deduplication, mobile-optimized checking, and real-time sync via
WebSockets. The existing codebase already has basic ShoppingList and
ShoppingListItem models, but lacks store section organization, ingredient
combining logic, WebSocket sync, and shareable links.

**Primary recommendation:** Build on existing models with ingredient-parser for
smart combining, FastAPI native WebSockets for real-time sync, and
secrets.token_urlsafe for shareable links.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Ingredient Combining
- **Smart combining**: Parse quantities, normalize units, sum amounts for the
  same ingredient across multiple recipes
- **Unit normalization**: Convert between compatible units when possible
  (e.g., 1 cup + 8 oz = 1.5 cups for the same ingredient)
- **Similar ingredients stay separate**: "onion" and "red onion" remain as
  distinct items — user decides on substitutions
- **Preparation ignored**: "1 onion (chopped)" and "1 onion (diced)" combine
  to just "2 onions" — prep doesn't matter at the grocery store

#### List Organization
- **Multiple named lists**: Users can have multiple shopping lists
  (e.g., "Weekly groceries", "Party supplies")
- **Group by store section**: Items grouped by store section (Produce, Dairy,
  Meat, etc.) for efficient store navigation
- **Hybrid section model**: Start with predefined sections (Produce, Dairy,
  Meat, Bakery, Pantry, Frozen, Other), allow user to add/edit/remove
- **Manual reordering**: Users can drag to reorder items within sections

#### Sharing Mechanics
- **Link = full access**: Anyone with the link can view AND edit the list
  (no separate view-only mode)
- **Random string links**: Format like `/list/abc123xyz` — easy to share via
  text/email, no naming conflicts
- **Auto-expire**: Links expire after a set period (e.g., 7 days) — prevents
  stale access while supporting ongoing household use
- **Unlimited concurrent users**: No cap on simultaneous access

#### Sync Strategy
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

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SHOP-01 | Generate shopping list from selected recipes with deduplicated ingredients and summed quantities | ingredient-parser for parsing/combining |
| SHOP-02 | Add, remove, edit items and adjust quantities | CRUD endpoints + WebSocket broadcast |
| SHOP-03 | Check off items with mobile-optimized large tap targets (44px minimum) | Frontend concern; API returns checked state |
| SHOP-04 | Access same list from multiple devices on same network | WebSocket real-time sync |
| SHOP-05 | Second user can view and check off items from shared list | share_token + WebSocket broadcast |
| SHOP-06 | Share list via simple link or PIN without account | secrets.token_urlsafe for share_token |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ingredient-parser | 3.x | Parse and combine ingredient quantities | Only Python library with pint integration for unit conversion |
| FastAPI WebSockets | 0.115+ | Real-time sync | Native FastAPI support, no extra dependencies |
| secrets (stdlib) | 3.13+ | Generate share tokens | Cryptographically secure, URL-safe |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pint | (via ingredient-parser) | Unit conversion | Automatic when using ingredient-parser |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ingredient-parser | Custom regex parsing | ingredient-parser handles edge cases like "1 lb 2 oz", ranges, and metric/imperial |
| FastAPI WebSockets | Socket.IO | Socket.IO adds client library dependency; native WebSockets sufficient for household scale |
| secrets.token_urlsafe | UUID4 | tokens are shorter, more shareable; UUIDs are longer and look technical |

**Installation:**
```bash
uv add ingredient-parser
```

## Architecture Patterns

### Recommended Project Structure
```
src/eat_it/
├── models/
│   ├── shopping_list.py      # Existing - extend with section field
│   └── store_section.py      # NEW - store section model
├── schemas/
│   └── shopping_list.py      # NEW - Pydantic schemas for API
├── routers/
│   └── shopping_lists.py     # NEW - CRUD + WebSocket endpoints
├── services/
│   ├── ingredient_combiner.py  # NEW - combine ingredients from recipes
│   └── section_categorizer.py  # NEW - auto-categorize ingredients
└── websocket/
    └── manager.py            # NEW - connection manager for lists
```

### Pattern 1: ConnectionManager for Per-List WebSocket Rooms
**What:** Each shopping list has its own "room" of connected clients
**When to use:** Broadcasting changes only to users viewing that specific list
**Example:**
```python
# Source: FastAPI docs + pattern for per-resource rooms
from fastapi import WebSocket
from typing import Dict, Set

class ListConnectionManager:
    """Manages WebSocket connections per shopping list."""

    def __init__(self):
        # Map: list_id -> set of websocket connections
        self.connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, list_id: int, websocket: WebSocket):
        await websocket.accept()
        if list_id not in self.connections:
            self.connections[list_id] = set()
        self.connections[list_id].add(websocket)

    def disconnect(self, list_id: int, websocket: WebSocket):
        if list_id in self.connections:
            self.connections[list_id].discard(websocket)
            if not self.connections[list_id]:
                del self.connections[list_id]

    async def broadcast_to_list(self, list_id: int, message: dict):
        """Send message to all clients viewing this list."""
        if list_id in self.connections:
            dead_connections = set()
            for connection in self.connections[list_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(list_id, dead)
```

### Pattern 2: Ingredient Combining Service
**What:** Parse ingredients from recipes, normalize names, combine quantities
**When to use:** When generating a shopping list from selected recipes
**Example:**
```python
# Source: ingredient-parser Context7 docs
from ingredient_parser import parse_ingredient
from collections import defaultdict

def combine_ingredients(ingredient_strings: list[str]) -> list[dict]:
    """Combine ingredients from multiple recipes.

    - Normalizes names (lowercase, stripped)
    - Sums quantities for same ingredient+unit
    - Ignores preparation notes
    """
    combined = defaultdict(lambda: {"quantity": 0, "unit": None})

    for raw in ingredient_strings:
        result = parse_ingredient(raw, string_units=True)

        # Get normalized name (ignore preparation)
        name = result.name[0].text.lower().strip() if result.name else raw

        # Get quantity and unit
        if result.amount:
            amt = result.amount[0]
            qty = float(amt.quantity) if amt.quantity else 0
            unit = amt.unit if isinstance(amt.unit, str) else str(amt.unit)

            key = f"{name}|{unit}"
            combined[key]["quantity"] += qty
            combined[key]["unit"] = unit
            combined[key]["name"] = name
        else:
            # No quantity (e.g., "salt to taste")
            combined[f"{name}|"][name] = name

    return list(combined.values())
```

### Pattern 3: Share Token Generation
**What:** Generate URL-safe tokens for list sharing with expiration
**When to use:** When user wants to share a list
**Example:**
```python
# Source: Python stdlib
import secrets
from datetime import datetime, timedelta

def generate_share_token() -> str:
    """Generate a URL-safe share token.

    Returns 12-character token like 'abc123XYZ987'
    """
    return secrets.token_urlsafe(9)  # ~12 chars

def is_token_expired(list: ShoppingList) -> bool:
    """Check if share token has expired (7-day default)."""
    if not list.share_token or not list.updated_at:
        return False
    expiration = list.updated_at + timedelta(days=7)
    return datetime.utcnow() > expiration
```

### Anti-Patterns to Avoid
- **Storing parsed ingredients at recipe save time:** Ingredient parsing for
  shopping lists should happen at list-generation time, not when recipes are
  saved. This allows flexibility in combining logic without migrations.
- **WebSocket without heartbeat:** Connections can silently die; implement
  periodic ping/pong or rely on broadcast error detection.
- **Global broadcast for all lists:** Don't broadcast every change to every
  connected client; use per-list rooms.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parse "1 lb 2 oz" | Regex splitting | ingredient-parser | Handles ranges, fractions, metric/imperial |
| Convert cups to oz | Custom conversion table | pint (via ingredient-parser) | Maintains precision, handles edge cases |
| Generate share links | UUID or random int | secrets.token_urlsafe | Cryptographically secure, URL-safe, short |
| WebSocket room management | Dict of list of connections | ListConnectionManager pattern | Handles cleanup, per-list isolation |

**Key insight:** ingredient-parser with pint handles the "1 cup + 8 oz = 1.5 cups"
use case via CompositeIngredientAmount.combined() and convert_to() methods.

## Common Pitfalls

### Pitfall 1: Ingredient Name Normalization Too Aggressive
**What goes wrong:** "onion" and "red onion" get combined when they shouldn't
**Why it happens:** Overly aggressive normalization strips too much
**How to avoid:** Only normalize by lowercasing and stripping whitespace. Don't
stem, don't remove adjectives. "red onion" stays distinct from "onion".
**Warning signs:** Users see combined items that are actually different

### Pitfall 2: WebSocket Connection Leaks
**What goes wrong:** Disconnected clients remain in connection sets
**Why it happens:** Network drops don't trigger WebSocketDisconnect
**How to avoid:** Track failed sends during broadcast, remove dead connections.
Consider client-side heartbeat for long-lived connections.
**Warning signs:** Memory grows over time, broadcasts slow down

### Pitfall 3: Lost Updates with Last-Write-Wins
**What goes wrong:** Two users edit same item, one change is lost
**Why it happens:** Concurrent edits without locking
**How to avoid:** For grocery lists, this is acceptable (CONTEXT.md decision).
Document this behavior. Could add item-level versioning later if needed.
**Warning signs:** Users complain about disappearing changes

### Pitfall 4: Share Token Enumeration
**What goes wrong:** Attackers guess share tokens to access lists
**Why it happens:** Tokens too short or predictable
**How to avoid:** Use secrets.token_urlsafe(9) for ~12 chars = 64+ bits entropy.
This gives ~10^19 possible tokens, making enumeration impractical.
**Warning signs:** Logs show repeated access attempts with invalid tokens

## Code Examples

### WebSocket Endpoint for Shopping List
```python
# Source: FastAPI docs pattern
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from eat_it.websocket.manager import manager
from eat_it.database import get_session
from sqlmodel import Session

router = APIRouter()

@router.websocket("/ws/{list_id}")
async def websocket_list(
    websocket: WebSocket,
    list_id: int,
    session: Session = Depends(get_session)
):
    """WebSocket endpoint for real-time shopping list updates."""
    # Verify list exists
    from eat_it.models.shopping_list import ShoppingList
    db_list = session.get(ShoppingList, list_id)
    if not db_list:
        await websocket.close(code=4004, reason="List not found")
        return

    await manager.connect(list_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            # Other message types handled by REST API
            # WebSocket is primarily for receiving updates
    except WebSocketDisconnect:
        manager.disconnect(list_id, websocket)
    except Exception:
        manager.disconnect(list_id, websocket)
```

### CRUD with WebSocket Broadcast
```python
# Source: Pattern for sync
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter()

@router.patch("/lists/{list_id}/items/{item_id}")
async def update_item(
    list_id: int,
    item_id: int,
    update: ShoppingListItemUpdate,
    session: Session = Depends(get_session),
):
    """Update item and broadcast change to all connected clients."""
    item = session.get(ShoppingListItem, item_id)
    if not item or item.shopping_list_id != list_id:
        raise HTTPException(404, "Item not found")

    # Update item
    item_data = update.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)

    # Broadcast to all clients viewing this list
    await manager.broadcast_to_list(list_id, {
        "type": "item_updated",
        "item": item.model_dump()
    })

    return item
```

### Auto-Categorize Ingredient to Store Section
```python
# Source: Claude's discretion - simple keyword matching
DEFAULT_SECTIONS = [
    ("produce", ["onion", "garlic", "tomato", "lettuce", "carrot", "pepper", "celery"]),
    ("dairy", ["milk", "cheese", "butter", "cream", "yogurt", "egg"]),
    ("meat", ["chicken", "beef", "pork", "bacon", "sausage", "fish", "salmon"]),
    ("bakery", ["bread", "tortilla", "bagel", "roll"]),
    ("pantry", ["flour", "sugar", "salt", "oil", "vinegar", "rice", "pasta", "sauce"]),
    ("frozen", ["frozen", "ice cream"]),
]

def categorize_ingredient(name: str) -> str:
    """Categorize ingredient to store section."""
    name_lower = name.lower()
    for section, keywords in DEFAULT_SECTIONS:
        if any(kw in name_lower for kw in keywords):
            return section
    return "other"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Polling for sync | WebSocket push | 2024+ | Real-time UX without server load |
| Custom ingredient parsing | ingredient-parser + pint | 2023+ | Handles edge cases, unit conversion |
| UUID for share tokens | secrets.token_urlsafe | Always | Shorter, more shareable |

**Deprecated/outdated:**
- Socket.IO for simple use cases: Native WebSockets in FastAPI are sufficient
- Long polling: WebSocket is now universally supported

## Open Questions

1. **Should store sections be user-configurable per-list or global?**
   - What we know: CONTEXT.md says "hybrid section model" with predefined
     sections, allow add/edit/remove
   - What's unclear: Are sections per-user, per-list, or global?
   - Recommendation: Start with global sections (simplest), add per-user
     customization in v2

2. **How to handle item quantity edits after generation?**
   - What we know: Users can edit quantities
   - What's unclear: Does editing break the link to original recipe?
   - Recommendation: No link exists after generation (items are independent).
     User can always regenerate list.

## Sources

### Primary (HIGH confidence)
- /strangetom/ingredient-parser (Context7) - ingredient parsing API, pint integration
- /websites/fastapi_tiangolo (Context7) - WebSocket patterns, ConnectionManager

### Secondary (MEDIUM confidence)
- FastAPI WebSocket docs - verified ConnectionManager pattern, broadcast approach

### Tertiary (LOW confidence)
- None - all core patterns verified

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - ingredient-parser is mature, FastAPI WebSockets stable
- Architecture: HIGH - patterns follow FastAPI best practices
- Pitfalls: HIGH - based on documented behavior and common issues

**Research date:** 2026-03-03
**Valid until:** 30 days - stable libraries, low risk of breaking changes
