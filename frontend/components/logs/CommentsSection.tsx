'use client'

import { useState, useEffect } from 'react'
import { commentsService, LogComment } from '@/lib/api/comments.service'
import { useAuthStore } from '@/lib/stores/auth.store'

interface CommentsSectionProps {
  logId: string
}

export default function CommentsSection({ logId }: CommentsSectionProps) {
  const { user } = useAuthStore()
  const [comments, setComments] = useState<LogComment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newComment, setNewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadComments()
  }, [logId])

  const loadComments = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await commentsService.getComments(logId)
      setComments(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load comments')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) return

    try {
      setSubmitting(true)
      setError(null)
      const comment = await commentsService.addComment(logId, {
        comment_text: newComment,
      })
      setComments([...comments, comment])
      setNewComment('')
    } catch (err: any) {
      setError(err.message || 'Failed to add comment')
    } finally {
      setSubmitting(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-700'
      case 'supervisor':
        return 'bg-blue-100 text-blue-700'
      case 'mentor':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Comments & Feedback
      </h2>

      {/* Error Alert */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Add Comment Form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment or feedback..."
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
          disabled={submitting}
        />
        <div className="mt-2 flex justify-end">
          <button
            type="submit"
            disabled={submitting || !newComment.trim()}
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
      </form>

      {/* Comments List */}
      {loading ? (
        <div className="flex justify-center py-8">
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
      ) : comments.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
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
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <p>No comments yet. Be the first to comment!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div
              key={comment.id}
              className="p-4 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">
                    {comment.user_name}
                  </span>
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded-full ${getRoleBadgeColor(
                      comment.user_role
                    )}`}
                  >
                    {comment.user_role.charAt(0).toUpperCase() +
                      comment.user_role.slice(1)}
                  </span>
                  {comment.is_specialist_comment && (
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-purple-100 text-purple-700">
                      Specialist
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(comment.created_at)}
                </span>
              </div>
              <p className="text-gray-900 whitespace-pre-wrap">
                {comment.comment_text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
