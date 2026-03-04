import React from 'react';

interface ButtonProps {
  readonly children?: React.ReactNode;
  readonly variant?: 'primary' | 'secondary' | 'ghost';
  readonly size?: 'default' | 'large';
  readonly icon?: string;
  readonly iconFilled?: boolean;
  readonly className?: string;
  readonly onClick?: () => void;
  readonly type?: 'button' | 'submit';
  readonly disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'default',
  icon,
  iconFilled = false,
  className = '',
  onClick,
  type = 'button',
  disabled = false,
}) => {
  const baseStyles =
    'flex items-center justify-center gap-2 font-bold transition-all';

  const variantStyles = {
    primary:
      'bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/30 active:scale-[0.98]',
    secondary:
      'bg-surface-dark border border-border-dark text-slate-200 hover:bg-slate-700',
    ghost:
      'bg-slate-100 dark:bg-surface-dark hover:bg-slate-200 dark:hover:bg-slate-700',
  };

  const sizeStyles = {
    default: 'px-6 py-3 rounded-xl',
    large: 'px-8 py-4 rounded-xl',
  };

  const iconStyle = iconFilled
    ? { fontVariationSettings: "'FILL' 1" }
    : {};

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {icon && (
        <span className="material-symbols-outlined" style={iconStyle}>
          {icon}
        </span>
      )}
      {children}
    </button>
  );
};
