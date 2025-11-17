'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { facilitiesService } from '@/lib/api/facilities.service'
import { FacilityCreate } from '@/types'
import { STATES, FACILITY_TYPES } from '@/lib/constants'

export default function NewFacilityPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FacilityCreate>()

  const onSubmit = async (data: FacilityCreate) => {
    try {
      setLoading(true)
      setError(null)

      await facilitiesService.create(data)
      router.push('/facilities')
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to create facility')
    } finally {
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Page Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <button
              onClick={() => router.back()}
              className="hover:text-gray-900"
            >
              Facilities
            </button>
            <span>/</span>
            <span className="text-gray-900">New Facility</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Add New Facility</h1>
          <p className="mt-2 text-gray-600">
            Create a new healthcare facility in the system
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
              onClick={() => router.back()}
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
              {loading ? 'Creating...' : 'Create Facility'}
            </button>
          </div>
        </form>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
