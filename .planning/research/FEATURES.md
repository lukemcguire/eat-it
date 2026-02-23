# Feature Research

**Domain:** Self-hosted recipe management + collaborative shopping lists
**Researched:** 2026-02-23
**Confidence:** MEDIUM-HIGH (competitor features from official docs and
multiple community sources; user pain points from Mealie 2024 survey
and HN/Lemmy discussions)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| URL recipe import | Every competitor has it; #1 requested feature in community discussions | MEDIUM | recipe-scrapers covers 611+ sites; wild_mode for additional; failure fallback is required |
| Manual recipe entry/edit | Import fails ~10–20% of the time on small blogs; users need an out | LOW | Full CRUD on all recipe fields |
| Recipe detail view | Core reading experience during cooking | LOW | Title, image, ingredients, steps, servings, time, source |
| Keyword/tag search | Expected as baseline before any AI features | LOW | Filter by ingredient, tag, category |
| Generate shopping list from recipes | Core value prop of any recipe+shopping tool | MEDIUM | Ingredient deduplication and quantity summing are the hard part |
| Edit shopping list manually | Users always add items outside recipes | LOW | Add, remove, edit, adjust quantity, check off |
| Mobile-optimized checklist view | Grocery shopping happens on phones | LOW | Large tap targets, check-off state, high contrast |
| Multi-device list access | Co-shoppers need same list; poll/refresh sync is sufficient for MVP | LOW | No websockets needed for MVP; refresh-to-sync acceptable |
| Data export | Self-hosters demand data sovereignty | LOW | JSON and/or CSV; one of the most common user demands |
| Docker deployment | Standard expectation for self-hosted tools | LOW | docker-compose with SQLite file volume |
| Graceful import failure | Parser fails on ~10-20% of sites; users expect feedback and fallback | LOW | Clear error message + manual entry path |
| Recipe rating and notes | Personal annotation is expected in any recipe collection | LOW | Per-recipe, private, not linked to shopping lists |
| Duplicate detection on import | Without it users accumulate duplicates silently | LOW | URL-based deduplication is simplest; warn don't block |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Natural language semantic search | No competitor offers local-only AI search; users currently get keyword-only search | HIGH | sentence-transformers locally; no API key; "vegetarian dinner for 4" resolves correctly |
| Preview-before-save import flow | Most apps auto-save on import, polluting collection with bad parses | LOW | User reviews parsed data, edits inline, then explicitly saves — prevents garbage accumulation |
| Shareable list link/PIN (no account required) | Forcing accounts to share a list alienates non-technical co-shoppers | LOW | PIN or UUID-based link; guest view + check-off; critical for the "Maria shares with partner" use case |
| Plugin/provider pattern for importers | Community can add parsers (OCR, video, foreign sites) without touching core | MEDIUM | Implemented as architecture from day one; even if no external plugins ship in v1 |
| Versioned metadata field in schema | Future plugins can attach data without schema hacks | LOW | `metadata: {}` JSON field on Recipe and ShoppingList — low cost, high future value |
| Offline-capable PWA | Competitors' mobile experiences are universally complained about; no competitor does this well | HIGH | Defer to post-MVP; but architect with it in mind |
| Extensible import provider registry | Scan plugin directory at startup; new importers registered without core changes | MEDIUM | Even OCR and video parsers slot in without rewrites |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time collaborative editing (websockets) | Users want live shared shopping lists | Adds infra complexity, state sync, merge conflicts; not necessary for household scale | Refresh-to-sync in MVP; websockets in v2 after validation |
| Meal planning calendar | Users see it in Mealie/Tandoor and expect it | Significant scope addition with its own UI/UX complexity; low value for MVP's use case (shopping list generation is the goal, not week-view planning) | Shopping list can be populated from any set of recipes without a calendar |
| Nutritional calculations | A common feature request across Mealie surveys | Requires ingredient → nutrient database linkage (USDA or similar); high data complexity for questionable cooking-session value | Tag recipes with dietary labels (vegan, gluten-free) as a simple proxy |
| Grocery store aisle ordering | Tandoor's power feature; users want store-layout-sorted lists | Complex UI to configure per store; negligible value for MVP household users | Category-based grouping of ingredients is sufficient (produce, dairy, etc.) |
| Native mobile apps | Users complain about web PWAs | Development cost is 3–5x a responsive web app; Flutter/React Native add maintenance burden | Mobile-first responsive web + PWA manifest; matches PRD scope |
| Third-party grocery delivery integration (Instacart etc.) | "Why not just order it?" | Privacy-hostile by definition; regional/API availability unpredictable; contradicts self-hosted value prop | Out of scope per PRD; only pursue if users demand post-launch |
| Social/public recipe sharing (ActivityPub, community feed) | Some users want to share across instances | Social graph is a product by itself; complexity dwarfs the recipe feature | Export + share-by-link covers the legitimate use case |
| Serving size auto-scaling with smart unit conversion | #1 most-requested feature in Mealie 2024 survey | Requires ingredient parsing into structured quantity+unit+food tuples; unit conversion graph; significant NLP complexity | Basic "multiply all quantities by N" as MVP; proper scaling as v1.x feature with ingredient NLP library |

