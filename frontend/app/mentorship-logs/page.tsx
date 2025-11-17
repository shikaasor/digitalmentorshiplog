'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { mentorshipLogsService, MentorshipLogFilters } from '@/lib/api/mentorship-logs.service'
import { MentorshipLog, LogStatus } from '@/types'

export default function MentorshipLogsPage() {
  const router = useRouter()
  const [logs, setLogs] = useState<MentorshipLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  // Filters
  const [statusFilter, setStatusFilter] = useState<LogStatus | ''>('')
  const [searchTerm, setSearchTerm] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const limit = 10

  useEffect(() => {
    loadLogs()
  }, [page, statusFilter])

  const loadLogs = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: MentorshipLogFilters = {
        skip: (page - 1) * limit,
        limit,
      }

      if (statusFilter) {
        filters.status = statusFilter
      }

      const response = await mentorshipLogsService.getAll(filters)
      setLogs(response.items || [])
      setTotal(response.total || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load mentorship logs')
    } finally {
      setLoading(false)
    }
  }

  const getStatusDisplay = (log: MentorshipLog) => {
    // If log has been rejected, show "Returned" status
    if (log.rejected_at && log.status === LogStatus.DRAFT) {
      return {
        text: 'Returned',
        color: 'bg-red-100 text-red-700',
      }
    }

    // Otherwise show normal status
    switch (log.status) {
      case LogStatus.DRAFT:
        return { text: 'Draft', color: 'bg-gray-100 text-gray-700' }
      case LogStatus.SUBMITTED:
        return { text: 'Submitted', color: 'bg-yellow-100 text-yellow-700' }
      case LogStatus.APPROVED:
        return { text: 'Approved', color: 'bg-green-100 text-green-700' }
      case LogStatus.COMPLETED:
        return { text: 'Completed', color: 'bg-blue-100 text-blue-700' }
      default:
        return { text: 'Unknown', color: 'bg-gray-100 text-gray-700' }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Mentorship Logs</h1>
            <p className="mt-2 text-gray-600">
              View and manage all mentorship visit logs
            </p>
          </div>
          <Link
            href="/mentorship-logs/new"
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
            Create New Log
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                placeholder="Search by facility or mentor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as LogStatus | '')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Actions */}
            <div className="flex items-end">
              <button
                onClick={() => {
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
        {!loading && logs.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Visit Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Facility
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Mentor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {logs.map((log) => (
                    <tr
                      key={log.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => router.push(`/mentorship-logs/${log.id}`)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(log.visit_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {log.facility ? (
                          <Link
                            href={`/facilities/${log.facility_id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                          >
                            {log.facility.name}
                          </Link>
                        ) : (
                          <span className="text-gray-900">N/A</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.mentor?.name || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-3 py-1 text-xs font-medium rounded-full ${
                            getStatusDisplay(log).color
                          }`}
                        >
                          {getStatusDisplay(log).text}
                        </span>
                        {log.rejected_at && log.status === LogStatus.DRAFT && (
                          <div className="mt-1 text-xs text-red-600">
                            Needs revision
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {log.duration_hours || 0}h {log.duration_minutes || 0}m
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/mentorship-logs/${log.id}/edit`)
                          }}
                          className="text-blue-600 hover:text-blue-800 mr-4"
                        >
                          Edit
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            router.push(`/mentorship-logs/${log.id}`)
                          }}
                          className="text-gray-600 hover:text-gray-800"
                        >
                          View
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
        {!loading && logs.length === 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <Image
              src="/images/icon.png"
              alt="No logs"
              width={48}
              height={48}
              className="mx-auto h-12 w-12 opacity-40"
            />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No logs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating a new mentorship log.
            </p>
            <div className="mt-6">
              <Link
                href="/mentorship-logs/new"
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
                Create New Log
              </Link>
            </div>
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
