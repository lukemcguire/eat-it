import React from 'react';

interface TagProps {
  readonly children: React.ReactNode;
  readonly variant?: 'primary' | 'muted' | 'outline';
  readonly className?: string;
}

export const Tag: React.FC<TagProps> = ({
  children,
  variant = 'primary',
  className = '',
}) => {
  const variantStyles = {
    primary: 'bg-primary text-white',
    muted: 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
    outline: 'bg-primary/10 text-primary',
  };

  return (
    <span
      className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-widest ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
