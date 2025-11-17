'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { usersService, UserFilters } from '@/lib/api/users.service'
import { User, UserRole } from '@/types'

export default function UsersPage() {
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  // Filters
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('')
  const [statusFilter, setStatusFilter] = useState<'active' | 'inactive' | ''>('')
  const [searchTerm, setSearchTerm] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const limit = 10

  useEffect(() => {
    loadUsers()
  }, [page, roleFilter, statusFilter])

  const loadUsers = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: UserFilters = {
        skip: (page - 1) * limit,
        limit,
      }

      if (roleFilter) {
        filters.role = roleFilter
      }

      if (statusFilter) {
        filters.is_active = statusFilter === 'active'
      }

      if (searchTerm) {
        filters.search = searchTerm
      }

      const response = await usersService.getAll(filters)
      setUsers(response.items || [])
      setTotal(response.total || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load users')
      setUsers([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    loadUsers()
  }

  const handleToggleStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await usersService.update(userId, { is_active: !currentStatus })
      loadUsers()
    } catch (err: any) {
      setError(err.message || 'Failed to update user status')
    }
  }

  const getRoleBadgeColor = (role: UserRole) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-700'
      case 'supervisor':
        return 'bg-blue-100 text-blue-700'
      case 'mentor':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Get supervisor name for a user
  const getSupervisorName = (user: User) => {
    if (!user.supervisor_id) return null
    const supervisor = users.find(u => u.id === user.supervisor_id)
    return supervisor?.name || 'Unknown'
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Users</h1>
            <p className="mt-2 text-gray-600">
              Manage user accounts and permissions
            </p>
          </div>
          <Link
            href="/users/new"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Add New User
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Search
                </button>
              </div>
            </div>

            {/* Role Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as UserRole | '')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Roles</option>
                <option value="mentor">Mentor</option>
                <option value="supervisor">Supervisor</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as 'active' | 'inactive' | '')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => {
                setRoleFilter('')
                setStatusFilter('')
                setSearchTerm('')
                setPage(1)
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
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
        )}

        {/* Table */}
        {!loading && users.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Supervisor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Specializations
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr
                      key={user.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {user.name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-3 py-1 text-xs font-medium rounded-full ${getRoleBadgeColor(
                            user.role
                          )}`}
                        >
                          {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {user.role === 'mentor' ? (
                          getSupervisorName(user) ? (
                            <span className="text-blue-600 font-medium">
                              {getSupervisorName(user)}
                            </span>
                          ) : (
                            <span className="text-gray-400 italic">No supervisor</span>
                          )
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {user.specializations && user.specializations.length > 0 ? (
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-700 rounded">
                              {user.specializations.length} area{user.specializations.length !== 1 ? 's' : ''}
                            </span>
                          </div>
                        ) : (
                          <span className="text-gray-400 text-sm">None</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleToggleStatus(user.id, user.is_active)}
                          className={`px-3 py-1 text-xs font-medium rounded-full ${
                            user.is_active
                              ? 'bg-green-100 text-green-700 hover:bg-green-200'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          } transition-colors`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => router.push(`/users/${user.id}/edit`)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {(page - 1) * limit + 1} to{' '}
                {Math.min(page * limit, total)} of {total} results
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page >= totalPages}
                  className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && users.length === 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || roleFilter || statusFilter
                ? 'Try adjusting your filters.'
                : 'Get started by adding a new user.'}
            </p>
            {!searchTerm && !roleFilter && !statusFilter && (
              <div className="mt-6">
                <Link
                  href="/users/new"
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition-colors"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  Add New User
                </Link>
              </div>
            )}
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
