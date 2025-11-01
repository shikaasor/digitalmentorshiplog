/**
 * Authentication Store
 *
 * Zustand store for auth state management
 */

import { create } from 'zustand'
import { User, LoginRequest, RegisterRequest } from '@/types'
import { authService } from '../api/auth.service'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null

  // Actions
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  loadUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,

  /**
   * Login user
   */
  login: async (credentials: LoginRequest) => {
    set({ isLoading: true, error: null })
    try {
      // Call login API
      const tokenData = await authService.login(credentials)

      // Save token to localStorage
      localStorage.setItem('access_token', tokenData.access_token)

      // Fetch user data
      const user = await authService.getCurrentUser()

      // Save user to localStorage
      localStorage.setItem('user', JSON.stringify(user))

      set({ user, token: tokenData.access_token, isLoading: false })
    } catch (error: any) {
      const errorMessage = error.message || 'Login failed'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  /**
   * Register new user
   */
  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null })
    try {
      const user = await authService.register(data)

      // After registration, automatically login
      await useAuthStore.getState().login({
        email: data.email,
        password: data.password,
      })

      set({ isLoading: false })
    } catch (error: any) {
      const errorMessage = error.message || 'Registration failed'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')

      // Clear state
      set({ user: null, token: null, error: null })
    }
  },

  /**
   * Load user from localStorage (on app init)
   */
  loadUser: async () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    if (!token || !userStr) {
      return
    }

    try {
      // Parse stored user
      const user = JSON.parse(userStr) as User

      // Verify token is still valid by fetching current user
      const currentUser = await authService.getCurrentUser()

      set({ user: currentUser, token })
    } catch (error) {
      // Token is invalid, clear everything
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, token: null })
    }
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null })
  },
}))
