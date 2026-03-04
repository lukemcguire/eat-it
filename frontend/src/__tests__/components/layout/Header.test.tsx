import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Header } from '@/components/layout/Header';

describe('Header', () => {
  it('renders with title', () => {
    render(<Header title="Test Title" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders menu button when onMenuClick provided', () => {
    const onMenuClick = vi.fn();
    render(<Header title="Test" onMenuClick={onMenuClick} />);
    expect(screen.getByRole('button', { name: /open menu/i })).toBeInTheDocument();
  });

  it('does not render menu button when onMenuClick not provided', () => {
    render(<Header title="Test" />);
    expect(screen.queryByRole('button', { name: /open menu/i })).not.toBeInTheDocument();
  });

  it('calls onMenuClick when menu button clicked', async () => {
    const user = userEvent.setup();
    const onMenuClick = vi.fn();
    render(<Header title="Test" onMenuClick={onMenuClick} />);

    await user.click(screen.getByRole('button', { name: /open menu/i }));
    expect(onMenuClick).toHaveBeenCalled();
  });

  it('renders actions', () => {
    render(
      <Header
        title="Test"
        actions={<button>Action Button</button>}
      />
    );
    expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument();
  });

  it('has correct height class', () => {
    const { container } = render(<Header title="Test" />);
    const header = container.querySelector('header');
    expect(header?.className).toContain('h-16');
  });
});
