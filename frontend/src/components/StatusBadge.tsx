import React from 'react';
import { TaskStatus } from '../types';

interface StatusBadgeProps {
  status: TaskStatus;
  onClick?: () => void;
  clickable?: boolean;
}

const statusConfig: Record<
  TaskStatus,
  { label: string; bg: string; text: string; border: string; dot: string }
> = {
  todo: {
    label: 'To Do',
    bg: 'bg-gray-100 dark:bg-gray-800',
    text: 'text-gray-700 dark:text-gray-300',
    border: 'border-gray-300 dark:border-gray-700',
    dot: 'bg-gray-400 dark:bg-gray-500',
  },
  in_progress: {
    label: 'In Progress',
    bg: 'bg-blue-50 dark:bg-blue-950/60',
    text: 'text-blue-700 dark:text-blue-300',
    border: 'border-blue-200 dark:border-blue-800',
    dot: 'bg-blue-500',
  },
  done: {
    label: 'Done',
    bg: 'bg-green-50 dark:bg-green-950/60',
    text: 'text-green-700 dark:text-green-300',
    border: 'border-green-200 dark:border-green-800',
    dot: 'bg-green-500',
  },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  onClick,
  clickable = false,
}) => {
  const config = statusConfig[status];

  const content = (
    <>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      <span>{config.label}</span>
      {clickable && (
        <span className="text-[10px] opacity-60 ml-0.5" title="Click to cycle status">
          ↺
        </span>
      )}
    </>
  );

  const baseClasses = `inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors ${config.bg} ${config.text} ${config.border}`;

  if (clickable && onClick) {
    return (
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        title="Click to advance status"
        aria-label={`Current status: ${config.label}. Click to cycle to next status`}
        className={`${baseClasses} hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500 cursor-pointer`}
      >
        {content}
      </button>
    );
  }

  return <span className={baseClasses}>{content}</span>;
};
