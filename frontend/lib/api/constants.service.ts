/**
 * Constants API Service
 *
 * Fetches predefined constants from the backend to ensure consistency
 * between frontend and backend validation rules.
 */

import { apiClient } from './client'

export interface AppConstants {
  interaction_types: string[]
  states: string[]
  facility_types: string[]
  activity_types: string[]
  thematic_areas: string[]
  competency_levels: string[]
  transfer_methods: string[]
  priorities: string[]
  attachment_types: string[]
  cadres: string[]
}

export const constantsService = {
  /**
   * Get all application constants in a single request
   */
  async getAll(): Promise<AppConstants> {
    const response = await apiClient.get<AppConstants>('/api/constants/all')
    return response.data
  },

  /**
   * Get valid states (Kano, Jigawa, Bauchi)
   */
  async getStates(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/states')
    return response.data
  },

  /**
   * Get valid facility types (Primary, Secondary, Tertiary)
   */
  async getFacilityTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/facility-types')
    return response.data
  },

  /**
   * Get valid interaction types
   */
  async getInteractionTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/interaction-types')
    return response.data
  },

  /**
   * Get valid activity types
   */
  async getActivityTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/activity-types')
    return response.data
  },

  /**
   * Get valid thematic areas
   */
  async getThematicAreas(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/thematic-areas')
    return response.data
  },

  /**
   * Get valid competency levels
   */
  async getCompetencyLevels(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/competency-levels')
    return response.data
  },

  /**
   * Get valid transfer methods
   */
  async getTransferMethods(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/transfer-methods')
    return response.data
  },

  /**
   * Get valid priority levels
   */
  async getPriorities(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/priorities')
    return response.data
  },

  /**
   * Get valid attachment types
   */
  async getAttachmentTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/attachment-types')
    return response.data
  },

  /**
   * Get valid healthcare worker cadres
   */
  async getCadres(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/constants/cadres')
    return response.data
  },
}
