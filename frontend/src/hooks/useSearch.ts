import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { Recipe } from '@/types/recipe';

export function useSearch(query: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['search', query],
    queryFn: () =>
      apiClient<Recipe[]>(`/search?q=${encodeURIComponent(query)}`),
    enabled: enabled && query.trim().length > 0,
  });
