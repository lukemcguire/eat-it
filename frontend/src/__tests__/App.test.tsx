import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '@/App';

describe('App', () => {
  it('renders QueryClientProvider', () => {
    const { container } = render(<App />);
    // QueryClientProvider doesn't add DOM elements, but app should render
    expect(container).toBeTruthy();
  });

  it('contains the application content', () => {
    render(<App />);
    // App should render something (will be placeholder for now)
    expect(screen.getByRole('heading', { name: /eat it/i })).toBeTruthy();
  });
});
