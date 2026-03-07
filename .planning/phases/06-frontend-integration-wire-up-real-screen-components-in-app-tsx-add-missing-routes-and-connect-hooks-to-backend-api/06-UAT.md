---
status: testing
phase: 06-frontend-integration
source: [06-01-SUMMARY.md, 06-02-SUMMARY.md, 06-03-SUMMARY.md, 06-04-SUMMARY.md]
started: 2026-03-07T16:30:00Z
updated: 2026-03-07T16:30:00Z
---

## Current Test

number: 1
name: Cold Start Smoke Test
expected: |
  Kill any running frontend dev server. Start the frontend from scratch (npm run dev or similar). The app boots without errors in the console, the page loads at /recipes (redirected from /), and the recipe binder UI is visible with no crash.
awaiting: user response

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running frontend dev server. Start the frontend from scratch (npm run dev or similar). The app boots without errors in the console, the page loads at /recipes (redirected from /), and the recipe binder UI is visible with no crash.
result: [pending]

### 2. Home Redirects to Recipes
expected: Navigate to the root URL (/). The browser should automatically redirect to /recipes and the RecipeBinderScreen should be displayed with the recipe grid.
result: [pending]

### 3. Bottom Navigation Links
expected: The bottom navigation bar shows 4 items: Recipes, Shopping, Search, Import. Tapping each navigates to /recipes, /shopping, /search, and /import respectively. Active tab is highlighted.
result: [pending]

### 4. Recipe Detail Modal Opens from URL
expected: Navigate to /recipes?recipe=1 (or any valid recipe ID). A modal overlay appears showing the recipe details. The URL shows the query parameter for shareability.
result: [pending]

### 5. Recipe Detail Modal Closes on Backdrop Click
expected: With the recipe detail modal open, click on the dark backdrop area (outside the modal content). The modal closes and the URL returns to /recipes without the query param.
result: [pending]

### 6. Recipe Binder Loads from API
expected: On the /recipes page, recipes are fetched from the backend API (not mock data). Loading state shows while fetching, then recipe cards appear. If no recipes exist, an empty state is shown.
result: [pending]

### 7. Recipe Import from URL
expected: Navigate to /import. Paste a valid recipe URL into the input field and submit. A loading indicator appears, then recipe preview shows with title and ingredients. Saving the recipe shows a success toast and navigates to /recipes.
result: [pending]

### 8. Search Page with Manual Trigger
expected: Navigate to /search. The page shows recent recipes before any search. Type a search term and either press Enter or click the search button. Results load and display as a recipe card grid. If no results, a friendly message appears.
result: [pending]

### 9. Shopping List from Route Params
expected: Navigate to /shopping/1 (or any valid list ID). The shopping list for that ID loads from the API. If the list doesn't exist or API errors, a toast notification shows the error.
result: [pending]

### 10. Toast Notifications Appear
expected: Trigger an action that causes an error (e.g., import an invalid URL). A toast notification appears at the top or bottom of the screen with the error message. Toast auto-dismisses after a few seconds or can be dismissed manually.
result: [pending]

## Summary

total: 10
passed: 0
issues: 0
pending: 10
skipped: 0

## Gaps

[none yet]
