import { useState, useCallback, useMemo } from 'react';
import {
  recipeCards,
  categoryFilters,
  type RecipeCard,
} from '../data/mockData';

export interface UseRecipeBinderReturn {
  readonly recipes: readonly RecipeCard[];
  readonly filteredRecipes: readonly RecipeCard[];
  readonly activeFilter: string;
  readonly setActiveFilter: (filter: string) => void;
  readonly searchQuery: string;
  readonly setSearchQuery: (query: string) => void;
  readonly toggleFavorite: (id: string) => void;
  readonly filters: typeof categoryFilters;
}

export function useRecipeBinder(): UseRecipeBinderReturn {
  const [recipes, setRecipes] = useState<readonly RecipeCard[]>(recipeCards);
  const [activeFilter, setActiveFilter] = useState('All Recipes');
  const [searchQuery, setSearchQuery] = useState('');

  const toggleFavorite = useCallback((id: string) => {
    setRecipes((prev) =>
      prev.map((recipe) =>
        recipe.id === id
          ? { ...recipe, isFavorite: !recipe.isFavorite }
          : recipe
      )
    );
  }, []);

  const filteredRecipes = useMemo(() => {
    let result = recipes;
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter((recipe) =>
        recipe.title.toLowerCase().includes(query)
      );
    }
    return result;
  }, [recipes, searchQuery]);

  return {
    recipes,
    filteredRecipes,
    activeFilter,
    setActiveFilter,
    searchQuery,
    setSearchQuery,
    toggleFavorite,
    filters: categoryFilters,
  } as const;
}
