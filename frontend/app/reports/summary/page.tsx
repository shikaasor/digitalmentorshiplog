'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { reportsService } from '@/lib/api/reports.service'
import { SummaryReport } from '@/types'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

export default function SummaryReportPage() {
  const [summary, setSummary] = useState<SummaryReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSummary()
  }, [])

  const loadSummary = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await reportsService.getSummary()
      setSummary(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load summary report')
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const logsChartData = summary
    ? Object.entries(summary.logs_by_status).map(([status, count]) => ({
        name: status.charAt(0).toUpperCase() + status.slice(1),
        value: count,
      }))
    : []

  const followUpsChartData = summary
    ? Object.entries(summary.follow_ups_by_status).map(([status, count]) => ({
        name: status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' '),
        value: count,
      }))
    : []

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

  return (
    <ProtectedRoute allowedRoles={['admin', 'supervisor']}>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link
              href="/reports"
              className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Reports
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Summary Report</h1>
            <p className="mt-2 text-gray-600">
              Overview of all mentorship activities and key performance indicators
            </p>
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
        {!loading && summary && (
          <>
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Logs</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {summary.total_logs}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Image
                      src="/images/icon.png"
                      alt="Logs"
                      width={24}
                      height={24}
                      className="w-6 h-6"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Facilities</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {summary.total_facilities}
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
                        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Mentors</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {summary.total_mentors}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="w-6 h-6 text-purple-600"
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
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Follow-Ups</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {summary.total_follow_ups}
                    </p>
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
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Logs by Status Chart */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Logs by Status
                </h3>
                {logsChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={logsChartData}
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
                        {logsChartData.map((entry, index) => (
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

              {/* Follow-Ups by Status Chart */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Follow-Ups by Status
                </h3>
                {followUpsChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={followUpsChartData}
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
                        {followUpsChartData.map((entry, index) => (
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
            </div>

            {/* Status Breakdown Tables */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Logs Status Table */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Logs Status Breakdown
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
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(summary.logs_by_status).map(([status, count]) => (
                        <tr key={status}>
                          <td className="px-4 py-3 text-sm text-gray-900 capitalize">
                            {status}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium">
                            {count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Follow-Ups Status Table */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Follow-Ups Status Breakdown
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
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(summary.follow_ups_by_status).map(([status, count]) => (
                        <tr key={status}>
                          <td className="px-4 py-3 text-sm text-gray-900 capitalize">
                            {status.replace('_', ' ')}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900 text-right font-medium">
                            {count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
