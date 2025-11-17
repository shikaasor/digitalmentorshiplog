/**
 * Mentorship Logs API Service
 */

import { apiClient } from './client'
import {
  MentorshipLog,
  MentorshipLogCreate,
  MentorshipLogUpdate,
  PaginatedResponse,
  LogStatus,
} from '@/types'

export interface MentorshipLogFilters {
  status?: LogStatus
  facility_id?: string
  mentor_id?: string
  date_from?: string
  date_to?: string
  skip?: number
  limit?: number
}

export const mentorshipLogsService = {
  /**
   * Get all mentorship logs with filters
   */
  async getAll(filters?: MentorshipLogFilters): Promise<PaginatedResponse<MentorshipLog>> {
    const params = new URLSearchParams()

    if (filters?.status) params.append('status', filters.status)
    if (filters?.facility_id) params.append('facility_id', filters.facility_id)
    if (filters?.mentor_id) params.append('mentor_id', filters.mentor_id)
    if (filters?.date_from) params.append('date_from', filters.date_from)
    if (filters?.date_to) params.append('date_to', filters.date_to)
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await apiClient.get<PaginatedResponse<MentorshipLog>>(
      `/api/mentorship-logs?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get a single mentorship log by ID
   */
  async getById(id: string): Promise<MentorshipLog> {
    const response = await apiClient.get<MentorshipLog>(`/api/mentorship-logs/${id}`)
    return response.data
  },

  /**
   * Create a new mentorship log
   */
  async create(data: MentorshipLogCreate): Promise<MentorshipLog> {
    const response = await apiClient.post<MentorshipLog>('/api/mentorship-logs', data)
    return response.data
  },

  /**
   * Update an existing mentorship log
   */
  async update(id: string, data: MentorshipLogUpdate): Promise<MentorshipLog> {
    const response = await apiClient.put<MentorshipLog>(`/api/mentorship-logs/${id}`, data)
    return response.data
  },

  /**
   * Delete a mentorship log
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/mentorship-logs/${id}`)
  },

  /**
   * Submit a log for approval (change status from draft to submitted)
   */
  async submit(id: string): Promise<MentorshipLog> {
    const response = await apiClient.post<MentorshipLog>(`/api/mentorship-logs/${id}/submit`)
    return response.data
  },

  /**
   * Approve a log (supervisor/admin only)
   */
  async approve(id: string): Promise<MentorshipLog> {
    const response = await apiClient.post<MentorshipLog>(`/api/mentorship-logs/${id}/approve`)
    return response.data
  },

  /**
   * Reject a log (supervisor/admin only)
   */
  async reject(id: string, reason: string): Promise<MentorshipLog> {
    const response = await apiClient.post<MentorshipLog>(`/api/mentorship-logs/${id}/reject`, {
      reason,
    })
    return response.data
  },
}
