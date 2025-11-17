/**
 * Comments API Service
 */

import { apiClient } from './client'

export interface LogComment {
  id: string
  mentorship_log_id: string
  user_id: string
  user_name: string
  user_role: string
  comment_text: string
  is_specialist_comment: boolean
  created_at: string
  updated_at: string
}

export interface LogCommentCreate {
  comment_text: string
  is_specialist_comment?: boolean
}

export interface LogCommentUpdate {
  comment_text: string
}

export const commentsService = {
  /**
   * Get all comments for a mentorship log
   */
  async getComments(logId: string): Promise<LogComment[]> {
    const response = await apiClient.get<LogComment[]>(
      `/api/mentorship-logs/${logId}/comments`
    )
    return response.data
  },

  /**
   * Add a comment to a mentorship log
   */
  async addComment(logId: string, data: LogCommentCreate): Promise<LogComment> {
    const response = await apiClient.post<LogComment>(
      `/api/mentorship-logs/${logId}/comments`,
      data
    )
    return response.data
  },

  /**
   * Update a comment
   */
  async updateComment(commentId: string, data: LogCommentUpdate): Promise<LogComment> {
    const response = await apiClient.put<LogComment>(
      `/api/mentorship-logs/comments/${commentId}`,
      data
    )
    return response.data
  },

  /**
   * Delete a comment
   */
  async deleteComment(commentId: string): Promise<void> {
    await apiClient.delete(`/api/mentorship-logs/comments/${commentId}`)
  },
}
