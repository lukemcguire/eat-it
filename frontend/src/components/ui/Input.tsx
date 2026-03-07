import React from 'react';

interface InputProps {
  readonly value: string;
  readonly onChange: (value: string) => void;
  readonly placeholder?: string;
  readonly icon?: string;
  readonly type?: 'text' | 'url';
  readonly className?: string;
  readonly disabled?: boolean;
}

export const Input: React.FC<InputProps> = ({
  value,
  onChange,
  placeholder,
  icon,
  type = 'text',
  className = '',
  disabled = false,
}) => {
  return (
    <div className={`relative ${className}`}>
      {icon && (
        <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
          {icon}
        </span>
      )}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full ${icon ? 'pl-12' : 'pl-4'} pr-4 py-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-charcoal-900/60 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed`}
      />
    </div>
  );
};
