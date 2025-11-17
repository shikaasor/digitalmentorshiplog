/**
 * Users API Service
 */

import { apiClient } from './client'
import {
  User,
  UserCreate,
  UserUpdate,
  PaginatedResponse,
  UserRole,
} from '@/types'

export interface UserFilters {
  role?: UserRole
  is_active?: boolean
  search?: string
  skip?: number
  limit?: number
}

export const usersService = {
  /**
   * Get all users with filters (Admin/Supervisor only)
   */
  async getAll(filters?: UserFilters): Promise<PaginatedResponse<User>> {
    const params = new URLSearchParams()

    if (filters?.role) params.append('role', filters.role)
    if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString())
    if (filters?.search) params.append('search', filters.search)
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await apiClient.get<PaginatedResponse<User>>(
      `/api/users?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get a single user by ID
   */
  async getById(id: string): Promise<User> {
    const response = await apiClient.get<User>(`/api/users/${id}`)
    return response.data
  },

  /**
   * Create a new user (Admin only)
   */
  async create(data: UserCreate): Promise<User> {
    const response = await apiClient.post<User>('/api/users', data)
    return response.data
  },

  /**
   * Update an existing user (Admin/Supervisor only)
   */
  async update(id: string, data: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(`/api/users/${id}`, data)
    return response.data
  },

  /**
   * Delete a user (Admin only)
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/users/${id}`)
  },

  /**
   * Get current logged-in user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/users/me')
    return response.data
  },
}
