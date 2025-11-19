/**
 * Notifications API Service
 *
 * Handles all types of notifications: comments, approvals, rejections, specialist logs
 */

import { apiClient } from './client'
import { Notification, MarkNotificationReadRequest } from '@/types'

export const notificationsService = {
  /**
   * Get all notifications for the current user (unified format)
   * @param unreadOnly - If true, only return unread notifications
   */
  async getNotifications(unreadOnly: boolean = false): Promise<Notification[]> {
    const params = unreadOnly ? { unread_only: true } : {}
    const response = await apiClient.get<Notification[]>(
      '/api/notifications/',
      { params }
    )
    return response.data
  },

  /**
   * Get count of unread notifications
   */
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<{ unread_count: number }>(
      '/api/notifications/count'
    )
    return response.data.unread_count
  },

  /**
   * Mark specific notifications as read
   * @param notificationIds - Array of notification IDs to mark as read
   */
  async markAsRead(notificationIds: string[]): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/notifications/mark-read',
      { notification_ids: notificationIds }
    )
    return response.data
  },

  /**
   * Mark all notifications as read for the current user
   */
  async markAllAsRead(): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/notifications/mark-all-read'
    )
    return response.data
  },

  /**
   * Delete a notification
   * @param notificationId - ID of the notification to delete
   */
  async deleteNotification(notificationId: string): Promise<void> {
    await apiClient.delete(`/api/notifications/${notificationId}`)
  },
}