## Feature Dependencies

```text
[Recipe storage (CRUD)]
    └──required by──> [URL import → parse → save]
    └──required by──> [Manual recipe entry]
    └──required by──> [Recipe search (keyword)]
    └──required by──> [Natural language search]
    └──required by──> [Generate shopping list]
    └──required by──> [Data export]

[Recipe storage]
    └──requires──> [Versioned schema with metadata field]

[Generate shopping list]
    └──requires──> [Ingredient deduplication + quantity summing]
    └──requires──> [Shopping list storage (CRUD)]

[Shopping list storage]
    └──required by──> [Manual list editing]
    └──required by──> [Mobile checklist view]
    └──required by──> [Multi-device access / sync]
    └──required by──> [Shareable link/PIN]

[Natural language search]
    └──requires──> [Recipe storage]
    └──requires──> [Embedding model (sentence-transformers)]
    └──requires──> [Vector index (SQLite-vec or similar)]
    └──enhances──> [Keyword search as fallback]

[Plugin provider registry]
    └──enhances──> [URL import] (adds more parsers)
    └──enhances──> [Future: OCR import, video import]

[Preview-before-save flow]
    └──requires──> [URL import parse step]
    └──enhances──> [Manual recipe entry] (same edit UI reused)
```

### Dependency Notes

- **Shopping list requires recipe storage:** Can't generate a list from
  recipes that aren't stored. Recipe CRUD must be complete before
  shopping list generation.
- **Natural language search requires embeddings:** Embeddings must be
  generated at recipe save time; vector index must be queryable.
  Falls back to keyword search if embedding model unavailable.
- **Shareable list requires shopping list storage:** The share link
  just exposes a read+check-off view of an existing list record.
- **Preview-before-save is an import flow variant:** The same recipe
  edit form is used for both manual entry and post-parse review;
  build once, use in both flows.
- **Plugin registry enhances but does not block MVP:** The provider
  pattern should be in place from day one (architecture), but no
  external plugins need to ship in v1.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] URL recipe import with preview-before-save — core value prop;
  failure fallback to manual entry required
- [ ] Manual recipe entry/edit — covers import failures and
  hand-written recipes
- [ ] Recipe CRUD with rating and notes — foundational; all other
  features depend on it
- [ ] Keyword + tag search — baseline discoverability before AI search
- [ ] Natural language semantic search (local embeddings) — primary
  differentiator; without it the app is just Mealie with less polish
- [ ] Generate shopping list from selected recipes with ingredient
  deduplication — second core value prop
- [ ] Manual shopping list editing (add/remove/edit/check-off) —
  required for real shopping use
