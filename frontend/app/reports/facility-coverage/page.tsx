'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { reportsService, FacilityCoverageFilters } from '@/lib/api/reports.service'
import { FacilityCoverageReport } from '@/types'

export default function FacilityCoverageReportPage() {
  const [report, setReport] = useState<FacilityCoverageReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [state, setState] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const itemsPerPage = 20

  useEffect(() => {
    loadReport()
  }, [])

  const loadReport = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: FacilityCoverageFilters = {}
      if (state) filters.state = state

      const data = await reportsService.getFacilityCoverageReport(filters)
      setReport(data)
      setPage(1) // Reset to first page when filters change
    } catch (err: any) {
      setError(err.message || 'Failed to load facility coverage report')
    } finally {
      setLoading(false)
    }
  }

  const handleApplyFilters = () => {
    loadReport()
  }

  const handleClearFilters = () => {
    setState('')
  }

  // Get unique states from report data
  const availableStates = report
    ? Array.from(new Set(report.facilities.map((f) => f.state).filter(Boolean)))
        .sort()
    : []

  // Pagination
  const paginatedFacilities = report
    ? report.facilities.slice((page - 1) * itemsPerPage, page * itemsPerPage)
    : []

  const totalPages = report ? Math.ceil(report.facilities.length / itemsPerPage) : 0

  // Calculate coverage percentage
  const coveragePercentage = report && report.total_facilities > 0
    ? ((report.visited_facilities / report.total_facilities) * 100).toFixed(1)
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
          <h1 className="text-3xl font-bold text-gray-900">Facility Coverage Report</h1>
          <p className="mt-2 text-gray-600">
            View facility visit coverage and identify gaps in service delivery
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <select
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All States</option>
                {availableStates.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
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
                    <p className="text-sm font-medium text-gray-600">Total Facilities</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {report.total_facilities}
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
                        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Visited Facilities</p>
                    <p className="text-3xl font-bold text-green-600 mt-2">
                      {report.visited_facilities}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{coveragePercentage}% coverage</p>
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

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Unvisited Facilities</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">
                      {report.unvisited_facilities}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(100 - parseFloat(coveragePercentage)).toFixed(1)}% gap
                    </p>
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
                    <p className="text-sm font-medium text-gray-600">Coverage Rate</p>
                    <p className="text-3xl font-bold text-purple-600 mt-2">
                      {coveragePercentage}%
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
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Facilities Table */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Facilities ({report.facilities.length})
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Facility Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Code
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        State
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        LGA
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Visits
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Last Visit
                      </th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {paginatedFacilities.map((facility) => (
                      <tr key={facility.facility_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {facility.facility_name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {facility.facility_code || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {facility.state || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {facility.lga || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 text-center font-medium">
                          {facility.visit_count}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {facility.last_visit_date
                            ? new Date(facility.last_visit_date).toLocaleDateString()
                            : '-'}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {facility.visit_count > 0 ? (
                            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                              Visited
                            </span>
                          ) : (
                            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">
                              Not Visited
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing {(page - 1) * itemsPerPage + 1} to{' '}
                    {Math.min(page * itemsPerPage, report.facilities.length)} of{' '}
                    {report.facilities.length} facilities
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
              )}
            </div>

            {/* Alert for Unvisited Facilities */}
            {report.unvisited_facilities > 0 && (
              <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
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
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-semibold text-yellow-800">
                      Coverage Gap Identified
                    </h3>
                    <p className="text-sm text-yellow-700 mt-1">
                      <strong>{report.unvisited_facilities}</strong> facilit{report.unvisited_facilities !== 1 ? 'ies have' : 'y has'} not been visited yet.
                      Consider scheduling visits to improve coverage.
                    </p>
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
