import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { IngredientSection } from '@/components/ingredients/IngredientSection';

// Mock the API hooks
vi.mock('@/hooks/useIngredients', () => ({
  useIngredientGroups: () => ({
    data: [
      {
        id: 1,
        recipe_id: 1,
        name: 'Main',
        ingredients: [
          {
            id: 1,
            group_id: 1,
            quantity: 1,
            unit: 'C',
            name: 'Flour',
            preparation: null,
            raw: '1 C. flour',
            display_order: 0,
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
          },
        ],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    isLoading: false,
  }),
  useBulkReplaceIngredients: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

let queryClient: QueryClient;

const wrapper = ({ children }: { children: React.ReactNode }) => {
  queryClient = createTestQueryClient();
  const router = createMemoryRouter([
    {
      path: '/',
      element: (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      ),
    },
  ]);
  return <RouterProvider router={router} />;
};

describe('IngredientSection', () => {
  it('renders ingredient list in view mode', () => {
    render(<IngredientSection recipeId={1} />, { wrapper });
    expect(screen.getByText('Ingredients')).toBeInTheDocument();
    expect(screen.getByText(/Flour/)).toBeInTheDocument();
  });

  it('shows Edit button on desktop', () => {
    render(<IngredientSection recipeId={1} />, { wrapper });
    expect(screen.getByRole('button', { name: /edit/i })).toBeInTheDocument();
  });

  it('enters edit mode when Edit is clicked', async () => {
    const user = userEvent.setup();
    render(<IngredientSection recipeId={1} />, { wrapper });
    await user.click(screen.getByRole('button', { name: /edit/i }));
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  it('shows single group as flat list without header', () => {
    render(<IngredientSection recipeId={1} />, { wrapper });
    // Should NOT show group name "Main" when only one group
    expect(screen.queryByText('Main')).not.toBeInTheDocument();
  });
});
