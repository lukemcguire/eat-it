# Phase 2: Recipe Import and CRUD - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Backend API for importing recipes from URLs (with preview-before-save), manual
CRUD operations, notes/rating, duplicate detection, and data export. Frontend
is Phase 5 - this phase focuses on API endpoints and business logic.

</domain>

<decisions>
## Implementation Decisions

### Import Flow

- **Stateless preview→save**: Client calls /parse, receives parsed data, then
  calls /recipes to save. No server-side preview caching.
- **Minimal parsing metadata**: Return parsed recipe data on success, or
  structured error on failure. No confidence scores or provenance.
- **Structured error responses**: Parsing failures return error code, message,
  and suggested action (e.g., MANUAL_ENTRY_REQUIRED).
- **Partial data handling**: Return what was parsed with null for missing
  required fields. Frontend highlights gaps for user to fill.

### Duplicate Detection

- **URL-only matching**: Only exact URL match counts as duplicate. No title
  similarity checking.
- **Warning with override**: Return warning with existing recipe info, but allow
  save to proceed with force=true flag.
- **Full comparison data**: Return complete existing recipe when duplicate
  detected so user can compare before deciding.
- **Check at parse time**: Duplicate detection runs during /parse step so user
  sees warning in preview before attempting save.

### Recipe Validation

- **Minimal required fields**: Only title is required. All other fields
  optional for maximum flexibility.
- **Plain text ingredients**: Ingredients stored as text strings. Schema has
  structured fields but validation doesn't require them (parser populates when
  possible).
- **Strict validation**: Return 422 with specific field errors for invalid
  data. No lenient coercion.
- **Separate annotation endpoints**: Rating and notes have dedicated endpoints
  (PATCH /recipes/{id}/rating, PATCH /recipes/{id}/notes) rather than being
  part of recipe CRUD.

### Export Design

- **Single endpoint**: /recipes/export?format=json|csv with format as query
  parameter.
- **All fields included**: Export includes all recipe data including metadata.
  No field selection.
- **All recipes only**: No scoped export (no filtering, no selection). Export
  returns entire collection.
- **File download response**: Return with Content-Disposition header for
  browser download behavior.

### Claude's Discretion

- Exact error code values and message wording
- Ingredient text format in CSV export (newline handling)
- Response content type specifics for each format
- Pagination strategy for recipe listing endpoint

</decisions>

<specifics>
## Specific Ideas

- No specific product references mentioned — user preferred recommended
  approaches throughout

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-recipe-import-and-crud*
*Context gathered: 2026-02-25*
