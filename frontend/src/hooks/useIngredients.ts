import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type {
  IngredientGroupWithIngredients,
  IngredientsBulkRequest,
  IngredientsBulkResponse,
} from '@/types/ingredient';

/**
 * Fetch ingredient groups with nested ingredients for a recipe.
 * Uses GET /recipes/{recipeId}/groups endpoint.
 */
export function useIngredientGroups(recipeId: number) {
  return useQuery({
    queryKey: ['recipes', recipeId, 'ingredient-groups'],
    queryFn: () =>
      apiClient<IngredientGroupWithIngredients[]>(
        `/recipes/${recipeId}/groups`
      ),
    enabled: !!recipeId,
  });
}

/**
 * Bulk replace all ingredient groups and ingredients for a recipe.
 * Uses PUT /recipes/{recipeId}/ingredients endpoint.
 *
 * Invalidates both ingredient-groups and recipe queries on success
 * to refresh any cached data.
 */
export function useBulkReplaceIngredients(recipeId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: IngredientsBulkRequest) =>
      apiClient<IngredientsBulkResponse>(
        `/recipes/${recipeId}/ingredients`,
        {
          method: 'PUT',
          body: JSON.stringify(payload),
        }
      ),
    onSuccess: () => {
      // Invalidate ingredient groups for this recipe
      queryClient.invalidateQueries({
        queryKey: ['recipes', recipeId, 'ingredient-groups'],
      });
      // Also invalidate the recipe itself in case it caches ingredients
      queryClient.invalidateQueries({
        queryKey: ['recipes', recipeId],
      });
    },
  });
}
