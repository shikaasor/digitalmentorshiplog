/**
 * Reports API Service
 */

import { apiClient } from './client'
import { SummaryReport } from '@/types'

export const reportsService = {
  /**
   * Get summary report
   */
  async getSummary(): Promise<SummaryReport> {
    const response = await apiClient.get<SummaryReport>('/api/reports/summary')
    return response.data
  },
}