- [ ] Mobile-optimized checklist view — shopping happens on phones;
  large tap targets, check-off UX
- [ ] Multi-device access (refresh-to-sync, no websockets) — enables
  the co-shopper use case
- [ ] Shareable list link or PIN — co-shopper access without mandatory
  accounts
- [ ] Data export (JSON + CSV) — self-hosters demand this on launch
- [ ] Docker deployment — expected baseline for self-hosted tools
- [ ] Plugin provider pattern in architecture — enables future parsers
  without rewrites; no user-visible plugin UI needed in v1
- [ ] Versioned metadata field on Recipe + ShoppingList schemas — zero
  cost now; prevents schema hacks later
- [ ] Duplicate URL detection on import — prevents silent collection
  pollution

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Serving size scaling (multiply quantities by N) — #1 user
  request across all competitors; add after core import/search/list
  is validated
- [ ] Ingredient category grouping on shopping list — "produce, dairy,
  pantry" grouping reduces friction during shopping
- [ ] Recipe collections / cookbooks — power user organization once
  library grows past ~50 recipes
- [ ] PWA manifest + offline checklist caching — improves shopping
  experience in low-signal stores; medium effort
- [ ] Improved import failure handling (partial parse + user edit) —
  upgrade from hard-fail to "here's what I got, fix the rest"
- [ ] Tag/ingredient deduplication tools — becomes necessary at scale;
  Mealie users explicitly requested this in 2024 survey

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] OCR / image-based recipe import — high demand, high complexity;
  defer until plugin architecture is proven
- [ ] Real-time collaborative editing (websockets) — post-MVP; not
  required for household scale
- [ ] Advanced AI: recipe categorization, dietary analysis,
  personalized recommendations — defer until core AI search is
  validated
- [ ] Video recipe parsing (YouTube/TikTok/Instagram) — slots into
  plugin architecture; significant complexity
- [ ] Plugin/extension API for community contributors — expose and
  document the internal provider pattern externally
- [ ] Meal planning calendar view — medium value, high UX complexity
- [ ] Nutritional calculation — requires ingredient database linkage
- [ ] Grocery store aisle layout configuration — power feature for
  Tandoor fans; not needed at household scale

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| URL recipe import | HIGH | MEDIUM | P1 |
| Natural language search | HIGH | HIGH | P1 |
| Generate shopping list | HIGH | MEDIUM | P1 |
| Mobile checklist view | HIGH | LOW | P1 |
| Manual recipe entry/edit | HIGH | LOW | P1 |
| Shareable list link/PIN | HIGH | LOW | P1 |
| Multi-device sync (refresh) | HIGH | LOW | P1 |
| Data export | MEDIUM | LOW | P1 |
| Docker deployment | MEDIUM | LOW | P1 |
| Preview-before-save flow | MEDIUM | LOW | P1 |
| Rating and notes | MEDIUM | LOW | P1 |
| Plugin provider pattern | LOW (now) / HIGH (future) | MEDIUM | P1 |
| Serving size scaling | HIGH | MEDIUM | P2 |
| Ingredient category grouping | MEDIUM | LOW | P2 |
| PWA offline support | MEDIUM | MEDIUM | P2 |
| OCR import | HIGH | HIGH | P3 |
| Real-time collaboration | MEDIUM | HIGH | P3 |
| Video recipe parsing | MEDIUM | HIGH | P3 |
| Meal planning calendar | MEDIUM | HIGH | P3 |
| Nutritional calculations | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Mealie | Tandoor | KitchenOwl | Eat It (our approach) |
|---------|--------|---------|------------|----------------------|
| URL import | Yes, 611+ sites | Yes | Yes | Yes, recipe-scrapers |
| Manual entry | Yes | Yes | Yes | Yes |
| Preview before save | No (auto-save) | No (auto-save) | No (auto-save) | Yes — differentiator |
| Natural language AI search | No (keyword + fuzzy) | No (keyword + fuzzy) | No | Yes — local embeddings, no API |
| Shopping list from recipes | Yes | Yes | Yes | Yes |
| Ingredient deduplication | Yes (ML-powered) | Yes | Yes | Yes |
| Serving size scaling | Basic | Yes (smart, per-ingredient) | No | Defer to v1.x |
| Real-time list sync | No | No | Yes | No (refresh-to-sync MVP) |
| Share list without account | Limited | Limited | Household model | Yes, PIN/link — differentiator |
| Meal planning calendar | Yes | Yes | Yes | No in MVP — anti-feature |
| Nutritional info | No | Yes | No | No in MVP |
| Store layout sorting | No | Yes | Auto-learn | No in MVP |
| Mobile app quality | Poor (community app) | Better (Kitshn) | Good (Flutter) | Responsive web + PWA path |
| Data export | Yes (JSON, markdown) | Yes | Limited | Yes (JSON + CSV) |
| Docker deploy | Yes | Yes | Yes | Yes |
| Plugin/extensibility | Limited | No | No | Yes — architecture from day 1 |
| Local AI, no API key | No | No | No | Yes — differentiator |
| Privacy-first, no telemetry | Yes | Yes | No | Yes |

