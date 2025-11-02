/**
 * API Client Configuration
 *
 * Axios instance with auth interceptors and robust error handling
 */

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ApiError } from '@/types'
import { parseError, logError, shouldLogout } from '@/lib/errors/error-handler'
import { toast } from '@/lib/stores/toast.store'

// Create axios instance
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors gracefully
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError<ApiError>) => {
    // Parse error using centralized handler
    const appError = parseError(error)

    // Log error for debugging
    logError(appError, 'API Client')

    // Only logout and redirect on 401 (Unauthorized), not on 403 (Forbidden)
    if (appError.statusCode === 401 && shouldLogout(appError)) {
      if (typeof window !== 'undefined') {
        // Clear auth data
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')

        // Show toast before redirecting
        toast.error('Session Expired', 'Please log in again to continue.')

        // Redirect after a short delay to allow toast to show
        setTimeout(() => {
          window.location.href = '/auth/login'
        }, 1000)
      }
    }

    // For 403 errors, just show a toast but don't logout
    if (appError.statusCode === 403) {
      toast.error('Access Denied', appError.message)
    }

    // Return rejected promise with parsed error
    return Promise.reject(appError)
  }
)

// Helper function to handle API errors in components
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const appError = parseError(error)
    return appError.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}

// Helper to show error toast from components
export function showErrorToast(error: unknown, context?: string) {
  const message = handleApiError(error)
  const details = error && typeof error === 'object' && 'details' in error
    ? (error as any).details
    : undefined

  toast.error(
    context || 'Operation Failed',
    details || message
  )
}
