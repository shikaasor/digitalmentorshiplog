'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { followUpsService, FollowUpFilters } from '@/lib/api/follow-ups.service'
import { usersService } from '@/lib/api/users.service'
import { FollowUp, FollowUpStatus, User, UserRole } from '@/types'
import { useAuthStore } from '@/lib/stores/auth.store'

export default function FollowUpsPage() {
  const router = useRouter()
  const { user: currentUser } = useAuthStore()
  const [followUps, setFollowUps] = useState<FollowUp[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  const canAssign = currentUser?.role === UserRole.ADMIN || currentUser?.role === UserRole.SUPERVISOR

  // Filters
  const [statusFilter, setStatusFilter] = useState<FollowUpStatus | ''>('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const limit = 10

  // Assignment modal state
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [selectedFollowUp, setSelectedFollowUp] = useState<FollowUp | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [selectedUserId, setSelectedUserId] = useState<string>('')
  const [assignmentLoading, setAssignmentLoading] = useState(false)

  useEffect(() => {
    loadFollowUps()
  }, [page, statusFilter, priorityFilter])

  useEffect(() => {
    // Load users only for admins/supervisors who can assign
    if (canAssign) {
      loadUsers()
    }
  }, [canAssign])

  const loadFollowUps = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: FollowUpFilters = {
        skip: (page - 1) * limit,
        limit,
      }

      if (statusFilter) {
        filters.status = statusFilter
      }

      if (priorityFilter) {
        filters.priority = priorityFilter
      }

      const response = await followUpsService.getAll(filters)
      setFollowUps(response.items || [])
      setTotal(response.total || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load follow-ups')
      setFollowUps([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (id: string, newStatus: 'in_progress' | 'completed') => {
    try {
      if (newStatus === 'in_progress') {
        await followUpsService.markInProgress(id)
      } else {
        await followUpsService.markCompleted(id)
      }
      loadFollowUps()
    } catch (err: any) {
      setError(err.message || 'Failed to update follow-up status')
    }
  }

  const handleDelete = async (id: string, actionItem: string) => {
    if (!confirm(`Are you sure you want to delete "${actionItem}"? This action cannot be undone.`)) {
      return
    }

    try {
      await followUpsService.delete(id)
      loadFollowUps()
    } catch (err: any) {
      setError(err.message || 'Failed to delete follow-up')
    }
  }

  const loadUsers = async () => {
    try {
      const response = await usersService.getAll({ is_active: true, limit: 500 })
      setUsers(response.items)
    } catch (err: any) {
      console.error('Failed to load users:', err)
    }
  }

  const openAssignModal = (followUp: FollowUp) => {
    setSelectedFollowUp(followUp)
    setSelectedUserId(followUp.assigned_to || '')
    setShowAssignModal(true)
  }

  const closeAssignModal = () => {
    setShowAssignModal(false)
    setSelectedFollowUp(null)
    setSelectedUserId('')
  }

  const handleAssign = async () => {
    if (!selectedFollowUp || !selectedUserId) return

    try {
      setAssignmentLoading(true)
      await followUpsService.update(selectedFollowUp.id, {
        assigned_to: selectedUserId
      })
      loadFollowUps()
      closeAssignModal()
    } catch (err: any) {
      setError(err.message || 'Failed to assign follow-up')
    } finally {
      setAssignmentLoading(false)
    }
  }

  const getStatusBadge = (status: FollowUpStatus) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
    }
    const labels = {
      pending: 'Pending',
      in_progress: 'In Progress',
      completed: 'Completed',
    }

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}
      >
        {labels[status]}
      </span>
    )
  }

  const getPriorityBadge = (priority?: string) => {
    if (!priority) return null

    const styles = {
      High: 'bg-red-100 text-red-800',
      Medium: 'bg-yellow-100 text-yellow-800',
      Low: 'bg-gray-100 text-gray-800',
    }

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          styles[priority as keyof typeof styles] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {priority}
      </span>
    )
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const isOverdue = (targetDate?: string) => {
    if (!targetDate) return false
    return new Date(targetDate) < new Date() && !followUps.find((f) => f.status === 'completed')
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Follow-Up Actions</h1>
            <p className="mt-2 text-gray-600">
              Track and manage action items from mentorship logs
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as FollowUpStatus | '')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Statuses</option>
                <option value={FollowUpStatus.PENDING}>Pending</option>
                <option value={FollowUpStatus.IN_PROGRESS}>In Progress</option>
                <option value={FollowUpStatus.COMPLETED}>Completed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Priorities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <button
                onClick={() => {
                  setStatusFilter('')
                  setPriorityFilter('')
                  setSearchTerm('')
                  setPage(1)
                }}
                className="w-full px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Clear Filters
              </button>
            </div>
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
        {!loading && followUps.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Action Item
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Assigned To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Target Date
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {followUps.map((followUp) => (
                    <tr
                      key={followUp.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-md">
                        <div className="font-medium">{followUp.action_item}</div>
                        {followUp.responsible_person && (
                          <div className="text-xs text-gray-500 mt-1">
                            Responsible: {followUp.responsible_person}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {getStatusBadge(followUp.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {getPriorityBadge(followUp.priority)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {followUp.assigned_to ? (
                          <div>
                            <div className="font-medium text-gray-900">
                              {users.length > 0
                                ? (users.find(u => u.id === followUp.assigned_to)?.name || 'Unknown User')
                                : 'Assigned'}
                            </div>
                            {followUp.responsible_person && (
                              <div className="text-xs text-gray-500 mt-0.5">
                                Team: {followUp.responsible_person}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div>
                            <div className="text-gray-500">Not assigned</div>
                            {followUp.responsible_person && (
                              <div className="text-xs text-gray-600 mt-0.5">
                                Team: {followUp.responsible_person}
                              </div>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span
                          className={
                            isOverdue(followUp.target_date)
                              ? 'text-red-600 font-medium'
                              : 'text-gray-600'
                          }
                        >
                          {formatDate(followUp.target_date)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          {canAssign && (
                            <button
                              onClick={() => openAssignModal(followUp)}
                              className="text-purple-600 hover:text-purple-800"
                              title="Assign to user"
                            >
                              Assign
                            </button>
                          )}
                          {followUp.status === FollowUpStatus.PENDING && (
                            <button
                              onClick={() =>
                                handleStatusChange(followUp.id, 'in_progress')
                              }
                              className="text-blue-600 hover:text-blue-800"
                              title="Start"
                            >
                              Start
                            </button>
                          )}
                          {followUp.status === FollowUpStatus.IN_PROGRESS && (
                            <button
                              onClick={() =>
                                handleStatusChange(followUp.id, 'completed')
                              }
                              className="text-green-600 hover:text-green-800"
                              title="Complete"
                            >
                              Complete
                            </button>
                          )}
                          <button
                            onClick={() =>
                              handleDelete(followUp.id, followUp.action_item)
                            }
                            className="text-red-600 hover:text-red-800"
                            title="Delete"
                          >
                            Delete
                          </button>
                        </div>
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
        {!loading && followUps.length === 0 && (
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No follow-ups found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {statusFilter || priorityFilter
                ? 'Try adjusting your filters.'
                : 'Follow-ups are created from mentorship logs.'}
            </p>
          </div>
        )}

        {/* Assignment Modal */}
        {showAssignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Assign Follow-Up
                </h3>
                <button
                  onClick={closeAssignModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {selectedFollowUp && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Action Item:</p>
                  <p className="text-sm font-medium text-gray-900 mb-4">
                    {selectedFollowUp.action_item}
                  </p>

                  {selectedFollowUp.responsible_person && (
                    <p className="text-xs text-gray-500 mb-4">
                      Responsible Team: {selectedFollowUp.responsible_person}
                    </p>
                  )}

                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assign to User
                  </label>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select a user...</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.name} ({user.email})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex gap-3 justify-end">
                <button
                  onClick={closeAssignModal}
                  className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={assignmentLoading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAssign}
                  disabled={!selectedUserId || assignmentLoading}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {assignmentLoading ? 'Assigning...' : 'Assign'}
                </button>
              </div>
            </div>
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
