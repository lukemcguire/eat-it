import React from 'react';

interface CardProps {
  readonly children: React.ReactNode;
  readonly className?: string;
  readonly hover?: boolean;
  readonly onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  onClick,
}) => {
  const hoverStyles = hover
    ? 'hover:shadow-xl hover:border-primary/50 transition-all cursor-pointer'
    : '';

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-border-dark ${hoverStyles} ${className}`}
    >
      {children}
    </div>
  );
};
