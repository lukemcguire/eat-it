import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';

const renderWithRouter = (initialRoute: string = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<div>Test Content</div>} />
          <Route path="/other" element={<div>Other Content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
};

describe('AppLayout', () => {
  it('renders children via Outlet', () => {
    renderWithRouter();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders Header', () => {
    renderWithRouter();
    // Header should be present (it renders the title)
    const header = document.querySelector('header');
    expect(header).toBeInTheDocument();
  });

  it('renders Sidebar', () => {
    renderWithRouter();
    const aside = document.querySelector('aside');
    expect(aside).toBeInTheDocument();
  });

  it('renders BottomNav', () => {
    renderWithRouter();
    const nav = document.querySelector('nav');
    expect(nav).toBeInTheDocument();
  });

  it('has correct main content area classes', () => {
    renderWithRouter();
    const main = document.querySelector('main');
    expect(main?.className).toContain('p-4');
    expect(main?.className).toContain('lg:p-6');
  });

  it('has bottom padding for mobile nav', () => {
    const { container } = renderWithRouter();
    const wrapper = container.querySelector('.pb-20');
    expect(wrapper).toBeInTheDocument();
  });

  it('has sidebar offset class for desktop', () => {
    const { container } = renderWithRouter();
    const wrapper = container.querySelector('.lg\\:ml-64');
    expect(wrapper).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    renderWithRouter();
    // Title is rendered in the header (h1 element)
    const headerTitle = document.querySelector('header h1');
    expect(headerTitle).toHaveTextContent('Eat It');
  });
});
