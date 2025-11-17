'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { facilitiesService, FacilityFilters } from '@/lib/api/facilities.service'
import { Facility, UserRole } from '@/types'
import { useAuthStore } from '@/lib/stores/auth.store'
import { STATES, FACILITY_TYPES } from '@/lib/constants'

export default function FacilitiesPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  const isAdmin = user?.role === UserRole.ADMIN

  // Filters
  const [stateFilter, setStateFilter] = useState('')
  const [facilityTypeFilter, setFacilityTypeFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  // Pagination
  const [page, setPage] = useState(1)
  const limit = 10

  useEffect(() => {
    loadFacilities()
  }, [page, stateFilter, facilityTypeFilter])

  const loadFacilities = async () => {
    try {
      setLoading(true)
      setError(null)

      const filters: FacilityFilters = {
        skip: (page - 1) * limit,
        limit,
      }

      if (stateFilter) {
        filters.state = stateFilter
      }

      if (facilityTypeFilter) {
        filters.facility_type = facilityTypeFilter
      }

      if (searchTerm) {
        filters.search = searchTerm
      }

      const response = await facilitiesService.getAll(filters)
      setFacilities(response.items || [])
      setTotal(response.total || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load facilities')
      setFacilities([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    loadFacilities()
  }

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
      return
    }

    try {
      await facilitiesService.delete(id)
      loadFacilities()
    } catch (err: any) {
      setError(err.message || 'Failed to delete facility')
    }
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Facilities</h1>
            <p className="mt-2 text-gray-600">
              Manage healthcare facilities in the mentorship program
            </p>
          </div>
          {isAdmin && (
            <Link
              href="/facilities/new"
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
              Add New Facility
            </Link>
          )}
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
                  placeholder="Search by name, code, or location..."
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

            {/* State Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                State
              </label>
              <select
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All States</option>
                {STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>

            {/* Facility Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Facility Type
              </label>
              <select
                value={facilityTypeFilter}
                onChange={(e) => setFacilityTypeFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="">All Types</option>
                {FACILITY_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Clear Filters */}
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => {
                setStateFilter('')
                setFacilityTypeFilter('')
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
        {!loading && facilities.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
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
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      State
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                      Contact
                    </th>
                    {isAdmin && (
                      <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Actions
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {facilities.map((facility) => (
                    <tr
                      key={facility.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => router.push(`/facilities/${facility.id}`)}
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {facility.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {facility.code || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {facility.facility_type || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {facility.location || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {facility.state || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {facility.contact_person && (
                          <div>
                            <div className="font-medium">{facility.contact_person}</div>
                            {facility.contact_phone && (
                              <div className="text-xs text-gray-500">{facility.contact_phone}</div>
                            )}
                          </div>
                        )}
                        {!facility.contact_person && 'N/A'}
                      </td>
                      {isAdmin && (
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              router.push(`/facilities/${facility.id}/edit`)
                            }}
                            className="text-blue-600 hover:text-blue-800 mr-4"
                          >
                            Edit
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(facility.id, facility.name)
                            }}
                            className="text-red-600 hover:text-red-800"
                          >
                            Delete
                          </button>
                        </td>
                      )}
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
        {!loading && facilities.length === 0 && (
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
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No facilities found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || stateFilter || facilityTypeFilter
                ? 'Try adjusting your filters.'
                : isAdmin
                ? 'Get started by adding a new facility.'
                : 'No facilities available at the moment.'}
            </p>
            {isAdmin && !searchTerm && !stateFilter && !facilityTypeFilter && (
              <div className="mt-6">
                <Link
                  href="/facilities/new"
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
                  Add New Facility
                </Link>
              </div>
            )}
          </div>
        )}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
