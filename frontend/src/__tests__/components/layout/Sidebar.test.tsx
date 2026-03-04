import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';

const renderWithRouter = (initialRoute: string = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Sidebar />
    </MemoryRouter>
  );
};

describe('Sidebar', () => {
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
    });
  });

  it('has lg:flex class for desktop visibility', () => {
    const { container } = renderWithRouter();
    const aside = container.querySelector('aside');
    expect(aside?.className).toContain('lg:flex');
  });

  it('has hidden class for mobile', () => {
    const { container } = renderWithRouter();
    const aside = container.querySelector('aside');
    expect(aside?.className).toContain('hidden');
  });

  it('renders brand "Eat It"', () => {
    renderWithRouter();
    expect(screen.getByText('Eat It')).toBeInTheDocument();
  });

  it('links navigate to correct paths', () => {
    renderWithRouter();
    expect(screen.getByText('Recipe Binder').closest('a')).toHaveAttribute('href', '/');
    expect(screen.getByText('Shopping List').closest('a')).toHaveAttribute('href', '/shopping');
    expect(screen.getByText('Search').closest('a')).toHaveAttribute('href', '/search');
    expect(screen.getByText('Add/Import').closest('a')).toHaveAttribute('href', '/import');
  });

  it('active nav item has active styling', () => {
    renderWithRouter('/');
    const recipeBinderLink = screen.getByText('Recipe Binder').closest('a');
    expect(recipeBinderLink?.className).toContain('bg-[#207fdf]/20');
  });
});
