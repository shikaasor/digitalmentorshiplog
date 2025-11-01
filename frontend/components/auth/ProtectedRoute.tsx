'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth.store'
import { UserRole } from '@/types'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: UserRole[]
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const router = useRouter()
  const { user, loadUser } = useAuthStore()
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Try to load user from localStorage on mount
    loadUser()
  }, [loadUser])

  useEffect(() => {
    // If no token, redirect to login
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/auth/login')
      setIsLoading(false)
      return
    }

    // Wait for user to be loaded
    if (!user) {
      setIsLoading(true)
      return
    }

    // Check if user has required role
    if (allowedRoles && allowedRoles.length > 0) {
      if (!allowedRoles.includes(user.role)) {
        console.warn(`Access denied: User role '${user.role}' not in allowed roles:`, allowedRoles)
        router.push('/dashboard')
        setIsAuthorized(false)
        setIsLoading(false)
        return
      }
    }

    // User is authorized
    setIsAuthorized(true)
    setIsLoading(false)
  }, [user, router, allowedRoles])

  // Show loading while checking auth and permissions
  if (isLoading || !isAuthorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-gray-600">
            {isLoading ? 'Loading...' : 'Checking permissions...'}
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
