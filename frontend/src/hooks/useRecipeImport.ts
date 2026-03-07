import { useState } from 'react';
import { useParseRecipe, useCreateRecipe } from './useRecipes';
import type { ParseResponse, RecipeCreate } from '@/types/recipe';

export interface ParsedRecipe {
  title: string;
  description?: string;
  instructions: string;
  prep_time?: string;
  cook_time?: string;
  servings?: string;
  source_url: string;
  image_url?: string;
  ingredients?: string[];
  tags?: string[];
}

export interface UseRecipeImportReturn {
  readonly url: string;
  readonly setUrl: (url: string) => void;
  readonly parsedRecipe: ParsedRecipe | null;
  readonly parseError: string | null;
  readonly isParsing: boolean;
  readonly isSaving: boolean;
  readonly parseRecipe: () => Promise<void>;
  readonly saveRecipe: () => Promise<void>;
  readonly discardRecipe: () => void;
  readonly duplicateWarning: { existing_recipe: { id: number; title: string } } | null;
}

export function useRecipeImport(): UseRecipeImportReturn {
  const [url, setUrl] = useState('');
  const [parsedRecipe, setParsedRecipe] = useState<ParsedRecipe | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [duplicateWarning, setDuplicateWarning] = useState<{
    existing_recipe: { id: number; title: string };
  } | null>(null);

  const parseMutation = useParseRecipe();
  const createMutation = useCreateRecipe();

  const parseRecipe = async () => {
    setParseError(null);
    setParsedRecipe(null);
    setDuplicateWarning(null);

    try {
      const result: ParseResponse = await parseMutation.mutateAsync(url);

      if (result.success && result.data) {
        // Map parsed data to our format
        const data = result.data as Record<string, unknown>;
        setParsedRecipe({
          title: String(data.title || ''),
          description: data.description ? String(data.description) : undefined,
          instructions: String(data.instructions || ''),
          prep_time: data.prep_time ? String(data.prep_time) : undefined,
          cook_time: data.cook_time ? String(data.cook_time) : undefined,
          servings: data.servings ? String(data.servings) : undefined,
          source_url: url,
          image_url: data.image ? String(data.image) : undefined,
          ingredients: Array.isArray(data.ingredients)
            ? (data.ingredients as string[])
            : undefined,
          tags: Array.isArray(data.tags) ? (data.tags as string[]) : undefined,
        });

        // Check for duplicate warning
        if (result.duplicate_warning?.existing_recipe) {
          setDuplicateWarning({
            existing_recipe: {
              id: result.duplicate_warning.existing_recipe.id,
              title: result.duplicate_warning.existing_recipe.title,
            },
          });
        }
      } else if (result.error) {
        setParseError(result.error.message);
      }
    } catch {
      setParseError('Failed to parse recipe from URL');
    }
  };

  const saveRecipe = async () => {
    if (!parsedRecipe) return;

    const recipeCreate: RecipeCreate = {
      title: parsedRecipe.title,
      description: parsedRecipe.description,
      instructions: parsedRecipe.instructions,
      prep_time: parsedRecipe.prep_time,
      cook_time: parsedRecipe.cook_time,
      servings: parsedRecipe.servings,
      source_url: parsedRecipe.source_url,
      image_url: parsedRecipe.image_url,
      tags: parsedRecipe.tags,
    };

    await createMutation.mutateAsync(recipeCreate);
  };

  const discardRecipe = () => {
    setUrl('');
    setParsedRecipe(null);
    setParseError(null);
    setDuplicateWarning(null);
  };

  return {
    url,
    setUrl,
    parsedRecipe,
    parseError,
    isParsing: parseMutation.isPending,
    isSaving: createMutation.isPending,
    parseRecipe,
    saveRecipe,
    discardRecipe,
    duplicateWarning,
  } as const;
}
