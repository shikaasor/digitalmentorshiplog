/**
 * Follow-ups API Service
 */

import { apiClient } from './client'
import {
  FollowUp,
  FollowUpCreate,
  FollowUpUpdate,
  FollowUpStatus,
  PaginatedResponse,
} from '@/types'

export interface FollowUpFilters {
  status?: FollowUpStatus
  mentorship_log_id?: string
  assigned_to?: string
  priority?: string
  skip?: number
  limit?: number
}

export const followUpsService = {
  /**
   * Get all follow-ups with filters
   */
  async getAll(filters?: FollowUpFilters): Promise<PaginatedResponse<FollowUp>> {
    const params = new URLSearchParams()

    if (filters?.status) params.append('status', filters.status)
    if (filters?.mentorship_log_id) params.append('mentorship_log_id', filters.mentorship_log_id)
    if (filters?.assigned_to) params.append('assigned_to', filters.assigned_to)
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await apiClient.get<PaginatedResponse<FollowUp>>(
      `/api/follow-ups?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get a single follow-up by ID
   */
  async getById(id: string): Promise<FollowUp> {
    const response = await apiClient.get<FollowUp>(`/api/follow-ups/${id}`)
    return response.data
  },

  /**
   * Create a new follow-up
   */
  async create(followUpData: FollowUpCreate): Promise<FollowUp> {
    const response = await apiClient.post<FollowUp>('/api/follow-ups', followUpData)
    return response.data
  },

  /**
   * Update an existing follow-up
   */
  async update(id: string, followUpData: FollowUpUpdate): Promise<FollowUp> {
    const response = await apiClient.put<FollowUp>(`/api/follow-ups/${id}`, followUpData)
    return response.data
  },

  /**
   * Mark a follow-up as in progress
   */
  async markInProgress(id: string): Promise<FollowUp> {
    const response = await apiClient.put<FollowUp>(`/api/follow-ups/${id}/in-progress`)
    return response.data
  },

  /**
   * Mark a follow-up as completed
   */
  async markCompleted(id: string): Promise<FollowUp> {
    const response = await apiClient.put<FollowUp>(`/api/follow-ups/${id}/complete`)
    return response.data
  },

  /**
   * Delete a follow-up
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/follow-ups/${id}`)
  },
}
