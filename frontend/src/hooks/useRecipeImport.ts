import { useState, useCallback } from 'react';
import {
  importedRecipe,
  type ImportedRecipe,
  type ImportIngredient,
} from '../data/mockData';

export interface UseRecipeImportReturn {
  readonly url: string;
  readonly setUrl: (url: string) => void;
  readonly recipe: ImportedRecipe | null;
  readonly isLoaded: boolean;
  readonly fetchRecipe: () => void;
  readonly addIngredient: (name: string, quantity: string) => void;
  readonly saveRecipe: () => void;
  readonly discardRecipe: () => void;
}

export function useRecipeImport(): UseRecipeImportReturn {
  const [url, setUrl] = useState('');
  const [recipe, setRecipe] = useState<ImportedRecipe | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  const fetchRecipe = useCallback(() => {
    // Simulate fetching - in production this would call an API
    if (url.trim()) {
      setRecipe(importedRecipe);
      setIsLoaded(true);
    }
  }, [url]);

  const addIngredient = useCallback((name: string, quantity: string) => {
    setRecipe((prev) =>
      prev
        ? {
            ...prev,
            ingredients: [
              ...prev.ingredients,
              { name, quantity } as ImportIngredient,
            ],
          }
        : null
    );
  }, []);

  const saveRecipe = useCallback(() => {
    // In production, this would persist to a database
    console.log('Saving recipe:', recipe);
    setUrl('');
    setRecipe(null);
    setIsLoaded(false);
  }, [recipe]);

  const discardRecipe = useCallback(() => {
    setUrl('');
    setRecipe(null);
    setIsLoaded(false);
  }, []);

  return {
    url,
    setUrl,
    recipe,
    isLoaded,
    fetchRecipe,
    addIngredient,
    saveRecipe,
    discardRecipe,
  } as const;
}
