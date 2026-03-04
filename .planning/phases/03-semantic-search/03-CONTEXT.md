# Phase 3: Semantic Search - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Natural language recipe search using local embeddings (no internet/API key
required), with keyword/tag fallback. Users find recipes by describing what
they want in plain English. Creating embeddings is part of this phase; the
embedding model infrastructure was set up in Phase 1.

</domain>

<decisions>
## Implementation Decisions

### Search Input Mode
- Single unified search field that handles both semantic and keyword queries
- System auto-detects intent (no mode toggle)
- Simple placeholder text ("Search recipes...") - no example hints
- No autocomplete suggestions
- No pre-filtering options - search queries all recipes

### Results Presentation
- Show top 20 results with relevance score cutoff
- Each result displays: recipe name, source URL, picture thumbnail
- Results sorted by relevance only (no sort options)
- Simple "No recipes found" message when no results

### Fallback Behavior
- Automatic fallback to keyword search when semantic returns no results
- Silent fallback - user not notified which search type was used
- Fall back to keyword search if semantic search unavailable (e.g., model
  fails to load)
- Search only recipes with embeddings for semantic results; unembedded
  recipes found via keyword fallback

### Embedding UX
- Generate embeddings immediately when recipe is saved
- Silent generation - no progress indicator or status display
- Recipes are searchable immediately after save (keyword fallback handles
  unembedded state)
- Regenerate embeddings automatically when recipe content changes
- No manual regenerate option

### Claude's Discretion
- Exact relevance score threshold for result cutoff
- How to combine/hybridize results when partial embedding coverage
- Embedding field selection (title only, title + ingredients, full text)
- Keyword search implementation (LIKE queries vs FTS5)

</decisions>

<specifics>
## Specific Ideas

No specific references - user preferred recommended/standard approaches
throughout.

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope.

</deferred>

---

*Phase: 03-semantic-search*
*Context gathered: 2026-03-03*
