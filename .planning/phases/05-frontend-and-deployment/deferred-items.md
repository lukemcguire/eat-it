# Deferred Items - Phase 05-frontend-and-deployment

## 2026-03-06: Additional TypeScript Unused Variable Errors

During 05-05 Docker build verification, additional unused variable errors were
discovered in files NOT covered by the plan. These are pre-existing issues.

### Files with unused imports/variables:

1. `src/__tests__/components/ingredients/IngredientSection.test.tsx`
   - Line 1: `beforeEach` is declared but never read

2. `src/components/screens-shadcn/RecipeBinderScreen.tsx`
   - Line 4: `Badge` is declared but never read

3. `src/components/screens-shadcn/RecipeImportScreen.tsx`
   - Line 6: `CardContent` is declared but never read
   - Line 9: `Separator` is declared but never read

4. `src/components/screens-shadcn/ShoppingListScreen.tsx`
   - Line 4: `Card` is declared but never read
   - Line 4: `TabsContent` is declared but never read

5. `src/components/shopping/ShoppingListScreen.tsx`
   - Line 48: `id` is declared but never read

6. `src/hooks/useShoppingList.ts`
   - Line 5: `ShoppingItem` is declared but never read

### Recommendation

Create a follow-up plan to clean up unused imports/variables in the
screens-shadcn components and related files.
