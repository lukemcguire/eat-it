---
phase: 06
slug: frontend-integration-wire-up-real-screen-components-in-app-tsx-add-missing-routes-and-connect-hooks-to-backend-api
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-07
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | vitest ^2.1.5 with @testing-library/react ^16.0.1 |
| **Config file** | `frontend/vitest.config.ts` |
| **Quick run command** | `cd frontend && npm test -- --run` |
| **Full suite command** | `cd frontend && npm test -- --run --coverage` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd frontend && npm test -- --run`
- **After every plan wave:** Run `cd frontend && npm test -- --run --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | Route-01 | unit | `npm test -- App.test.tsx` | ✅ | ⬜ pending |
| 06-01-02 | 01 | 1 | Route-02 | unit | `npm test -- App.test.tsx` | ✅ | ⬜ pending |
| 06-01-03 | 01 | 1 | Modal-01 | unit | `npm test -- RecipeDetailModal.test.tsx` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | Type-01 | compile | `npx tsc --noEmit` | ✅ | ⬜ pending |
| 06-02-02 | 02 | 1 | Hook-01 | unit | `npm test -- useShoppingList.test.tsx` | ❌ W0 | ⬜ pending |
| 06-02-03 | 02 | 1 | Hook-02 | unit | `npm test -- useSearch.test.tsx` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 2 | Screen-01 | unit | `npm test -- --run` | ✅ | ⬜ pending |
| 06-03-02 | 03 | 2 | Hook-03 | compile | `npx tsc --noEmit` | ✅ | ⬜ pending |
| 06-03-03 | 03 | 2 | Screen-02 | unit | `npm test -- --run` | ✅ | ⬜ pending |
| 06-03-04 | 03 | 2 | Screen-03 | unit | `npm test -- --run` | ✅ | ⬜ pending |
| 06-04-01 | 04 | 3 | Search-01 | compile | `npx tsc --noEmit` | ✅ | ⬜ pending |
| 06-04-02 | 04 | 3 | Route-03 | unit | `npm test -- --run` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/__tests__/hooks/useShoppingList.test.tsx` — stubs for Hook-01
- [ ] `frontend/src/__tests__/hooks/useSearch.test.tsx` — stubs for Hook-02
- [ ] `frontend/src/__tests__/components/RecipeDetailModal.test.tsx` — stubs for Modal-01
- [ ] `npm install sonner` — missing dependency

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Modal URL shareability | Route-02 | Browser URL bar state | Copy URL with ?recipe=X, paste in new tab, verify modal opens |
| Hardware back button closes modal | Route-02 | Mobile-specific | On mobile device, open modal, press back, verify modal closes |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
