import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { tasksApi } from '../api/tasks';
import { TaskCreateInput, TaskFilters, TaskStatus, TaskUpdateInput } from '../types';

export const useTasks = (filters: TaskFilters) => {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => tasksApi.getTasks(filters),
    placeholderData: (previousData) => previousData,
  });
};

export const useCreateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreateInput) => tasksApi.createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task created successfully');
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Failed to create task';
      toast.error(msg);
    },
  });
};

export const useUpdateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TaskUpdateInput }) =>
      tasksApi.updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task updated successfully');
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Failed to update task';
      toast.error(msg);
    },
  });
};

export const useDeleteTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => tasksApi.deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      toast.success('Task deleted successfully');
    },
    onError: (error: any) => {
      const msg = error.response?.data?.detail || 'Failed to delete task';
      toast.error(msg);
    },
  });
};

export const getNextStatus = (current: TaskStatus): TaskStatus => {
  switch (current) {
    case 'todo':
      return 'in_progress';
    case 'in_progress':
      return 'done';
    case 'done':
      return 'todo';
  }
};
