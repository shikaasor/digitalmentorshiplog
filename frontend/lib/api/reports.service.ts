/**
 * Reports API Service
 */

import { apiClient } from './client'
import {
  SummaryReport,
  MentorshipLogsReport,
  FollowUpsReport,
  FacilityCoverageReport,
  LogStatus,
  FollowUpStatus,
} from '@/types'

export interface MentorshipLogsReportFilters {
  start_date?: string
  end_date?: string
  mentor_id?: string
  facility_id?: string
  status?: LogStatus
}

export interface FollowUpsReportFilters {
  status?: FollowUpStatus
  priority?: string
}

export interface FacilityCoverageFilters {
  state?: string
}

export const reportsService = {
  /**
   * Get summary report with overall statistics
   */
  async getSummary(): Promise<SummaryReport> {
    const response = await apiClient.get<SummaryReport>('/api/reports/summary')
    return response.data
  },

  /**
   * Get mentorship logs report with optional filters
   */
  async getMentorshipLogsReport(
    filters?: MentorshipLogsReportFilters
  ): Promise<MentorshipLogsReport> {
    const params = new URLSearchParams()

    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    if (filters?.mentor_id) params.append('mentor_id', filters.mentor_id)
    if (filters?.facility_id) params.append('facility_id', filters.facility_id)
    if (filters?.status) params.append('status', filters.status)

    const queryString = params.toString()
    const url = queryString
      ? `/api/reports/mentorship-logs?${queryString}`
      : '/api/reports/mentorship-logs'

    const response = await apiClient.get<MentorshipLogsReport>(url)
    return response.data
  },

  /**
   * Get follow-ups report with optional filters
   */
  async getFollowUpsReport(
    filters?: FollowUpsReportFilters
  ): Promise<FollowUpsReport> {
    const params = new URLSearchParams()

    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)

    const queryString = params.toString()
    const url = queryString
      ? `/api/reports/follow-ups?${queryString}`
      : '/api/reports/follow-ups'

    const response = await apiClient.get<FollowUpsReport>(url)
    return response.data
  },

  /**
   * Get facility coverage report with optional filters
   */
  async getFacilityCoverageReport(
    filters?: FacilityCoverageFilters
  ): Promise<FacilityCoverageReport> {
    const params = new URLSearchParams()

    if (filters?.state) params.append('state', filters.state)

    const queryString = params.toString()
    const url = queryString
      ? `/api/reports/facility-coverage?${queryString}`
      : '/api/reports/facility-coverage'

    const response = await apiClient.get<FacilityCoverageReport>(url)
    return response.data
  },
}
