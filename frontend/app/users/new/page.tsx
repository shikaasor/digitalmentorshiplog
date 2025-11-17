'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { usersService } from '@/lib/api/users.service'
import { UserCreate, User, UserRole } from '@/types'
import { THEMATIC_AREAS } from '@/lib/constants/thematic-areas'

export default function NewUserPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [supervisors, setSupervisors] = useState<User[]>([])
  const [selectedSpecializations, setSelectedSpecializations] = useState<string[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<UserCreate>()

  const password = watch('password')
  const selectedRole = watch('role')

  // Fetch supervisors on component mount
  useEffect(() => {
    const fetchSupervisors = async () => {
      try {
        const response = await usersService.getAll({ role: UserRole.SUPERVISOR })
        setSupervisors(response.items)
      } catch (err) {
        console.error('Failed to fetch supervisors:', err)
      }
    }
    fetchSupervisors()
  }, [])

  // Toggle specialization selection
  const toggleSpecialization = (area: string) => {
    setSelectedSpecializations(prev => {
      if (prev.includes(area)) {
        return prev.filter(a => a !== area)
      } else {
        return [...prev, area]
      }
    })
  }

  const onSubmit = async (data: UserCreate) => {
    try {
      setLoading(true)
      setError(null)

      // Add specializations to the data
      const userData = {
        ...data,
        specializations: selectedSpecializations,
      }

      await usersService.create(userData)
      router.push('/users')
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to create user')
    } finally {
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <button
              onClick={() => router.back()}
              className="hover:text-gray-900"
            >
              Users
            </button>
            <span>/</span>
            <span className="text-gray-900">New User</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Add New User</h1>
          <p className="mt-2 text-gray-600">
            Create a new user account in the system
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            {/* Personal Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Personal Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Full Name */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    {...register('name', { required: 'Full name is required' })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter full name"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
                    })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="user@example.com"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      {...register('password', {
                        required: 'Password is required',
                        minLength: {
                          value: 8,
                          message: 'Password must be at least 8 characters',
                        },
                      })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      placeholder="Enter password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showPassword ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Professional Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Professional Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Designation */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Designation
                  </label>
                  <input
                    type="text"
                    {...register('designation')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="e.g., Program Officer, Field Coordinator"
                  />
                </div>

                {/* Region/State */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Region/State
                  </label>
                  <input
                    type="text"
                    {...register('region_state')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter region or state"
                  />
                </div>
              </div>
            </div>

            {/* Role & Permissions */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Role & Permissions
              </h2>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    User Role <span className="text-red-500">*</span>
                  </label>
                  <select
                    {...register('role', { required: 'Role is required' })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select role</option>
                    <option value="mentor">Mentor - Can create and manage logs</option>
                    <option value="supervisor">Supervisor - Can view and approve logs</option>
                    <option value="admin">Admin - Full system access</option>
                  </select>
                  {errors.role && (
                    <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
                  )}
                  <p className="mt-2 text-sm text-gray-500">
                    Choose the appropriate role based on the user's responsibilities
                  </p>
                </div>

                {/* Supervisor Assignment (shown only for mentors) */}
                {selectedRole === 'mentor' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Assign Supervisor
                    </label>
                    <select
                      {...register('supervisor_id')}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    >
                      <option value="">No supervisor assigned</option>
                      {supervisors.map(supervisor => (
                        <option key={supervisor.id} value={supervisor.id}>
                          {supervisor.name} ({supervisor.email})
                        </option>
                      ))}
                    </select>
                    <p className="mt-2 text-sm text-gray-500">
                      The assigned supervisor will be able to approve this mentor's logs
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Thematic Area Specializations */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Thematic Area Specializations
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Select thematic areas where this user has specialized expertise. Specialists will receive notifications for logs in their areas.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {THEMATIC_AREAS.map(area => (
                  <label
                    key={area}
                    className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={selectedSpecializations.includes(area)}
                      onChange={() => toggleSpecialization(area)}
                      className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{area}</span>
                  </label>
                ))}
              </div>
              {selectedSpecializations.length > 0 && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>{selectedSpecializations.length}</strong> specialization(s) selected
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
