/**
 * Centralized Error Handler
 * Provides consistent error handling across the application
 */

export enum ErrorType {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  NOT_FOUND = 'NOT_FOUND',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  UNKNOWN = 'UNKNOWN',
}

export interface AppError {
  type: ErrorType
  message: string
  details?: string
  statusCode?: number
  shouldLogout?: boolean
  retryable?: boolean
}

/**
 * Parse error from API response or exception
 */
export function parseError(error: any): AppError {
  // Network errors (no response)
  if (!error.response) {
    return {
      type: ErrorType.NETWORK_ERROR,
      message: 'Unable to connect to the server. Please check your internet connection.',
      details: error.message,
      retryable: true,
    }
  }

  const { status, data } = error.response

  // Handle different HTTP status codes
  switch (status) {
    case 401:
      return {
        type: ErrorType.AUTHENTICATION,
        message: 'Your session has expired. Please log in again.',
        statusCode: 401,
        shouldLogout: true,
      }

    case 403:
      return {
        type: ErrorType.AUTHORIZATION,
        message: 'You do not have permission to perform this action.',
        details: data?.detail || 'Access denied',
        statusCode: 403,
        shouldLogout: false,
      }

    case 404:
      return {
        type: ErrorType.NOT_FOUND,
        message: 'The requested resource was not found.',
        details: data?.detail,
        statusCode: 404,
        retryable: false,
      }

    case 422:
      return {
        type: ErrorType.VALIDATION,
        message: 'Please check your input and try again.',
        details: formatValidationErrors(data?.detail),
        statusCode: 422,
        retryable: false,
      }

    case 500:
    case 502:
    case 503:
      return {
        type: ErrorType.SERVER_ERROR,
        message: 'Something went wrong on our end. Please try again later.',
        details: data?.detail || 'Server error',
        statusCode: status,
        retryable: true,
      }

    default:
      return {
        type: ErrorType.UNKNOWN,
        message: data?.detail || 'An unexpected error occurred.',
        details: data?.message,
        statusCode: status,
        retryable: false,
      }
  }
}

/**
 * Format validation errors from FastAPI
 */
function formatValidationErrors(errors: any[]): string {
  if (!Array.isArray(errors)) return ''

  return errors
    .map((err) => {
      const field = err.loc?.join('.') || 'Field'
      return `${field}: ${err.msg}`
    })
    .join('\n')
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyMessage(error: AppError): string {
  return error.message
}

/**
 * Check if error should trigger logout
 */
export function shouldLogout(error: AppError): boolean {
  return error.shouldLogout || false
}

/**
 * Check if error is retryable
 */
export function isRetryable(error: AppError): boolean {
  return error.retryable || false
}

/**
 * Log error for debugging (can be sent to monitoring service)
 */
export function logError(error: AppError, context?: string) {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[Error ${context ? `in ${context}` : ''}]:`, {
      type: error.type,
      message: error.message,
      details: error.details,
      statusCode: error.statusCode,
    })
  }

  // In production, send to monitoring service (e.g., Sentry)
  // if (process.env.NODE_ENV === 'production') {
  //   sendToMonitoring(error, context)
  // }
}
