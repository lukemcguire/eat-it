import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TouchButton } from '@/components/ui/TouchButton';

describe('TouchButton', () => {
  it('renders with 44px minimum height', () => {
    render(<TouchButton>Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('min-h-[44px]');
  });

  it('renders with 44px minimum width', () => {
    render(<TouchButton>Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('min-w-[44px]');
  });

  it('applies primary variant styles by default', () => {
    render(<TouchButton>Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-[#207fdf]');
  });

  it('applies secondary variant styles', () => {
    render(<TouchButton variant="secondary">Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-[#1a2632]');
  });

  it('applies ghost variant styles', () => {
    render(<TouchButton variant="ghost">Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-transparent');
  });

  it('applies icon size styles', () => {
    render(<TouchButton size="icon">X</TouchButton>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('p-2');
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    let clicked = false;
    render(<TouchButton onClick={() => { clicked = true; }}>Click me</TouchButton>);

    await user.click(screen.getByRole('button'));
    expect(clicked).toBe(true);
  });

  it('can be disabled', () => {
    render(<TouchButton disabled>Click me</TouchButton>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
