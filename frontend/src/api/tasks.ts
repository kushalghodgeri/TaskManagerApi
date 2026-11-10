import { apiClient } from './client';
import { Paginated, Task, TaskCreateInput, TaskFilters, TaskUpdateInput } from '../types';

export const tasksApi = {
  async getTasks(filters?: TaskFilters): Promise<Paginated<Task>> {
    const params = new URLSearchParams();

    if (filters?.status) params.append('status', filters.status);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.search && filters.search.trim()) params.append('search', filters.search.trim());
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters?.sort_by) params.append('sort_by', filters.sort_by);
    if (filters?.order) params.append('order', filters.order);

    const response = await apiClient.get<Paginated<Task>>('/tasks', { params });
    return response.data;
  },

  async getTask(id: number): Promise<Task> {
    const response = await apiClient.get<Task>(`/tasks/${id}`);
    return response.data;
  },

  async createTask(data: TaskCreateInput): Promise<Task> {
    const response = await apiClient.post<Task>('/tasks', data);
    return response.data;
  },

  async updateTask(id: number, data: TaskUpdateInput): Promise<Task> {
    const response = await apiClient.patch<Task>(`/tasks/${id}`, data);
    return response.data;
  },

  async deleteTask(id: number): Promise<void> {
    await apiClient.delete(`/tasks/${id}`);
  },
};
