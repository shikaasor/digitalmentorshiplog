/**
 * Authentication Store
 *
 * Zustand store for auth state management with robust error handling
 * and truly stateless JWT authentication
 */

import { create } from 'zustand'
import { User, LoginRequest, RegisterRequest } from '@/types'
import { authService } from '../api/auth.service'
import { toast } from './toast.store'
import { handleApiError } from '../api/client'

// Helper: Decode JWT and check if it's expired
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const expiration = payload.exp * 1000 // Convert to milliseconds
    return Date.now() >= expiration
  } catch {
    return true // If we can't parse it, consider it expired
  }
}

// Helper: Get token expiration time
function getTokenExpiration(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 // Convert to milliseconds
  } catch {
    return null
  }
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null

  // Actions
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  loadUser: () => void
  isAuthenticated: () => boolean
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

      // Show success toast
      toast.success('Welcome back!', `Logged in as ${user.name}`)
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      set({ error: errorMessage, isLoading: false })

      // Show error toast
      toast.error('Login Failed', errorMessage)
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

      // Show success toast
      toast.success('Registration Successful!', 'Logging you in...')

      // After registration, automatically login
      await useAuthStore.getState().login({
        email: data.email,
        password: data.password,
      })

      set({ isLoading: false })
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      set({ error: errorMessage, isLoading: false })

      // Show error toast
      toast.error('Registration Failed', errorMessage)
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
   * This is now STATELESS - only checks localStorage, no API call
   */
  loadUser: () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    // No token or user data
    if (!token || !userStr) {
      set({ user: null, token: null })
      return
    }

    // Check if token is expired (client-side validation)
    if (isTokenExpired(token)) {
      console.log('Token expired, clearing auth data')
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, token: null })
      return
    }

    // Token is valid, restore user from localStorage
    try {
      const user = JSON.parse(userStr) as User
      set({ user, token })
    } catch (error) {
      console.error('Failed to parse user data:', error)
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, token: null })
    }
  },

  /**
   * Check if user is authenticated (has valid token)
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('access_token')
    if (!token) return false
    return !isTokenExpired(token)
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null })
  },
}))
