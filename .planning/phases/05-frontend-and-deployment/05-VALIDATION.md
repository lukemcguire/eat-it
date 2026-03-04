---
phase: 5
slug: frontend-and-deployment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest (frontend) + pytest (backend) |
| **Config file** | `vitest.config.ts`, `pyproject.toml` |
| **Quick run command** | `pnpm test --run` (frontend), `pytest -x -q` (backend) |
| **Full suite command** | `pnpm test --run && pytest` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pnpm test --run` or `pytest -x -q` (context-appropriate)
- **After every plan wave:** Run `pnpm test --run && pytest`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | DATA-02 | unit | `pytest -x -q` | ✅ existing | ⬜ pending |
| 5-01-02 | 01 | 1 | DATA-02 | unit | `pytest -x -q` | ✅ existing | ⬜ pending |
| 5-02-01 | 02 | 1 | DATA-02 | unit | `pnpm test --run` | ❌ W0 | ⬜ pending |
| 5-02-02 | 02 | 1 | DATA-02 | unit | `pnpm test --run` | ❌ W0 | ⬜ pending |
| 5-03-01 | 03 | 2 | DATA-02 | e2e | `pytest tests/e2e/` | ❌ W0 | ⬜ pending |
| 5-03-02 | 03 | 2 | DATA-02 | e2e | `pytest tests/e2e/` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `frontend/src/__tests__/setup.ts` — Vitest setup with @testing-library/react
- [ ] `frontend/vitest.config.ts` — Configure jsdom environment
- [ ] `tests/e2e/test_docker_deployment.py` — E2E Docker deployment tests
- [ ] `@testing-library/react` and `@testing-library/user-event` installed

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 44px tap targets | DATA-02 | Requires visual inspection on mobile device | Open app on mobile, verify all buttons/links have sufficient tap area |
| Responsive layout | DATA-02 | Visual verification across breakpoints | Resize browser 320px-1920px, verify layout adapts correctly |
| Docker single-container deploy | DATA-02 | Infrastructure test | `docker run -p 8000:8000 -v eatit-data:/app/data eat-it` and verify app loads |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
