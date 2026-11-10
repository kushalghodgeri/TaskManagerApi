import React, { useEffect, useState } from 'react';
import { ArrowUpDown, RotateCcw, Search } from 'lucide-react';
import { TaskFilters, TaskPriority, TaskStatus } from '../types';

interface FilterBarProps {
  filters: TaskFilters;
  onChange: (filters: Partial<TaskFilters>) => void;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onChange, onReset }) => {
  const [searchTerm, setSearchTerm] = useState<string>(filters.search || '');

  // 300ms debounce on search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (filters.search || '')) {
        onChange({ search: searchTerm || undefined, skip: 0 });
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm, filters.search, onChange]);

  // Sync internal search state if reset externally
  useEffect(() => {
    setSearchTerm(filters.search || '');
  }, [filters.search]);

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/80 p-4 shadow-sm space-y-3">
      {/* Search Input */}
      <div className="relative w-full">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search tasks by title..."
          className="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Dropdown Filters and Sorting */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3">
        {/* Status */}
        <div>
          <label htmlFor="filter-status" className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
            Status
          </label>
          <select
            id="filter-status"
            value={filters.status || ''}
            onChange={(e) =>
              onChange({
                status: (e.target.value as TaskStatus) || undefined,
                skip: 0,
              })
            }
            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-2.5 py-1.5 text-xs sm:text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="filter-priority" className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
            Priority
          </label>
          <select
            id="filter-priority"
            value={filters.priority || ''}
            onChange={(e) =>
              onChange({
                priority: (e.target.value as TaskPriority) || undefined,
                skip: 0,
              })
            }
            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-2.5 py-1.5 text-xs sm:text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label htmlFor="filter-sortby" className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
            Sort By
          </label>
          <select
            id="filter-sortby"
            value={filters.sort_by || 'created_at'}
            onChange={(e) =>
              onChange({
                sort_by: e.target.value as 'created_at' | 'due_date' | 'priority',
                skip: 0,
              })
            }
            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-2.5 py-1.5 text-xs sm:text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="created_at">Created Date</option>
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
          </select>
        </div>

        {/* Order */}
        <div>
          <label htmlFor="filter-order" className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
            Order
          </label>
          <div className="flex items-center gap-1">
            <select
              id="filter-order"
              value={filters.order || 'desc'}
              onChange={(e) =>
                onChange({
                  order: e.target.value as 'asc' | 'desc',
                  skip: 0,
                })
              }
              className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-2.5 py-1.5 text-xs sm:text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
            <button
              type="button"
              onClick={() =>
                onChange({
                  order: filters.order === 'asc' ? 'desc' : 'asc',
                  skip: 0,
                })
              }
              title="Toggle sort direction"
              aria-label="Toggle sort direction"
              className="p-1.5 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <ArrowUpDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Reset Button */}
        <div className="col-span-2 sm:col-span-4 lg:col-span-1 flex items-end">
          <button
            type="button"
            onClick={onReset}
            className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};
