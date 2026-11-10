import React from 'react';
import { Calendar, Edit3, Trash2 } from 'lucide-react';
import { getNextStatus, useUpdateTask } from '../hooks/useTasks';
import { Task } from '../types';
import { PriorityBadge } from './PriorityBadge';
import { StatusBadge } from './StatusBadge';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onEdit, onDelete }) => {
  const updateTaskMutation = useUpdateTask();

  const handleStatusCycle = () => {
    const nextStatus = getNextStatus(task.status);
    updateTaskMutation.mutate({
      id: task.id,
      data: { status: nextStatus },
    });
  };

  // Due date calculation
  const formattedDueDate = task.due_date
    ? new Date(task.due_date).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : null;

  const isOverdue =
    task.due_date &&
    task.status !== 'done' &&
    new Date(task.due_date).getTime() < Date.now();

  return (
    <div className="group relative flex flex-col justify-between rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/80 p-5 shadow-sm hover:shadow-md transition-all hover:border-blue-300 dark:hover:border-blue-700">
      <div>
        {/* Top Badges & Actions */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge
              status={task.status}
              clickable={true}
              onClick={handleStatusCycle}
            />
            <PriorityBadge priority={task.priority} />
          </div>

          <div className="flex items-center gap-1 opacity-90 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
            <button
              type="button"
              onClick={() => onEdit(task)}
              title="Edit task"
              aria-label={`Edit task "${task.title}"`}
              className="p-1.5 rounded-lg text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => onDelete(task)}
              title="Delete task"
              aria-label={`Delete task "${task.title}"`}
              className="p-1.5 rounded-lg text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Title */}
        <h3
          className={`text-base font-semibold text-gray-900 dark:text-gray-100 break-words ${
            task.status === 'done' ? 'line-through text-gray-400 dark:text-gray-500' : ''
          }`}
        >
          {task.title}
        </h3>

        {/* Description snippet */}
        {task.description && (
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-3 whitespace-pre-wrap">
            {task.description}
          </p>
        )}
      </div>

      {/* Footer Info */}
      <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        {formattedDueDate ? (
          <div
            className={`flex items-center gap-1 font-medium ${
              isOverdue
                ? 'text-red-600 dark:text-red-400 font-semibold'
                : 'text-gray-500 dark:text-gray-400'
            }`}
            title={isOverdue ? 'Task is overdue!' : 'Due date'}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>
              {isOverdue ? 'Overdue: ' : 'Due: '}
              {formattedDueDate}
            </span>
          </div>
        ) : (
          <span className="text-gray-400 dark:text-gray-600 italic">No due date</span>
        )}

        <span className="text-[11px] text-gray-400 dark:text-gray-500" title={task.created_at}>
          {new Date(task.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );
};
