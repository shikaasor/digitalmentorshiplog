'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useForm } from 'react-hook-form'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { facilitiesService } from '@/lib/api/facilities.service'
import { FacilityUpdate } from '@/types'
import { STATES, FACILITY_TYPES } from '@/lib/constants'

export default function EditFacilityPage() {
  const router = useRouter()
  const params = useParams()
  const facilityId = params.id as string

  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FacilityUpdate>()

  useEffect(() => {
    if (facilityId) {
      loadFacility()
    }
  }, [facilityId])

  const loadFacility = async () => {
    try {
      setInitialLoading(true)
      setError(null)
      const data = await facilitiesService.getById(facilityId)

      // Reset form with existing data
      reset({
        name: data.name,
        code: data.code,
        location: data.location,
        state: data.state,
        lga: data.lga,
        facility_type: data.facility_type,
        contact_person: data.contact_person,
        contact_email: data.contact_email,
        contact_phone: data.contact_phone,
      })
    } catch (err: any) {
      setError(err.message || 'Failed to load facility')
    } finally {
      setInitialLoading(false)
    }
  }

  const onSubmit = async (data: FacilityUpdate) => {
    try {
      setLoading(true)
      setError(null)

      await facilitiesService.update(facilityId, data)
      router.push(`/facilities/${facilityId}`)
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to update facility')
    } finally {
      setLoading(false)
    }
  }

  if (initialLoading) {
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

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <button
              onClick={() => router.push('/facilities')}
              className="hover:text-gray-900"
            >
              Facilities
            </button>
            <span>/</span>
            <button
              onClick={() => router.push(`/facilities/${facilityId}`)}
              className="hover:text-gray-900"
            >
              Facility
            </button>
            <span>/</span>
            <span className="text-gray-900">Edit</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Facility</h1>
          <p className="mt-2 text-gray-600">
            Update facility information
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
            {/* Basic Information */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Basic Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Facility Name */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Facility Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    {...register('name', { required: 'Facility name is required' })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter facility name"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                {/* Facility Code */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Facility Code
                  </label>
                  <input
                    type="text"
                    {...register('code')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="e.g., FAC001"
                  />
                </div>

                {/* Facility Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Facility Type
                  </label>
                  <select
                    {...register('facility_type')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select type</option>
                    {FACILITY_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Location Details */}
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Location Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Location/Address */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Address/Location
                  </label>
                  <textarea
                    {...register('location')}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter facility address"
                  />
                </div>

                {/* State */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State
                  </label>
                  <select
                    {...register('state')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    <option value="">Select state</option>
                    {STATES.map((state) => (
                      <option key={state} value={state}>
                        {state}
                      </option>
                    ))}
                  </select>
                </div>

                {/* LGA */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    LGA (Local Government Area)
                  </label>
                  <input
                    type="text"
                    {...register('lga')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter LGA"
                  />
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Contact Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Contact Person */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Person Name
                  </label>
                  <input
                    type="text"
                    {...register('contact_person')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Enter contact person name"
                  />
                </div>

                {/* Contact Phone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    {...register('contact_phone')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="e.g., +234 XXX XXX XXXX"
                  />
                </div>

                {/* Contact Email */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Email
                  </label>
                  <input
                    type="email"
                    {...register('contact_email')}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="contact@facility.com"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4 justify-end">
            <button
              type="button"
              onClick={() => router.push(`/facilities/${facilityId}`)}
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
