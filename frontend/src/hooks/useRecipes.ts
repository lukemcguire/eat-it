import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type {
  Recipe,
  RecipeCreate,
  RecipeUpdate,
  RecipeRatingUpdate,
  RecipeNotesUpdate,
  ParseResponse,
} from '@/types/recipe';

// List recipes with pagination and search
export function useRecipes(params?: {
  offset?: number;
  limit?: number;
  q?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params?.offset) searchParams.set('offset', String(params.offset));
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.q) searchParams.set('q', params.q);

  const query = searchParams.toString();
  return useQuery({
    queryKey: ['recipes', params],
    queryFn: () => apiClient<Recipe[]>(`/recipes${query ? `?${query}` : ''}`),
  });
}

// Get single recipe
export function useRecipe(id: number) {
  return useQuery({
    queryKey: ['recipes', id],
    queryFn: () => apiClient<Recipe>(`/recipes/${id}`),
    enabled: !!id,
  });
}

// Create recipe
export function useCreateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recipe: RecipeCreate) =>
      apiClient<Recipe>('/recipes/', {
        method: 'POST',
        body: JSON.stringify(recipe),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
    },
  });
}

// Update recipe
export function useUpdateRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, recipe }: { id: number; recipe: RecipeUpdate }) =>
      apiClient<Recipe>(`/recipes/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(recipe),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      queryClient.invalidateQueries({ queryKey: ['recipes', id] });
    },
  });
}

// Delete recipe
export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient<void>(`/recipes/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
    },
  });
}

// Parse recipe URL
export function useParseRecipe() {
  return useMutation({
    mutationFn: (url: string) =>
      apiClient<ParseResponse>(`/recipes/parse?url=${encodeURIComponent(url)}`),
  });
}

// Update rating
export function useUpdateRating() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, rating }: { id: number; rating: RecipeRatingUpdate }) =>
      apiClient<Recipe>(`/recipes/${id}/rating`, {
        method: 'PATCH',
        body: JSON.stringify(rating),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['recipes', id] });
    },
  });
}

// Update notes
export function useUpdateNotes() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: RecipeNotesUpdate }) =>
      apiClient<Recipe>(`/recipes/${id}/notes`, {
        method: 'PATCH',
        body: JSON.stringify(notes),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['recipes', id] });
    },
  });
}
