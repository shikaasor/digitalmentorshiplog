'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { mentorshipLogsService } from '@/lib/api/mentorship-logs.service'
import { attachmentsService } from '@/lib/api/attachments.service'
import { facilitiesService } from '@/lib/api/facilities.service'
import { MentorshipLogCreate, Facility, MenteesPresent, SkillsTransfer, FollowUpNested } from '@/types'
import { THEMATIC_AREAS } from '@/lib/constants/thematic-areas'

// Define checkbox options matching ACE2 PDF
const ACTIVITIES_OPTIONS = [
  'Direct clinical service',
  'Side-by-side mentorship',
  'Case review/discussion',
  'Data review and analysis',
  'Systems assessment/improvement',
  'Training/demonstration',
  'Meeting facilitation',
]

// Use backend constants for thematic areas (includes "Other" option)
const THEMATIC_AREAS_OPTIONS = THEMATIC_AREAS

const ATTACHMENT_TYPES_OPTIONS = [
  'Photos (with consent)',
  'Tools/Templates Shared',
  'Before/After Documentation',
  'Reference Materials',
]

const STATES = ['Kano', 'Jigawa', 'Bauchi']
const INTERACTION_TYPES = ['On-site', 'Virtual', 'Phone']
const PRIORITY_OPTIONS = ['High', 'Medium', 'Low']

