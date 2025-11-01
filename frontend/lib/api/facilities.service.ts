/**
 * Facilities API Service
 */

import { apiClient } from './client'
import {
  Facility,
  FacilityCreate,
  FacilityUpdate,
  PaginatedResponse,
} from '@/types'

export interface FacilityFilters {
  state?: string
  facility_type?: string
  search?: string
  skip?: number
  limit?: number
}

export const facilitiesService = {
  /**
   * Get all facilities with filters
   */
  async getAll(filters?: FacilityFilters): Promise<PaginatedResponse<Facility>> {
    const params = new URLSearchParams()

    if (filters?.state) params.append('state', filters.state)
    if (filters?.facility_type) params.append('facility_type', filters.facility_type)
    if (filters?.search) params.append('search', filters.search)
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString())
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString())

    const response = await apiClient.get<PaginatedResponse<Facility>>(
      `/api/facilities?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get a single facility by ID
   */
  async getById(id: string): Promise<Facility> {
    const response = await apiClient.get<Facility>(`/api/facilities/${id}`)
    return response.data
  },

  /**
   * Create a new facility
   */
  async create(data: FacilityCreate): Promise<Facility> {
    const response = await apiClient.post<Facility>('/api/facilities', data)
    return response.data
  },

  /**
   * Update an existing facility
   */
  async update(id: string, data: FacilityUpdate): Promise<Facility> {
    const response = await apiClient.put<Facility>(`/api/facilities/${id}`, data)
    return response.data
  },

  /**
   * Delete a facility
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/facilities/${id}`)
  },
}
