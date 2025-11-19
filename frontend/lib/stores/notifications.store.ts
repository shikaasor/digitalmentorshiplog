/**
 * Notifications Store
 *
 * Zustand store for managing specialist notifications
 */

import { create } from 'zustand'
import { SpecialistNotification } from '@/types'
import { notificationsService } from '../api/notifications.service'
import { toast } from './toast.store'
import { handleApiError } from '../api/client'

interface NotificationsState {
  notifications: SpecialistNotification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
  isOpen: boolean // For dropdown state

  // Actions
  fetchNotifications: (unreadOnly?: boolean) => Promise<void>
  fetchUnreadCount: () => Promise<void>
  markAsRead: (notificationIds: string[]) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (notificationId: string) => Promise<void>
  toggleDropdown: () => void
  closeDropdown: () => void
  clearError: () => void
}

export const useNotificationsStore = create<NotificationsState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
  isOpen: false,

  /**
   * Fetch notifications
   */
  fetchNotifications: async (unreadOnly: boolean = false) => {
    set({ isLoading: true, error: null })
    try {
      const notifications = await notificationsService.getNotifications(unreadOnly)
      set({
        notifications,
        isLoading: false,
        unreadCount: notifications.filter(n => !n.is_read).length
      })
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      set({ error: errorMessage, isLoading: false })
      console.error('Failed to fetch notifications:', errorMessage)
    }
  },

  /**
   * Fetch unread count only (lightweight)
   */
  fetchUnreadCount: async () => {
    try {
      const count = await notificationsService.getUnreadCount()
      set({ unreadCount: count })
    } catch (error: any) {
      console.error('Failed to fetch unread count:', handleApiError(error))
    }
  },

  /**
   * Mark notifications as read
   */
  markAsRead: async (notificationIds: string[]) => {
    try {
      await notificationsService.markAsRead(notificationIds)

      // Update local state
      const { notifications } = get()
      const updatedNotifications = notifications.map(notification =>
        notificationIds.includes(notification.id)
          ? { ...notification, is_read: true, read_at: new Date().toISOString() }
          : notification
      )

      set({
        notifications: updatedNotifications,
        unreadCount: updatedNotifications.filter(n => !n.is_read).length
      })
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      toast.error('Failed to mark as read', errorMessage)
      throw error
    }
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async () => {
    try {
      await notificationsService.markAllAsRead()

      // Update local state
      const { notifications } = get()
      const updatedNotifications = notifications.map(notification => ({
        ...notification,
        is_read: true,
        read_at: new Date().toISOString()
      }))

      set({
        notifications: updatedNotifications,
        unreadCount: 0
      })

      toast.success('All notifications marked as read')
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      toast.error('Failed to mark all as read', errorMessage)
      throw error
    }
  },

  /**
   * Delete a notification
   */
  deleteNotification: async (notificationId: string) => {
    try {
      await notificationsService.deleteNotification(notificationId)

      // Remove from local state
      const { notifications } = get()
      const updatedNotifications = notifications.filter(n => n.id !== notificationId)

      set({
        notifications: updatedNotifications,
        unreadCount: updatedNotifications.filter(n => !n.is_read).length
      })

      toast.success('Notification deleted')
    } catch (error: any) {
      const errorMessage = handleApiError(error)
      toast.error('Failed to delete notification', errorMessage)
      throw error
    }
  },

  /**
   * Toggle dropdown open/close
   */
  toggleDropdown: () => {
    const { isOpen } = get()
    set({ isOpen: !isOpen })

    // Fetch notifications when opening
    if (!isOpen) {
      get().fetchNotifications()
    }
  },

  /**
   * Close dropdown
   */
  closeDropdown: () => {
    set({ isOpen: false })
  },

  /**
   * Clear error message
   */
  clearError: () => {
    set({ error: null })
  },
}))
