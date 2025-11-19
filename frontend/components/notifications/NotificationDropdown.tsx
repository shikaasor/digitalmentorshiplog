'use client'

import { useRouter } from 'next/navigation'
import { useNotificationsStore } from '@/lib/stores/notifications.store'
import { SpecialistNotification } from '@/types'

export default function NotificationDropdown() {
  const router = useRouter()
  const {
    notifications,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    closeDropdown,
  } = useNotificationsStore()

  const handleNotificationClick = async (notification: SpecialistNotification) => {
    // Mark as read if unread
    if (!notification.is_read) {
      await markAsRead([notification.id])
    }

    // Close dropdown and navigate to log
    closeDropdown()
    router.push(`/mentorship-logs/${notification.mentorship_log_id}`)
  }

  const handleMarkAllAsRead = async (e: React.MouseEvent) => {
    e.stopPropagation()
    await markAllAsRead()
  }

  const handleDelete = async (e: React.MouseEvent, notificationId: string) => {
    e.stopPropagation()
    if (confirm('Delete this notification?')) {
      await deleteNotification(notificationId)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) return 'Just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  const unreadNotifications = notifications.filter(n => !n.is_read)
  const hasUnread = unreadNotifications.length > 0

  return (
    <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-[100] max-h-[600px] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
          {hasUnread && (
            <button
              onClick={handleMarkAllAsRead}
              className="text-xs text-blue-600 hover:text-blue-700 font-medium"
            >
              Mark all as read
            </button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <div className="overflow-y-auto flex-1">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <svg
              className="animate-spin h-8 w-8 text-blue-600"
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
        ) : error ? (
          <div className="p-4 text-center text-red-600 text-sm">{error}</div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <p className="text-gray-500 text-sm">No notifications yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                onClick={() => handleNotificationClick(notification)}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors relative ${
                  !notification.is_read ? 'bg-blue-50' : ''
                }`}
              >
                {/* Unread Indicator */}
                {!notification.is_read && (
                  <div className="absolute left-2 top-1/2 -translate-y-1/2 w-2 h-2 bg-blue-600 rounded-full"></div>
                )}

                <div className="ml-3">
                  {/* Thematic Area Badge */}
                  <div className="mb-1">
                    <span className="inline-block px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
                      {notification.thematic_area}
                    </span>
                  </div>

                  {/* Message */}
                  <p className="text-sm text-gray-900 mb-1">
                    New mentorship log in your area of expertise
                  </p>

                  {/* Log Details */}
                  {notification.log_facility_name && (
                    <p className="text-xs text-gray-600 mb-1">
                      <span className="font-medium">Facility:</span>{' '}
                      {notification.log_facility_name}
                    </p>
                  )}

                  {notification.log_mentor_name && (
                    <p className="text-xs text-gray-600 mb-1">
                      <span className="font-medium">Mentor:</span>{' '}
                      {notification.log_mentor_name}
                    </p>
                  )}

                  {notification.log_visit_date && (
                    <p className="text-xs text-gray-600 mb-2">
                      <span className="font-medium">Visit Date:</span>{' '}
                      {new Date(notification.log_visit_date).toLocaleDateString()}
                    </p>
                  )}

                  {/* Footer */}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {formatDate(notification.notified_at)}
                    </span>

                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDelete(e, notification.id)}
                      className="text-xs text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {notifications.length > 0 && (
        <div className="p-3 border-t border-gray-200 text-center">
          <button
            onClick={() => {
              closeDropdown()
              // Could navigate to a full notifications page if you create one
              // router.push('/notifications')
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View all notifications
          </button>
        </div>
      )}
    </div>
  )
}
