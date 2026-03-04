import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface TouchButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

const variantStyles = {
  primary: 'bg-[#207fdf] text-white hover:bg-[#1a6bc7] shadow-lg shadow-[#207fdf]/30',
  secondary: 'bg-[#1a2632] text-[#f1f5f9] border border-[#2e4e6b] hover:bg-[#243342]',
  ghost: 'bg-transparent text-[#f1f5f9] hover:bg-[#1a2632]',
  danger: 'bg-[#ef4444] text-white hover:bg-[#dc2626]',
};

const sizeStyles = {
  default: 'min-h-[44px] min-w-[44px] px-4 py-3',
  sm: 'min-h-[36px] min-w-[36px] px-3 py-2 text-sm',
  lg: 'min-h-[52px] min-w-[52px] px-6 py-4 text-lg',
  icon: 'min-h-[44px] min-w-[44px] p-2',
};

export const TouchButton = forwardRef<HTMLButtonElement, TouchButtonProps>(
  ({ className, variant = 'primary', size = 'default', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-xl font-semibold',
          'transition-transform duration-200',
          'hover:scale-[1.02] active:scale-[0.98]',
          'focus:outline-none focus:ring-2 focus:ring-[#207fdf]/50',
          'disabled:opacity-50 disabled:pointer-events-none',
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      />
    );
  }
);

TouchButton.displayName = 'TouchButton';
