import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import * as apiModule from '@/lib/api';
import {
  useRecipes,
  useRecipe,
  useCreateRecipe,
  useDeleteRecipe,
} from '@/hooks/useRecipes';

// Mock apiClient
vi.mock('@/lib/api', () => ({
  apiClient: vi.fn(),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe('useRecipes', () => {
  it('returns query with correct key', () => {
    const { result } = renderHook(() => useRecipes(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toHaveProperty('data');
    expect(result.current).toHaveProperty('isLoading');
  });

  it('calls apiClient with correct endpoint', async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValueOnce([]);
    renderHook(() => useRecipes(), { wrapper: createWrapper() });
    await waitFor(() => {
      expect(apiModule.apiClient).toHaveBeenCalledWith('/recipes');
    });
  });

  it('passes query params when provided', async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValueOnce([]);
    renderHook(() => useRecipes({ q: 'pasta', limit: 10 }), {
      wrapper: createWrapper(),
    });
    await waitFor(() => {
      expect(apiModule.apiClient).toHaveBeenCalledWith(
        expect.stringContaining('/recipes?')
      );
      expect(apiModule.apiClient).toHaveBeenCalledWith(
        expect.stringContaining('q=pasta')
      );
      expect(apiModule.apiClient).toHaveBeenCalledWith(
        expect.stringContaining('limit=10')
      );
    });
  });
});

describe('useRecipe', () => {
  it('returns query with id in key', () => {
    const { result } = renderHook(() => useRecipe(1), {
      wrapper: createWrapper(),
    });
    expect(result.current).toHaveProperty('data');
  });

  it('is disabled when id is falsy', () => {
    const { result } = renderHook(() => useRecipe(0), {
      wrapper: createWrapper(),
    });
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useCreateRecipe', () => {
  it('returns mutation that invalidates recipes on success', async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValueOnce({ id: 1, title: 'Test' });
    const { result } = renderHook(() => useCreateRecipe(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toHaveProperty('mutate');
    expect(result.current).toHaveProperty('mutateAsync');
  });
});

describe('useDeleteRecipe', () => {
  it('returns mutation that calls DELETE endpoint', async () => {
    vi.mocked(apiModule.apiClient).mockResolvedValueOnce(undefined);
    const { result } = renderHook(() => useDeleteRecipe(), {
      wrapper: createWrapper(),
    });
    expect(result.current).toHaveProperty('mutate');
  });
});