## Gap Analysis

### In PRD but absent from typical competitors

| PRD Feature | Gap | Impact |
|-------------|-----|--------|
| Local embedding search | No competitor does this; they use keyword/fuzzy only | Major differentiator; validates the whole "privacy-first AI" positioning |
| Preview-before-save import | All competitors auto-save; bad parses pollute collections | Differentiator; reduces user frustration significantly |
| PIN/link sharing without accounts | Competitors require account creation for sharing | Lowers barrier for the co-shopper persona dramatically |
| Plugin provider pattern in architecture | No competitor exposes extension points at this level | Positions Eat It for community contributions in v2 |
| Versioned metadata schema field | No competitor designs for this explicitly | Prevents future technical debt |

### In typical competitors but not yet in PRD

| Competitor Feature | PRD Status | Recommendation |
|--------------------|------------|----------------|
| Serving size scaling | Not mentioned | Add to v1.x scope; it's the #1 feature request across all competitors |
| Ingredient sectioning within recipe | Not mentioned | Low complexity; add as recipe editor enhancement in v1 |
| Duplicate detection/warning on import | Mentioned in UX section, not in requirements | Formalize as a requirement; URL-hash dedup is trivial |
| Tag/label management (bulk merge, rename) | Not mentioned | Defer to v1.x; becomes necessary past 100 recipes |
| Recipe composition / sub-recipes | Not mentioned | Defer to v2+; niche use case but loved by power users |
| Offline PWA checklist | Not mentioned | Add to v1.x; shopping stores have poor signal |

## Sources

- Mealie official documentation and feature list:
  https://docs.mealie.io/documentation/getting-started/introduction/
- Mealie 2024 October user survey (feature requests and complaints):
  https://docs.mealie.io/news/surveys/2024-october/q12/ and q13/
- Tandoor Recipes GitHub and official site:
  https://github.com/TandoorRecipes/recipes and https://tandoor.dev/
- XDA Developers: Tandoor vs Mealie comparison:
  https://www.xda-developers.com/reasons-tandoor-replaced-mealie-for-managing-my-recipes/
- KitchenOwl features page: https://kitchenowl.org/features/
- Hacker News discussion on Mealie (community pain points):
  https://news.ycombinator.com/item?id=30623852
- Lemmy/SDF community suggestions for self-hosted recipe managers:
  https://lemmy.sdf.org/post/351462
- recipe-scrapers Python library (611+ supported sites):
  https://github.com/hhursev/recipe-scrapers
- awesome-selfhosted recipe management category:
  https://awesome-selfhosted.net/tags/recipe-management.html

---
*Feature research for: self-hosted recipe management + shopping lists*
*Researched: 2026-02-23*
