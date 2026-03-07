/**
 * Smoke tests for screen components.
 *
 * These tests ensure each screen component:
 * 1. Can be imported without TypeScript errors
 * 2. Renders without crashing
 *
 * This catches interface mismatches between components and hooks
 * that would otherwise only be caught at build time.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";

// Import all screens to catch type errors at test time
import {
  RecipeBinderScreen,
  RecipeDetailScreen,
  RecipeImportScreen,
  ShoppingListScreen,
} from "@/components/screens-shadcn";

// Mock hooks that screens depend on
vi.mock("@/hooks", () => ({
  useRecipeBinder: () => ({
    recipes: [],
    filteredRecipes: [],
    isLoading: false,
    error: null,
    searchQuery: "",
    setSearchQuery: vi.fn(),
    activeFilter: "All Recipes",
    setActiveFilter: vi.fn(),
    toggleFavorite: vi.fn(),
    filters: ["All Recipes", "Favorites", "Recent"],
  }),
  useRecipe: () => ({
    recipe: null,
    isLoading: false,
    error: null,
  }),
  useRecipeImport: () => ({
    url: "",
    setUrl: vi.fn(),
    parsedRecipe: null,
    parseError: null,
    isParsing: false,
    isSaving: false,
    parseRecipe: vi.fn(),
    saveRecipe: vi.fn(),
    discardRecipe: vi.fn(),
    duplicateWarning: null,
  }),
  // Shopping list hooks
  useShoppingList: () => ({
    data: { items: [] },
    isLoading: false,
    error: null,
  }),
  useUpdateShoppingListItem: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useStoreSections: () => ({
    data: { data: [] },
    isLoading: false,
  }),
}));

// Create wrapper with all required providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>{children}</MemoryRouter>
      </QueryClientProvider>
    );
  };
}

describe("Screen Components", () => {
  describe("RecipeBinderScreen", () => {
    it("renders without crashing", () => {
      render(<RecipeBinderScreen />, { wrapper: createWrapper() });
      expect(screen.getByText(/recipe binder/i)).toBeInTheDocument();
    });
  });

  describe("RecipeDetailScreen", () => {
    it("renders without crashing", () => {
      render(<RecipeDetailScreen />, { wrapper: createWrapper() });
      // RecipeDetailScreen shows loading or not found when no recipe
      expect(document.body).toBeInTheDocument();
    });
  });

  describe("RecipeImportScreen", () => {
    it("renders without crashing", () => {
      render(<RecipeImportScreen />, { wrapper: createWrapper() });
      expect(screen.getByText(/import new recipe/i)).toBeInTheDocument();
    });
  });

  describe("ShoppingListScreen", () => {
    it("renders without crashing", () => {
      render(<ShoppingListScreen />, { wrapper: createWrapper() });
      expect(screen.getByText(/shopping list/i)).toBeInTheDocument();
    });
  });
});
