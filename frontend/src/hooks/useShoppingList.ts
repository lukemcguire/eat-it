import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type {
  ShoppingList,
  ShoppingListsResponse,
  ShoppingListItem,
  ShoppingListItemCreate,
  ShoppingListItemUpdate,
  ShoppingListCreate,
  ShoppingListUpdate,
  ShoppingListGenerate,
  StoreSectionsResponse,
} from '@/types/shopping';

// List all shopping lists (without items for performance)
export function useShoppingLists() {
  return useQuery({
    queryKey: ['shopping-lists'],
    queryFn: () => apiClient<ShoppingListsResponse>('/shopping-lists/'),
  });
}

// Get single list with items
export function useShoppingList(id: number) {
  return useQuery({
    queryKey: ['shopping-list', id],
    queryFn: () => apiClient<ShoppingList>(`/shopping-lists/${id}`),
    enabled: !!id,
  });
}

// Get shared list via token
export function useSharedShoppingList(token: string) {
  return useQuery({
    queryKey: ['shared-shopping-list', token],
    queryFn: () => apiClient<ShoppingList>(`/shopping-lists/shared/${token}`),
    enabled: !!token,
  });
}

// Create a new shopping list
export function useCreateShoppingList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ShoppingListCreate) =>
      apiClient<ShoppingList>('/shopping-lists/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping-lists'] });
    },
  });
}

// Update shopping list name
export function useUpdateShoppingList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ShoppingListUpdate }) =>
      apiClient<ShoppingList>(`/shopping-lists/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-lists'] });
      queryClient.invalidateQueries({ queryKey: ['shopping-list', id] });
    },
  });
}

// Delete shopping list
export function useDeleteShoppingList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      apiClient<void>(`/shopping-lists/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping-lists'] });
    },
  });
}

// Generate shopping list from recipes
export function useGenerateShoppingList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ShoppingListGenerate) =>
      apiClient<ShoppingList>('/shopping-lists/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping-lists'] });
    },
  });
}

// Add item to list
export function useAddShoppingListItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      listId,
      data,
    }: {
      listId: number;
      data: ShoppingListItemCreate;
    }) =>
      apiClient<ShoppingListItem>(`/shopping-lists/${listId}/items`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, { listId }) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
    },
  });
}

// Update item (toggle checked, edit name/quantity)
export function useUpdateShoppingListItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      listId,
      itemId,
      data,
    }: {
      listId: number;
      itemId: number;
      data: ShoppingListItemUpdate;
    }) =>
      apiClient<ShoppingListItem>(
        `/shopping-lists/${listId}/items/${itemId}`,
        {
          method: 'PATCH',
          body: JSON.stringify(data),
        }
      ),
    onSuccess: (_, { listId }) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
    },
  });
}

// Delete item from list
export function useDeleteShoppingListItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      apiClient<void>(`/shopping-lists/${listId}/items/${itemId}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, { listId }) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
    },
  });
}

// Clear completed items
export function useClearCompletedItems() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (listId: number) =>
      apiClient<void>(`/shopping-lists/${listId}/completed`, {
        method: 'DELETE',
      }),
    onSuccess: (_, listId) => {
      queryClient.invalidateQueries({ queryKey: ['shopping-list', listId] });
    },
  });
}

// Generate share token
export function useShareShoppingList() {
  return useMutation({
    mutationFn: (listId: number) =>
      apiClient<{ share_token: string; expires_at: string; share_url: string }>(
        `/shopping-lists/${listId}/share`,
        { method: 'POST' }
      ),
  });
}

// List store sections
export function useStoreSections() {
  return useQuery({
    queryKey: ['store-sections'],
    queryFn: () => apiClient<StoreSectionsResponse>('/shopping-lists/sections'),
  });
}
