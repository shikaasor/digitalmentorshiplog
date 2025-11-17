'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { reportsService, FollowUpsReportFilters } from '@/lib/api/reports.service'
import { FollowUpsReport, FollowUpStatus } from '@/types'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

export default function FollowUpsReportPage() {
  const [report, setReport] = useState<FollowUpsReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [status, setStatus] = useState<FollowUpStatus | ''>('')
  const [priority, setPriority] = useState('')

  useEffect(() => {
    loadReport()
  }, [])

  const loadReport = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: FollowUpsReportFilters = {}
      if (status) filters.status = status
      if (priority) filters.priority = priority

      const data = await reportsService.getFollowUpsReport(filters)
      setReport(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load follow-ups report')
    } finally {
      setLoading(false)
    }
  }

  const handleApplyFilters = () => {
    loadReport()
  }

  const handleClearFilters = () => {
    setStatus('')
    setPriority('')
  }

  // Prepare chart data
  const chartData = report
    ? Object.entries(report.by_status).map(([status, count]) => ({
        name: status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' '),
        value: count,
      }))
    : []

  const COLORS = ['#F59E0B', '#3B82F6', '#10B981', '#EF4444']

  // Calculate percentages
  const pendingPercentage = report && report.total_count > 0
    ? ((report.pending_count / report.total_count) * 100).toFixed(1)
    : '0'

  const overduePercentage = report && report.total_count > 0
    ? ((report.overdue_count / report.total_count) * 100).toFixed(1)
    : '0'

  return (
    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <Link
            href="/reports"
            className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Follow-Ups Report</h1>
          <p className="mt-2 text-gray-600">
            Track pending, overdue, and completed action items
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as FollowUpStatus | '')}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Priorities</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <div className="flex items-end gap-2">
              <button
                onClick={handleApplyFilters}
                className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Apply
              </button>
              <button
                onClick={handleClearFilters}
                className="px-4 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Clear
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

        {/* Content */}
        {!loading && report && (
          <>
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Follow-Ups</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {report.total_count}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Pending</p>
                    <p className="text-3xl font-bold text-yellow-600 mt-2">
                      {report.pending_count}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{pendingPercentage}% of total</p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-yellow-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Overdue</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">
                      {report.overdue_count}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{overduePercentage}% of total</p>
                  </div>
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-red-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Completed</p>
                    <p className="text-3xl font-bold text-green-600 mt-2">
                      {report.by_status['completed'] || 0}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Chart and Status Table */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Status Distribution Chart */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Status Distribution
                </h3>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) =>
                          `${name}: ${(percent * 100).toFixed(0)}%`
                        }
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-center text-gray-500 py-12">No data available</p>
                )}
              </div>

              {/* Status Breakdown Table */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Status Breakdown
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
                          Status
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                          Count
                        </th>
                        <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase">
                          Percentage
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(report.by_status).map(([status, count]) => {
                        const percentage = report.total_count > 0
                          ? ((count / report.total_count) * 100).toFixed(1)
                          : '0'
                        return (
                          <tr key={status}>
                            <td className="px-4 py-3 text-sm text-gray-900 capitalize">
                              {status.replace('_', ' ')}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium">
                              {count}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-600 text-right">
                              {percentage}%
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Alert for Overdue Items */}
            {report.overdue_count > 0 && (
              <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg
                      className="w-6 h-6 text-red-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-semibold text-red-800">
                      Attention Required
                    </h3>
                    <p className="text-sm text-red-700 mt-1">
                      You have <strong>{report.overdue_count}</strong> overdue follow-up{report.overdue_count !== 1 ? 's' : ''} that need immediate attention.
                    </p>
                    <Link
                      href="/follow-ups"
                      className="text-sm text-red-800 font-medium hover:text-red-900 mt-2 inline-block underline"
                    >
                      View all follow-ups →
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
