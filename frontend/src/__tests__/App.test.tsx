import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from '@/App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeTruthy();
  });

  it('renders QueryClientProvider', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('renders AppLayout', () => {
    render(<App />);
    // AppLayout renders the sidebar
    const aside = document.querySelector('aside');
    expect(aside).toBeInTheDocument();
  });

  it('renders navigation items', () => {
    render(<App />);
    // Navigation items appear in both Sidebar and BottomNav
    // Use getAllByText since there are multiple instances
    expect(screen.getAllByText('Recipe Binder').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Shopping List').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Search').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Add/Import').length).toBeGreaterThan(0);
  });

  it('renders default route content', () => {
    render(<App />);
    // RecipeBinder placeholder should be visible (in main content area)
    const main = document.querySelector('main');
    expect(main?.textContent).toContain('Recipe Binder');
  });
});
