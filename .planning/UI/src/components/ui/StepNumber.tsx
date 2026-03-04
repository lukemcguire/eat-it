import React from 'react';

interface StepNumberProps {
  readonly number: number;
  readonly className?: string;
}

export const StepNumber: React.FC<StepNumberProps> = ({
  number,
  className = '',
}) => {
  return (
    <div
      className={`flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-primary text-white font-bold transition-all shadow-md shadow-primary/20 group-hover:scale-110 ${className}`}
    >
      {number}
    </div>
  );
};
