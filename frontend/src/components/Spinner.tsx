import React from 'react';
import { Loader2 } from 'lucide-react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  label,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-10 h-10',
  };

  return (
    <div
      role="status"
      aria-label={label || 'Loading'}
      className={`flex items-center justify-center gap-2 ${className}`}
    >
      <Loader2 className={`animate-spin text-blue-600 dark:text-blue-400 ${sizeClasses[size]}`} />
      {label && <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>}
      <span className="sr-only">{label || 'Loading...'}</span>
    </div>
  );
};
