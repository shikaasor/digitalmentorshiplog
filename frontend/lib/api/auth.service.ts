/**
 * Authentication API Service
 */

import { apiClient } from './client'
import { LoginRequest, RegisterRequest, TokenResponse, User } from '@/types'

export const authService = {
  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/api/auth/login', credentials)
    return response.data
  },

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/register', data)
    return response.data
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me')
    return response.data
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout')
  },
}
