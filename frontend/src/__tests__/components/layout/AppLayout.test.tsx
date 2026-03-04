import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';

const renderWithRouter = (children: React.ReactNode) => {
  return render(
    <MemoryRouter>
      <AppLayout>{children}</AppLayout>
    </MemoryRouter>
  );
};

describe('AppLayout', () => {
  it('renders children', () => {
    renderWithRouter(<div>Test Content</div>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders Header', () => {
    renderWithRouter(<div>Test</div>);
    // Header should be present (it renders the title)
    const header = document.querySelector('header');
    expect(header).toBeInTheDocument();
  });

  it('renders Sidebar', () => {
    renderWithRouter(<div>Test</div>);
    const aside = document.querySelector('aside');
    expect(aside).toBeInTheDocument();
  });

  it('renders BottomNav', () => {
    renderWithRouter(<div>Test</div>);
    const nav = document.querySelector('nav');
    expect(nav).toBeInTheDocument();
  });

  it('has correct main content area classes', () => {
    renderWithRouter(<div>Test</div>);
    const main = document.querySelector('main');
    expect(main?.className).toContain('p-4');
    expect(main?.className).toContain('lg:p-6');
  });

  it('has bottom padding for mobile nav', () => {
    const { container } = renderWithRouter(<div>Test</div>);
    const wrapper = container.querySelector('.pb-20');
    expect(wrapper).toBeInTheDocument();
  });

  it('has sidebar offset class for desktop', () => {
    const { container } = renderWithRouter(<div>Test</div>);
    const wrapper = container.querySelector('.lg\\:ml-64');
    expect(wrapper).toBeInTheDocument();
  });

  it('renders with custom title', () => {
    renderWithRouter(<div>Test</div>);
    // Title is rendered in the header (h1 element)
    const headerTitle = document.querySelector('header h1');
    expect(headerTitle).toHaveTextContent('Eat It');
  });
});
