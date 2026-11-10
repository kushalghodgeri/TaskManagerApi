import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  ListTodo,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { tasksApi } from '../api/tasks';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { EmptyState } from '../components/EmptyState';
import { FilterBar } from '../components/FilterBar';
import { Navbar } from '../components/Navbar';
import { Pagination } from '../components/Pagination';
import { Spinner } from '../components/Spinner';
import { TaskCard } from '../components/TaskCard';
import { TaskModal } from '../components/TaskModal';
import { useCreateTask, useDeleteTask, useTasks, useUpdateTask } from '../hooks/useTasks';
import { Task, TaskCreateInput, TaskFilters, TaskUpdateInput } from '../types';

export const DashboardPage: React.FC = () => {
  // Filters and pagination state
  const [filters, setFilters] = useState<TaskFilters>({
    status: undefined,
    priority: undefined,
    search: undefined,
    skip: 0,
    limit: 10,
    sort_by: 'created_at',
    order: 'desc',
  });

  // Modal & Dialog states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  // Queries & Mutations
  const { data, isLoading, isError, error, refetch, isFetching } = useTasks(filters);
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const deleteTaskMutation = useDeleteTask();

  // Summary stats queries
  const { data: totalStats } = useQuery({
    queryKey: ['tasks', 'stats', 'total'],
    queryFn: () => tasksApi.getTasks({ limit: 1 }),
  });
  const { data: todoStats } = useQuery({
    queryKey: ['tasks', 'stats', 'todo'],
    queryFn: () => tasksApi.getTasks({ status: 'todo', limit: 1 }),
  });
  const { data: inProgressStats } = useQuery({
    queryKey: ['tasks', 'stats', 'in_progress'],
    queryFn: () => tasksApi.getTasks({ status: 'in_progress', limit: 1 }),
  });
  const { data: doneStats } = useQuery({
    queryKey: ['tasks', 'stats', 'done'],
    queryFn: () => tasksApi.getTasks({ status: 'done', limit: 1 }),
  });

  // Handlers
  const handleFilterChange = (newFilters: Partial<TaskFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleResetFilters = () => {
    setFilters({
      status: undefined,
      priority: undefined,
      search: undefined,
      skip: 0,
      limit: 10,
      sort_by: 'created_at',
      order: 'desc',
    });
  };

  const handleOpenCreateModal = () => {
    setTaskToEdit(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (task: Task) => {
    setTaskToEdit(task);
    setIsModalOpen(true);
  };

  const handleModalSubmit = async (data: TaskCreateInput | TaskUpdateInput) => {
    if (taskToEdit) {
      await updateTaskMutation.mutateAsync({
        id: taskToEdit.id,
        data: data as TaskUpdateInput,
      });
    } else {
      await createTaskMutation.mutateAsync(data as TaskCreateInput);
    }
    setIsModalOpen(false);
  };

  const handleDeleteConfirm = async () => {
    if (!taskToDelete) return;
    await deleteTaskMutation.mutateAsync(taskToDelete.id);
    setTaskToDelete(null);
  };

  const stats = [
    {
      label: 'Total Tasks',
      count: totalStats?.total ?? 0,
      icon: ListTodo,
      color: 'text-gray-600 dark:text-gray-400',
      bg: 'bg-gray-100 dark:bg-gray-800',
    },
    {
      label: 'To Do',
      count: todoStats?.total ?? 0,
      icon: Clock,
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-950/50',
    },
    {
      label: 'In Progress',
      count: inProgressStats?.total ?? 0,
      icon: RefreshCw,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-50 dark:bg-blue-950/50',
    },
    {
      label: 'Done',
      count: doneStats?.total ?? 0,
      icon: CheckCircle2,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-50 dark:bg-green-950/50',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col transition-colors">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Header with Title and Create Action */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100">
              Task Dashboard
            </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Manage, organize, and track your tasks with real-time updates.
            </p>
          </div>

          <button
            type="button"
            onClick={handleOpenCreateModal}
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Task</span>
          </button>
        </div>

        {/* Status Summary Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800/80 p-4 shadow-sm flex items-center justify-between"
              >
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                    {stat.label}
                  </p>
                  <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-100">
                    {stat.count}
                  </p>
                </div>
                <div className={`p-2.5 rounded-lg ${stat.bg} ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Filter and Search Bar */}
        <FilterBar
          filters={filters}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
        />

        {/* Task Cards Content Section */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center">
              <Spinner size="lg" label="Loading tasks..." />
            </div>
          ) : isError ? (
            <div className="p-8 rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/40 text-center">
              <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400 mx-auto mb-2" />
              <h3 className="text-base font-semibold text-red-800 dark:text-red-300">
                Failed to load tasks
              </h3>
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {(error as any)?.message || 'An error occurred while fetching your tasks.'}
              </p>
              <button
                type="button"
                onClick={() => refetch()}
                className="mt-4 px-4 py-2 text-sm font-medium text-red-700 dark:text-red-300 bg-red-100 dark:bg-red-900/60 hover:bg-red-200 rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          ) : !data || data.items.length === 0 ? (
            <EmptyState
              title={filters.search || filters.status || filters.priority ? 'No matching tasks' : 'No tasks yet'}
              description={
                filters.search || filters.status || filters.priority
                  ? 'Try modifying your search or clearing active filters.'
                  : 'Start by creating your first task to stay organized.'
              }
              actionLabel="Create Task"
              onAction={handleOpenCreateModal}
            />
          ) : (
            <>
              {/* Task Cards Grid */}
              <div className="relative">
                {isFetching && (
                  <div className="absolute top-2 right-2 z-10">
                    <Spinner size="sm" />
                  </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {data.items.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onEdit={handleOpenEditModal}
                      onDelete={(t) => setTaskToDelete(t)}
                    />
                  ))}
                </div>
              </div>

              {/* Pagination Controls */}
              <Pagination
                total={data.total}
                skip={data.skip}
                limit={data.limit}
                onPageChange={(newSkip) => handleFilterChange({ skip: newSkip })}
                onLimitChange={(newLimit) => handleFilterChange({ limit: newLimit, skip: 0 })}
              />
            </>
          )}
        </div>
      </main>

      {/* Task Creation / Edit Modal */}
      <TaskModal
        isOpen={isModalOpen}
        taskToEdit={taskToEdit}
        isSubmitting={createTaskMutation.isPending || updateTaskMutation.isPending}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
      />

      {/* Confirm Deletion Dialog */}
      <ConfirmDialog
        isOpen={Boolean(taskToDelete)}
        title="Delete Task"
        message={`Are you sure you want to delete "${taskToDelete?.title}"? This action cannot be undone.`}
        confirmLabel="Delete Task"
        isConfirming={deleteTaskMutation.isPending}
        onConfirm={handleDeleteConfirm}
        onClose={() => setTaskToDelete(null)}
      />
    </div>
  );
};