export default function NewMentorshipLogPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [facilities, setFacilities] = useState<Facility[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<MentorshipLogCreate>({
    defaultValues: {
      mentees_present: [],
      activities_conducted: [],
      thematic_areas: [],
      attachment_types: [],
      skills_transfers: [],
      follow_ups: [],
    },
  })

  const {
    fields: menteesFields,
    append: appendMentee,
    remove: removeMentee,
  } = useFieldArray({
    control,
    name: 'mentees_present',
  })

  const {
    fields: skillsFields,
    append: appendSkill,
    remove: removeSkill,
  } = useFieldArray({
    control,
    name: 'skills_transfers',
  })

  const {
    fields: followUpFields,
    append: appendFollowUp,
    remove: removeFollowUp,
  } = useFieldArray({
    control,
    name: 'follow_ups',
  })

  // Load facilities on mount
  useEffect(() => {
    const loadFacilities = async () => {
      try {
        const response = await facilitiesService.getAll({ limit: 500 })
        setFacilities(response.items || [])
      } catch (err) {
        console.error('Failed to load facilities:', err)
      }
    }
    loadFacilities()
  }, [])

  const onSubmit = async (data: MentorshipLogCreate, shouldSubmit = false) => {
    try {
      setLoading(true)
      setError(null)

      // Create the mentorship log (as draft)
      const log = await mentorshipLogsService.create(data)

      // Upload files to the server if any
      if (uploadedFiles.length > 0) {
        try {
          await attachmentsService.upload(log.id, uploadedFiles)
        } catch (uploadErr: any) {
          // Log created successfully but file upload failed
          console.error('File upload failed:', uploadErr)
          setError(`Log created but file upload failed: ${uploadErr.message}`)
          // Still navigate to the log page so user can retry upload later
        }
      }

      // If shouldSubmit flag is true, submit for approval
      if (shouldSubmit) {
        await mentorshipLogsService.submit(log.id)
      }

      router.push(`/mentorship-logs/${log.id}`)
      router.refresh()
    } catch (err: any) {
      setError(err.message || 'Failed to create mentorship log')
    } finally {
      setLoading(false)
    }
  }

  const saveDraft = async () => {
    const data = watch()
    await onSubmit(data as MentorshipLogCreate, false) // Save as draft only
  }

  const submitForApproval = async () => {
    const data = watch()
    await onSubmit(data as MentorshipLogCreate, true) // Save and submit for approval
  }

  // Handle checkbox toggle for arrays
  const toggleArrayValue = (field: 'activities_conducted' | 'thematic_areas' | 'attachment_types', value: string) => {
    const currentValues = watch(field) || []
    if (currentValues.includes(value)) {
      setValue(
        field,
        currentValues.filter((v) => v !== value)
      )
    } else {
      setValue(field, [...currentValues, value])
    }
  }

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      const fileArray = Array.from(files)
      setUploadedFiles((prev) => [...prev, ...fileArray])
    }
  }

  // Remove uploaded file
  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">ACE2 Clinical Mentorship Log</h1>
          <p className="mt-2 text-gray-600">
            Document your mentorship visit and activities
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Header Information */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Visit Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Facility */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Facility Name <span className="text-red-500">*</span>
                </label>
                <select
                  {...register('facility_id', { required: 'Facility is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                >
                  <option value="">Select facility...</option>
                  {facilities.map((facility) => (
                    <option key={facility.id} value={facility.id}>
                      {facility.name} {facility.code ? `(${facility.code})` : ''}
                    </option>
                  ))}
                </select>
                {errors.facility_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.facility_id.message}</p>
                )}
              </div>

              {/* Visit Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  {...register('visit_date', { required: 'Visit date is required' })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
                {errors.visit_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.visit_date.message}</p>
                )}
              </div>

              {/* Interaction Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interaction Type
                </label>
                <div className="flex gap-4">
                  {INTERACTION_TYPES.map((type) => (
                    <label key={type} className="flex items-center">
                      <input
                        type="radio"
                        {...register('interaction_type')}
                        value={type}
                        className="mr-2"
                      />
                      {type}
                    </label>
                  ))}
                </div>
              </div>

              {/* Duration */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hours
                  </label>
                  <input
                    type="number"
                    min="0"
                    {...register('duration_hours', { valueAsNumber: true })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minutes
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="59"
                    {...register('duration_minutes', { valueAsNumber: true })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Mentees Present */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Mentees Present (Name & Cadre)
              </h2>
              <button
                type="button"
                onClick={() => appendMentee({ name: '', cadre: '' })}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Mentee
              </button>
            </div>

            {menteesFields.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No mentees added yet. Click "Add Mentee" to begin.
              </p>
            )}

            <div className="space-y-3">
              {menteesFields.map((field, index) => (
                <div key={field.id} className="flex gap-4 items-start">
                  <div className="flex-1">
                    <input
                      {...register(`mentees_present.${index}.name` as const)}
                      placeholder="Name"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                  </div>
                  <div className="flex-1">
                    <input
                      {...register(`mentees_present.${index}.cadre` as const)}
                      placeholder="Cadre (e.g., Nurse, Doctor, Lab Scientist)"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => removeMentee(index)}
                    className="px-3 py-2 text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Section 1: Activities Conducted */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              1. Activities Conducted
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {ACTIVITIES_OPTIONS.map((activity) => (
                <label key={activity} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={(watch('activities_conducted') || []).includes(activity)}
                    onChange={() => toggleArrayValue('activities_conducted', activity)}
                    className="mr-3 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{activity}</span>
                </label>
              ))}
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Other (specify)
              </label>
              <input
                {...register('activities_other_specify')}
                placeholder="Specify other activities..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Section 2: Thematic Areas Covered */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              2. Thematic Areas Covered
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {THEMATIC_AREAS_OPTIONS.map((area) => (
                <label key={area} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={(watch('thematic_areas') || []).includes(area)}
                    onChange={() => toggleArrayValue('thematic_areas', area)}
                    className="mr-3 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{area}</span>
                </label>
              ))}
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Other (specify)
              </label>
              <input
                {...register('thematic_areas_other_specify')}
                placeholder="Specify other thematic areas..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Section 3: Observations */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              3. Observations
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Strengths Observed
                </label>
                <textarea
                  rows={4}
                  {...register('strengths_observed')}
                  placeholder="Describe the strengths and positive practices you observed..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gaps Identified
                </label>
                <textarea
                  rows={4}
                  {...register('gaps_identified')}
                  placeholder="Describe any gaps, challenges, or areas for improvement..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Root Causes of Gaps
                </label>
                <textarea
                  rows={4}
                  {...register('root_causes')}
                  placeholder="Describe the root causes of identified gaps..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>
            </div>
          </div>

          {/* Section 4: Skills Transfer */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                4. Skills Transfer
              </h2>
              <button
                type="button"
                onClick={() =>
                  appendSkill({
                    skill_knowledge_transferred: '',
                    recipient_name: '',
                    recipient_cadre: '',
                    method: '',
                    competency_level: '',
                    followup_needed: false,
                  })
                }
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Skills Transfer
              </button>
            </div>

            {skillsFields.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No skills transfers added yet. Click "Add Skills Transfer" to begin.
              </p>
            )}

            <div className="space-y-4">
              {skillsFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-gray-900">Skills Transfer #{index + 1}</h3>
                    <button
                      type="button"
                      onClick={() => removeSkill(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Skill/Knowledge Transferred
                      </label>
                      <input
                        {...register(`skills_transfers.${index}.skill_knowledge_transferred` as const)}
                        placeholder="e.g., ART initiation protocol"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Recipient Name
                      </label>
                      <input
                        {...register(`skills_transfers.${index}.recipient_name` as const)}
                        placeholder="Name of recipient"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Recipient Cadre
                      </label>
                      <input
                        {...register(`skills_transfers.${index}.recipient_cadre` as const)}
                        placeholder="e.g., Nurse, Doctor"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Method
                      </label>
                      <input
                        {...register(`skills_transfers.${index}.method` as const)}
                        placeholder="e.g., Demonstration, Training"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Competency Level
                      </label>
                      <input
                        {...register(`skills_transfers.${index}.competency_level` as const)}
                        placeholder="e.g., Beginner, Intermediate, Advanced"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          {...register(`skills_transfers.${index}.followup_needed` as const)}
                          className="mr-3 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-gray-700">Follow-up Needed</span>
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 5: Action Items */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">5. Action Items</h2>
              <button
                type="button"
                onClick={() =>
                  appendFollowUp({
                    action_item: '',
                    responsible_person: '',
                    target_date: '',
                    resources_needed: '',
                    priority: '',
                    notes: '',
                  })
                }
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Action Item
              </button>
            </div>

            {followUpFields.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No action items added yet. Click "Add Action Item" to begin.
              </p>
            )}

            <div className="space-y-4">
              {followUpFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-gray-900">Action Item #{index + 1}</h3>
                    <button
                      type="button"
                      onClick={() => removeFollowUp(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Action Description
                      </label>
                      <textarea
                        rows={2}
                        {...register(`follow_ups.${index}.action_item` as const)}
                        placeholder="Describe the action item..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Responsible Person
                      </label>
                      <input
                        {...register(`follow_ups.${index}.responsible_person` as const)}
                        placeholder="Person responsible"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Date
                      </label>
                      <input
                        type="date"
                        {...register(`follow_ups.${index}.target_date` as const)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Resources Needed
                      </label>
                      <input
                        {...register(`follow_ups.${index}.resources_needed` as const)}
                        placeholder="Resources required"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Priority
                      </label>
                      <select
                        {...register(`follow_ups.${index}.priority` as const)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      >
                        <option value="">Select priority...</option>
                        {PRIORITY_OPTIONS.map((priority) => (
                          <option key={priority} value={priority}>
                            {priority}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Notes
                      </label>
                      <textarea
                        rows={2}
                        {...register(`follow_ups.${index}.notes` as const)}
                        placeholder="Additional notes..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 6: Challenges & Solutions */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              6. Challenges & Solutions
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Challenges Encountered
                </label>
                <textarea
                  rows={4}
                  {...register('challenges_encountered')}
                  placeholder="Describe any challenges encountered during the visit..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Solutions Implemented/Proposed
                </label>
                <textarea
                  rows={4}
                  {...register('solutions_proposed')}
                  placeholder="Describe solutions that were implemented or proposed..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Support Needed from Program Leadership
                </label>
                <textarea
                  rows={4}
                  {...register('support_needed')}
                  placeholder="Describe support needed from program leadership..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>
            </div>
          </div>

          {/* Section 7: Success Stories */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              7. Success Stories (Optional)
            </h2>
            <div>
              <textarea
                rows={6}
                {...register('success_stories')}
                placeholder="Share any success stories, positive outcomes, or notable achievements from this mentorship visit..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Section 8: Attachments */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              8. Attachments
            </h2>

            {/* Attachment Types Checkboxes */}
            <div className="mb-6">
              <p className="text-sm font-medium text-gray-700 mb-3">
                Select the types of attachments:
              </p>
              <div className="space-y-2">
                {ATTACHMENT_TYPES_OPTIONS.map((type) => (
                  <label key={type} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={(watch('attachment_types') || []).includes(type)}
                      onChange={() => toggleArrayValue('attachment_types', type)}
                      className="mr-3 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-gray-700">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* File Upload Widget */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Files
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                <input
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                  accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  <svg
                    className="w-12 h-12 text-gray-400 mb-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                  <span className="text-sm text-gray-600 mb-1">
                    Click to upload or drag and drop
                  </span>
                  <span className="text-xs text-gray-500">
                    Images, PDF, Word, Excel files (Max 10MB per file)
                  </span>
                </label>
              </div>

              {/* Uploaded Files List */}
              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-sm font-medium text-gray-700">
                    Uploaded Files ({uploadedFiles.length})
                  </p>
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <Image
                          src="/images/icon.png"
                          alt="File"
                          width={32}
                          height={32}
                          className="w-8 h-8 flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="ml-3 text-red-600 hover:text-red-800 flex-shrink-0"
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
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <p className="mt-2 text-xs text-gray-500">
                Note: Files will be uploaded when you submit the form
              </p>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-between bg-white rounded-xl border border-gray-200 p-6">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>

            <div className="flex gap-4">
              <button
                type="button"
                onClick={saveDraft}
                disabled={loading}
                className="px-6 py-2 border border-blue-600 text-blue-600 font-medium rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save as Draft
              </button>
              <button
                type="button"
                onClick={submitForApproval}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Submitting...' : 'Submit for Approval'}
              </button>
            </div>
          </div>
        </form>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
