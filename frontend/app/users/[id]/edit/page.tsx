'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { usersService } from '@/lib/api/users.service'
import { UserUpdate, User, UserRole } from '@/types'
import { SPECIALIZATION_AREAS } from '@/lib/constants/thematic-areas'

export default function EditUserPage() {
  const router = useRouter()
  const params = useParams()
  const userId = params.id as string

  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [supervisors, setSupervisors] = useState<User[]>([])
  const [selectedSpecializations, setSelectedSpecializations] = useState<string[]>([])
  const [currentUser, setCurrentUser] = useState<User | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<UserUpdate>()

  const selectedRole = watch('role')

  useEffect(() => {
    if (userId) {
      loadUser()
      loadSupervisors()
    }
  }, [userId])

  const loadSupervisors = async () => {
    try {
      const response = await usersService.getAll({ role: UserRole.SUPERVISOR })
      setSupervisors(response.items)
    } catch (err) {
      console.error('Failed to fetch supervisors:', err)
    }
  }

  const loadUser = async () => {
    try {
      setInitialLoading(true)
      setError(null)
      const data = await usersService.getById(userId)
      setCurrentUser(data)

      // Set specializations from user data
      const userSpecializations = data.specializations?.map(s => s.thematic_area) || []
      setSelectedSpecializations(userSpecializations)

      // Reset form with existing data
      reset({
        name: data.name,
        designation: data.designation,
        region_state: data.region_state,
        role: data.role,
        is_active: data.is_active,
        supervisor_id: data.supervisor_id,
      })
    } catch (err: any) {
      setError(err.message || 'Failed to load user')
    } finally {
      setInitialLoading(false)
    }
  }

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

  const onSubmit = async (data: UserUpdate) => {
    try {
      setLoading(true)
      setError(null)

      // Add specializations to the data
      const userData = {
        ...data,
        specializations: selectedSpecializations,
      }

      await usersService.update(userId, userData)
      router.push('/users')
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to update user')
    } finally {
      setLoading(false)
    }
  }

  if (initialLoading) {
    return (
      <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
        <DashboardLayout>
          <div className="flex items-center justify-center py-12">
            <svg
              className="animate-spin h-10 w-10 text-blue-600"
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
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <button
              onClick={() => router.push('/users')}
              className="hover:text-gray-900"
            >
              Users
            </button>
            <span>/</span>
            <span className="text-gray-900">Edit User</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Edit User</h1>
          <p className="mt-2 text-gray-600">
            Update user information and permissions
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
                    Full Name
                  </label>
                  <input
                    type="text"
                    {...register('name')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter full name"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
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
                    User Role
                  </label>
                  <select
                    {...register('role')}
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
                {(selectedRole === 'mentor' || currentUser?.role === 'mentor') && (
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
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Thematic Area Specializations
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Select thematic areas where this user has specialized expertise. Specialists will receive notifications for logs in their areas.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {SPECIALIZATION_AREAS.map(area => (
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

            {/* Account Status */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Account Status
              </h2>
              <div className="flex items-center gap-3">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    {...register('is_active')}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  <span className="ml-3 text-sm font-medium text-gray-700">
                    Account Active
                  </span>
                </label>
                <p className="text-sm text-gray-500">
                  Inactive accounts cannot log in
                </p>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => router.push('/users')}
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
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
