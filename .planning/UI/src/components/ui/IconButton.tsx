import React from 'react';

interface IconProps {
  readonly name: string;
  readonly className?: string;
  readonly filled?: boolean;
}

export const Icon: React.FC<IconProps> = ({
  name,
  className = '',
  filled = false,
}) => {
  const style = filled
    ? { fontVariationSettings: "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24" }
    : {};

  return (
    <span
      className={`material-symbols-outlined ${className}`}
      style={style}
      aria-hidden="true"
    >
      {name}
    </span>
  );
};
