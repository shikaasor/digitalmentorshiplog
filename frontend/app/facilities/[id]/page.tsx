'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { facilitiesService } from '@/lib/api/facilities.service'
import { Facility, UserRole } from '@/types'
import { useAuthStore } from '@/lib/stores/auth.store'

export default function FacilityViewPage() {
  const router = useRouter()
  const params = useParams()
  const facilityId = params.id as string
  const { user } = useAuthStore()

  const [facility, setFacility] = useState<Facility | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isAdmin = user?.role === UserRole.ADMIN

  useEffect(() => {
    if (facilityId) {
      loadFacility()
    }
  }, [facilityId])

  const loadFacility = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await facilitiesService.getById(facilityId)
      setFacility(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load facility')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!facility) return

    if (!confirm(`Are you sure you want to delete "${facility.name}"? This action cannot be undone.`)) {
      return
    }

    try {
      await facilitiesService.delete(facilityId)
      router.push('/facilities')
    } catch (err: any) {
      setError(err.message || 'Failed to delete facility')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <ProtectedRoute>
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

  if (error || !facility) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error || 'Facility not found'}
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
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
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back
            </button>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <button
              onClick={() => router.push('/facilities')}
              className="hover:text-gray-900"
            >
              Facilities
            </button>
            <span>/</span>
            <span className="text-gray-900">{facility.name}</span>
          </div>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{facility.name}</h1>
              {facility.code && (
                <p className="mt-1 text-gray-600">Code: {facility.code}</p>
              )}
            </div>
            {isAdmin && (
              <div className="flex gap-3">
                <button
                  onClick={() => router.push(`/facilities/${facilityId}/edit`)}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
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
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
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
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Facility Details */}
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Basic Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Facility Name
                </label>
                <p className="text-gray-900">{facility.name}</p>
              </div>

              {facility.code && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Facility Code
                  </label>
                  <p className="text-gray-900">{facility.code}</p>
                </div>
              )}

              {facility.facility_type && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Facility Type
                  </label>
                  <p className="text-gray-900">{facility.facility_type}</p>
                </div>
              )}
            </div>
          </div>

          {/* Location Details */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Location Details
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {facility.location && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    Address/Location
                  </label>
                  <p className="text-gray-900">{facility.location}</p>
                </div>
              )}

              {facility.state && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    State
                  </label>
                  <p className="text-gray-900">{facility.state}</p>
                </div>
              )}

              {facility.lga && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">
                    LGA (Local Government Area)
                  </label>
                  <p className="text-gray-900">{facility.lga}</p>
                </div>
              )}
            </div>
          </div>

          {/* Contact Information */}
          {(facility.contact_person || facility.contact_email || facility.contact_phone) && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Contact Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {facility.contact_person && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Contact Person
                    </label>
                    <p className="text-gray-900">{facility.contact_person}</p>
                  </div>
                )}

                {facility.contact_phone && (
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Contact Phone
                    </label>
                    <p className="text-gray-900">{facility.contact_phone}</p>
                  </div>
                )}

                {facility.contact_email && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-500 mb-1">
                      Contact Email
                    </label>
                    <p className="text-gray-900">
                      <a
                        href={`mailto:${facility.contact_email}`}
                        className="text-blue-600 hover:underline"
                      >
                        {facility.contact_email}
                      </a>
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              System Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Created At
                </label>
                <p className="text-gray-900">{formatDate(facility.created_at)}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Last Updated
                </label>
                <p className="text-gray-900">{formatDate(facility.updated_at)}</p>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
