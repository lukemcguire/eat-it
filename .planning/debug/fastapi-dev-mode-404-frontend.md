---
status: diagnosed
trigger: "FastAPI dev mode returns 404 JSON instead of serving frontend"
created: 2026-03-05T00:00:00Z
updated: 2026-03-05T00:00:00Z
---

## Current Focus

hypothesis: This is a design gap - FastAPI intentionally returns 404 in dev mode
test: Reviewed main.py SPA fallback logic and vite.config.ts proxy setup
expecting: Confirm dev mode uses Vite proxy, not FastAPI for frontend
next_action: Report diagnosis - this is expected behavior, not a bug

## Symptoms

expected: Navigate to http://localhost:8000 should serve the frontend UI
actual: Returns {"detail": "Not found"} JSON response
errors: None - this is intentional behavior
reproduction: Run FastAPI dev server without static/ directory, navigate to root
started: Always been this way - design decision, not a regression

## Eliminated

- hypothesis: Bug in SPA fallback routing
  evidence: Code is intentionally checking STATIC_DIR_EXISTS and returning 404 when false
  timestamp: 2026-03-05T00:00:00Z

## Evidence

- timestamp: 2026-03-05T00:00:00Z
  checked: main.py lines 84-118
  found: SPA fallback only activates when static/ directory exists (line 86, 91, 113-117)
  implication: This is intentional design - dev mode relies on Vite dev server

- timestamp: 2026-03-05T00:00:00Z
  checked: vite.config.ts lines 12-16
  found: Vite dev server proxies /recipes and /shopping-lists to localhost:8000
  implication: Dev workflow is: Vite on port 5173 -> proxies API to FastAPI on 8000

- timestamp: 2026-03-05T00:00:00Z
  checked: static/ directory existence
  found: static/ directory does not exist
  implication: No built frontend assets, so SPA fallback correctly returns 404

- timestamp: 2026-03-05T00:00:00Z
  checked: config.py
  found: Has environment setting (default: "production") but not used to switch SPA behavior
  implication: The current approach uses static/ existence as the mode detector

## Resolution

root_cause: Design gap - the intended development workflow uses two servers (Vite + FastAPI), not FastAPI alone. FastAPI returns 404 for non-API routes in dev mode because there are no static assets to serve.

fix: Not a bug. Two options for improvement:
  1. **Recommended**: Update documentation to clarify dev workflow requires running both servers
  2. **Alternative**: Add a dev mode that proxies to Vite or returns HTML with redirect

verification: N/A - this is expected behavior
files_changed: []
