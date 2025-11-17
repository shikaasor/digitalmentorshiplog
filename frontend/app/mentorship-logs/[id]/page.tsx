'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import RejectionAlert from '@/components/logs/RejectionAlert'
import CommentsSection from '@/components/logs/CommentsSection'
import { mentorshipLogsService } from '@/lib/api/mentorship-logs.service'
import { MentorshipLog, LogStatus } from '@/types'
import { usePermissions } from '@/lib/hooks/usePermissions'

export default function ViewMentorshipLogPage() {
  const router = useRouter()
  const params = useParams()
  const { canApproveLogs, canRejectLogs } = usePermissions()
  const [log, setLog] = useState<MentorshipLog | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const logId = params.id as string

  useEffect(() => {
    if (logId) {
      loadLog()
    }
  }, [logId])

  const loadLog = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await mentorshipLogsService.getById(logId)
      setLog(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load mentorship log')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this log?')) return

    try {
      await mentorshipLogsService.delete(logId)
      router.push('/mentorship-logs')
    } catch (err: any) {
      setError(err.message || 'Failed to delete log')
    }
  }

  const handleApprove = async () => {
    if (!confirm('Are you sure you want to approve this log?')) return

    try {
      const updated = await mentorshipLogsService.approve(logId)
      setLog(updated)
    } catch (err: any) {
      setError(err.message || 'Failed to approve log')
    }
  }

  const handleReject = async () => {
    const reason = prompt('Please provide a reason for rejection:')
    if (!reason) return

    try {
      const updated = await mentorshipLogsService.reject(logId, reason)
      setLog(updated)
    } catch (err: any) {
      setError(err.message || 'Failed to reject log')
    }
  }

  const getStatusBadgeColor = (status: LogStatus) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-700'
      case 'submitted':
        return 'bg-yellow-100 text-yellow-700'
      case 'approved':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  // A log can be edited if it's in draft status (includes rejected logs which are set back to draft)
  const canEdit = log && log.status === LogStatus.DRAFT
  const canApprove = log && log.status === LogStatus.SUBMITTED && canApproveLogs
  const canReject = log && log.status === LogStatus.SUBMITTED && canRejectLogs

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

  if (error || !log) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error || 'Log not found'}
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Link
                href="/mentorship-logs"
                className="text-gray-600 hover:text-gray-800"
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
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">ACE2 Clinical Mentorship Log</h1>
            </div>
            <p className="text-gray-600">
              Visit on {formatDate(log.visit_date)}
            </p>
          </div>

          <div className="flex gap-3">
            {canEdit && (
              <Link
                href={`/mentorship-logs/${logId}/edit`}
                className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Log
              </Link>
            )}
            {canApprove && (
              <>
                <button
                  onClick={handleApprove}
                  className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  Approve
                </button>
                <button
                  onClick={handleReject}
                  className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  Reject
                </button>
              </>
            )}
            <button
              onClick={handleDelete}
              className="px-4 py-2 border border-red-600 text-red-600 font-medium rounded-lg hover:bg-red-50 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Status Badge */}
        <div className="mb-6">
          <span
            className={`inline-block px-4 py-2 text-sm font-medium rounded-full ${getStatusBadgeColor(
              log.status
            )}`}
          >
            {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
          </span>
        </div>

        {/* Rejection Alert - Show if log was rejected */}
        {log.rejected_at && (
          <RejectionAlert
            rejectedAt={log.rejected_at}
            rejectionReason={log.rejection_reason}
          />
        )}

        {/* Visit Information */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Visit Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Facility Name
              </label>
              {log.facility ? (
                <Link
                  href={`/facilities/${log.facility_id}`}
                  className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                >
                  {log.facility.name}
                </Link>
              ) : (
                <p className="text-gray-900">N/A</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Mentor
              </label>
              <p className="text-gray-900">{log.mentor?.name || 'N/A'}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Visit Date
              </label>
              <p className="text-gray-900">{formatDate(log.visit_date)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Interaction Type
              </label>
              <p className="text-gray-900 capitalize">
                {log.interaction_type || 'N/A'}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Duration
              </label>
              <p className="text-gray-900">
                {log.duration_hours || 0}h {log.duration_minutes || 0}m
              </p>
            </div>
          </div>
        </div>

        {/* Mentees Present */}
        {log.mentees_present && log.mentees_present.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Mentees Present ({log.mentees_present.length})
            </h2>
            <div className="space-y-2">
              {log.mentees_present.map((mentee: any, index: number) => (
                <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-900">{mentee.name}</span>
                  {mentee.cadre && (
                    <span className="text-sm text-gray-600">({mentee.cadre})</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Section 1: Activities Conducted */}
        {(log.activities_conducted && log.activities_conducted.length > 0) || log.activities_other_specify && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              1. Activities Conducted
            </h2>
            {log.activities_conducted && log.activities_conducted.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {log.activities_conducted.map((activity: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                    >
                      {activity}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {log.activities_other_specify && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Other Activities
                </label>
                <p className="text-gray-900">{log.activities_other_specify}</p>
              </div>
            )}
          </div>
        )}

        {/* Section 2: Thematic Areas Covered */}
        {(log.thematic_areas && log.thematic_areas.length > 0) || log.thematic_areas_other_specify && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              2. Thematic Areas Covered
            </h2>
            {log.thematic_areas && log.thematic_areas.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {log.thematic_areas.map((area: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                    >
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {log.thematic_areas_other_specify && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Other Thematic Areas
                </label>
                <p className="text-gray-900">{log.thematic_areas_other_specify}</p>
              </div>
            )}
          </div>
        )}

        {/* Section 3: Observations */}
        {(log.strengths_observed || log.gaps_identified || log.root_causes) && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              3. Observations
            </h2>
            <div className="space-y-4">
              {log.strengths_observed && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Strengths Observed
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.strengths_observed}
                  </p>
                </div>
              )}

              {log.gaps_identified && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Gaps Identified
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.gaps_identified}
                  </p>
                </div>
              )}

              {log.root_causes && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Root Causes of Gaps
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.root_causes}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Section 4: Skills Transfer */}
        {log.skills_transfers && log.skills_transfers.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              4. Skills Transfer ({log.skills_transfers.length})
            </h2>
            <div className="space-y-4">
              {log.skills_transfers.map((skill: any, index: number) => (
                <div
                  key={skill.id || index}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Skill/Knowledge Transferred
                      </label>
                      <p className="text-gray-900">{skill.skill_knowledge_transferred || 'N/A'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Recipient Name
                      </label>
                      <p className="text-gray-900">{skill.recipient_name || 'N/A'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Recipient Cadre
                      </label>
                      <p className="text-gray-900">{skill.recipient_cadre || 'N/A'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Method
                      </label>
                      <p className="text-gray-900">{skill.method || 'N/A'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Competency Level
                      </label>
                      <p className="text-gray-900">{skill.competency_level || 'N/A'}</p>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-500 mb-1">
                        Follow-up Needed
                      </label>
                      <p className="text-gray-900">
                        {skill.followup_needed ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Section 5: Action Items / Follow-Ups */}
        {log.follow_ups && log.follow_ups.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              5. Action Items ({log.follow_ups.length})
            </h2>
            <div className="space-y-4">
              {log.follow_ups.map((followUp: any, index: number) => (
                <div
                  key={followUp.id || index}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <p className="text-gray-900 font-medium">
                      {followUp.action_item}
                    </p>
                    <span
                      className={`px-3 py-1 text-xs font-medium rounded-full ${
                        followUp.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : followUp.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {followUp.status?.replace('_', ' ') || 'Pending'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {followUp.responsible_person && (
                      <div>
                        <span className="text-gray-500">Responsible Person: </span>
                        <span className="text-gray-900">
                          {followUp.responsible_person}
                        </span>
                      </div>
                    )}

                    {followUp.target_date && (
                      <div>
                        <span className="text-gray-500">Target Date: </span>
                        <span className="text-gray-900">
                          {formatDate(followUp.target_date)}
                        </span>
                      </div>
                    )}

                    {followUp.resources_needed && (
                      <div className="md:col-span-2">
                        <span className="text-gray-500">Resources Needed: </span>
                        <span className="text-gray-900">
                          {followUp.resources_needed}
                        </span>
                      </div>
                    )}

                    {followUp.priority && (
                      <div>
                        <span className="text-gray-500">Priority: </span>
                        <span className={`font-medium ${
                          followUp.priority === 'High' ? 'text-red-600' :
                          followUp.priority === 'Medium' ? 'text-yellow-600' :
                          'text-green-600'
                        }`}>
                          {followUp.priority}
                        </span>
                      </div>
                    )}

                    {followUp.notes && (
                      <div className="md:col-span-2">
                        <span className="text-gray-500">Notes: </span>
                        <span className="text-gray-900">{followUp.notes}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Section 6: Challenges & Solutions */}
        {(log.challenges_encountered || log.solutions_proposed || log.support_needed) && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              6. Challenges & Solutions
            </h2>
            <div className="space-y-4">
              {log.challenges_encountered && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Challenges Encountered
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.challenges_encountered}
                  </p>
                </div>
              )}

              {log.solutions_proposed && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Solutions Implemented/Proposed
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.solutions_proposed}
                  </p>
                </div>
              )}

              {log.support_needed && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-2">
                    Support Needed from Program Leadership
                  </label>
                  <p className="text-gray-900 whitespace-pre-wrap">
                    {log.support_needed}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Section 7: Success Stories */}
        {log.success_stories && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              7. Success Stories
            </h2>
            <p className="text-gray-900 whitespace-pre-wrap">
              {log.success_stories}
            </p>
          </div>
        )}

        {/* Section 8: Attachments */}
        {((log.attachment_types && log.attachment_types.length > 0) || (log.attachments && log.attachments.length > 0)) && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              8. Attachments
            </h2>

            {log.attachment_types && log.attachment_types.length > 0 && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-500 mb-2">
                  Attachment Types
                </label>
                <div className="flex flex-wrap gap-2">
                  {log.attachment_types.map((type: string, index: number) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {log.attachments && log.attachments.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-2">
                  Files ({log.attachments.length})
                </label>
                <div className="space-y-2">
                  {log.attachments.map((attachment: any) => (
                    <div
                      key={attachment.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div className="flex items-center gap-3">
                        <Image
                          src="/images/icon.png"
                          alt="File"
                          width={32}
                          height={32}
                          className="w-8 h-8"
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {attachment.file_name}
                          </p>
                          {attachment.file_size && (
                            <p className="text-xs text-gray-500">
                              {(attachment.file_size / 1024).toFixed(2)} KB
                            </p>
                          )}
                        </div>
                      </div>
                      <a
                        href={attachment.file_path}
                        download
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Download
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Metadata */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Metadata</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Created: </span>
              <span className="text-gray-900">
                {formatDate(log.created_at)}
              </span>
            </div>

            <div>
              <span className="text-gray-500">Last Updated: </span>
              <span className="text-gray-900">
                {formatDate(log.updated_at)}
              </span>
            </div>

            <div>
              <span className="text-gray-500">Created By: </span>
              <span className="text-gray-900">
                {log.mentor?.name || 'N/A'}
              </span>
            </div>

            {log.approver && (
              <div>
                <span className="text-gray-500">Approved By: </span>
                <span className="text-gray-900">{log.approver.name}</span>
              </div>
            )}
          </div>
        </div>

        {/* Comments Section */}
        <CommentsSection logId={logId} />
      </DashboardLayout>
    </ProtectedRoute>
  )
}
