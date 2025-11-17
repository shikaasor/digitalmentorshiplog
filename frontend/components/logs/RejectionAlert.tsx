/**
 * Rejection Alert Component
 * Shows a prominent alert when a log has been rejected
 */

interface RejectionAlertProps {
  rejectedAt: string
  rejectionReason?: string
}

export default function RejectionAlert({ rejectedAt, rejectionReason }: RejectionAlertProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-lg">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-semibold text-red-800">
            This log was returned for revision
          </h3>
          <p className="text-xs text-red-700 mt-1">
            Returned on {formatDate(rejectedAt)}
          </p>
          {rejectionReason && (
            <div className="mt-3 p-3 bg-white rounded border border-red-200">
              <p className="text-sm font-medium text-red-900 mb-1">Reason for return:</p>
              <p className="text-sm text-red-800 whitespace-pre-wrap">{rejectionReason}</p>
            </div>
          )}
          <div className="mt-3 text-sm text-red-800">
            <p className="font-medium">What to do next:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Review the feedback above</li>
              <li>Make the necessary corrections</li>
              <li>Resubmit your log for approval</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
