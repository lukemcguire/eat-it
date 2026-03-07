---
status: investigating
trigger: "Docker build fails with TypeScript compilation errors"
created: 2026-03-05T00:00:00Z
updated: 2026-03-05T00:00:00Z
---

## Current Focus

hypothesis: "Multiple TypeScript configuration and export mismatches causing build failures"
test: "Analyze each error and identify root causes"
expecting: "Find specific fixes needed for each error type"
next_action: "Document root causes and required fixes"

## Symptoms

expected: Docker build should succeed with TypeScript compilation
actual: Docker build fails with 5 TypeScript errors
errors:
  - "src/components/ui/index.ts(3,10): error TS2305: Module '"./IconButton"' has no exported member 'IconButton'."
  - "src/components/recipe-binder/RecipeBinderScreen.tsx(4,10): error TS2305: Module '"../ui"' has no exported member 'Icon'."
  - "src/components/recipe-detail/RecipeDetailScreen.tsx(4,10): error TS2305: Module '"../ui"' has no exported member 'Icon'."
  - "src/components/recipe-import/RecipeImportScreen.tsx(3,10): error TS2305: Module '"../ui"' has no exported member 'Icon'."
  - "src/lib/api.ts(1,30): error TS2339: Property 'env' does not exist on type 'ImportMeta'."
reproduction: Run Docker build for frontend
started: Unknown - discovered during phase 05 deployment

## Eliminated

(none yet)

## Evidence

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/src/components/ui/index.ts
  found: "Exports `IconButton` from './IconButton' on line 3"
  implication: index.ts expects IconButton to be exported from IconButton.tsx

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/src/components/ui/IconButton.tsx
  found: "Only exports `Icon` component (line 9), NOT `IconButton`"
  implication: MISMATCH - index.ts exports IconButton but file only exports Icon

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/src/components/recipe-binder/RecipeBinderScreen.tsx
  found: "Imports `Icon` from '../ui' (line 4)"
  implication: Consumers expect `Icon` to be re-exported from index.ts

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/src/vite-env.d.ts
  found: "FILE DOES NOT EXIST"
  implication: No Vite type declarations, causing import.meta.env error

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/tsconfig.json
  found: "Does not include vite-env.d.ts in include array, only includes 'src'"
  implication: Even if vite-env.d.ts existed, it might not be included

- timestamp: 2026-03-05T00:00:00Z
  checked: frontend/src/lib/api.ts
  found: "Uses `import.meta.env.VITE_API_BASE` on line 1"
  implication: Requires Vite client types for ImportMeta.env

## Resolution

root_cause: |
  THREE DISTINCT ISSUES:

  1. **Export Mismatch in IconButton.tsx**: The file exports `Icon` but index.ts
     tries to re-export `IconButton`. The file is named IconButton.tsx but only
     contains an Icon component.

  2. **Missing Icon export from index.ts**: Components import `Icon` from '../ui'
     but index.ts doesn't export Icon - it only exports IconButton (which doesn't
     exist in the file).

  3. **Missing vite-env.d.ts**: No Vite type declarations file exists, causing
     TypeScript to not recognize `import.meta.env`. This file should declare
     Vite client types for access to environment variables.

fix: |
  1. In frontend/src/components/ui/index.ts:
     - Change `export { IconButton } from './IconButton';` to `export { Icon } from './IconButton';`
     OR rename the file to Icon.tsx

  2. Create frontend/src/vite-env.d.ts with:
     ```typescript
     /// <reference types="vite/client" />
     ```

  3. Optionally update tsconfig.json to explicitly include vite-env.d.ts

verification: Run `npm run build` or `tsc --noEmit` in frontend directory
files_changed: []
