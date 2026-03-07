import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { BottomNav } from '@/components/layout/BottomNav';

const renderWithRouter = (initialRoute: string = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <BottomNav />
    </MemoryRouter>
  );
};

describe('BottomNav', () => {
  it('renders 4 navigation items', () => {
    renderWithRouter();
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(4);
  });

  it('has correct nav labels', () => {
    renderWithRouter();
    expect(screen.getByText('Recipe Binder')).toBeInTheDocument();
    expect(screen.getByText('Shopping List')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Add/Import')).toBeInTheDocument();
  });

  it('each nav item has 44px minimum tap target', () => {
    renderWithRouter();
    const links = screen.getAllByRole('link');
    links.forEach((link) => {
      expect(link.className).toContain('min-h-[44px]');
      expect(link.className).toContain('min-w-[44px]');
    });
  });

  it('active nav item has active styling', () => {
    renderWithRouter('/recipes');
    const recipeBinderLink = screen.getByText('Recipe Binder').closest('a');
    expect(recipeBinderLink?.className).toContain('text-[#207fdf]');
  });

  it('inactive nav items have muted styling', () => {
    renderWithRouter('/recipes');
    const shoppingLink = screen.getByText('Shopping List').closest('a');
    expect(shoppingLink?.className).toContain('text-[#94a3b8]');
  });

  it('has lg:hidden class for desktop hiding', () => {
    const { container } = renderWithRouter();
    const nav = container.querySelector('nav');
    expect(nav?.className).toContain('lg:hidden');
  });

  it('links navigate to correct paths', () => {
    renderWithRouter();
    expect(screen.getByText('Recipe Binder').closest('a')).toHaveAttribute('href', '/recipes');
    expect(screen.getByText('Shopping List').closest('a')).toHaveAttribute('href', '/shopping');
    expect(screen.getByText('Search').closest('a')).toHaveAttribute('href', '/search');
    expect(screen.getByText('Add/Import').closest('a')).toHaveAttribute('href', '/import');
  });
});
