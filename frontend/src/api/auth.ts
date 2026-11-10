import { apiClient } from './client';
import { AuthToken, LoginInput, RegisterInput, User } from '../types';

export const authApi = {
  async register(data: RegisterInput): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  async login(data: LoginInput): Promise<AuthToken> {
    const params = new URLSearchParams();
    params.append('username', data.username);
    params.append('password', data.password);

    const response = await apiClient.post<AuthToken>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },
};
