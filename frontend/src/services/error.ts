import type { AppError } from '@/types'

export class ErrorHandler {
  private static instance: ErrorHandler
  private errorListeners: ((error: AppError) => void)[] = []

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler()
    }
    return ErrorHandler.instance
  }

  // Register a global error listener
  onError(callback: (error: AppError) => void) {
    this.errorListeners.push(callback)
    return () => {
      const index = this.errorListeners.indexOf(callback)
      if (index > -1) {
        this.errorListeners.splice(index, 1)
      }
    }
  }

  // Handle and format errors
  handleError(error: unknown): AppError {
    const formattedError = this.formatError(error)
    this.notifyListeners(formattedError)
    return formattedError
  }

  // Format different types of errors into a consistent AppError
  private formatError(error: unknown): AppError {
    if (error instanceof Error) {
      return this.enhanceError(error)
    }

    if (typeof error === 'string') {
      return this.enhanceError(new Error(error))
    }

    return this.enhanceError(new Error('An unknown error occurred'))
  }

  // Enhance an error with additional properties
  private enhanceError(error: Error): AppError {
    const appError = error as AppError

    // Add timestamp
    appError.timestamp = new Date().toISOString()

    // Add error code if not present
    if (!appError.code) {
      appError.code = this.determineErrorCode(error)
    }

    // Add user-friendly message if not present
    if (!appError.message || appError.message === '[object Object]') {
      appError.message = this.getUserFriendlyMessage(appError.code)
    }

    return appError
  }

  // Determine error code based on error type and message
  private determineErrorCode(error: Error): string {
    if (error.name === 'NetworkError') return 'NETWORK_ERROR'
    if (error.name === 'TimeoutError') return 'TIMEOUT_ERROR'
    if (error.message.includes('WebSocket')) return 'WEBSOCKET_ERROR'
    if (error.message.includes('validation')) return 'VALIDATION_ERROR'
    if (error.message.includes('permission')) return 'PERMISSION_ERROR'
    return 'UNKNOWN_ERROR'
  }

  // Get user-friendly message based on error code
  private getUserFriendlyMessage(code: string): string {
    const messages: Record<string, string> = {
      NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
      TIMEOUT_ERROR: 'The request took too long to complete. Please try again.',
      WEBSOCKET_ERROR: 'Lost connection to the installation service. Attempting to reconnect...',
      VALIDATION_ERROR: 'The provided configuration is invalid. Please check your settings.',
      PERMISSION_ERROR: 'You don\'t have permission to perform this action.',
      UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.'
    }

    return messages[code] || messages.UNKNOWN_ERROR
  }

  // Notify all registered error listeners
  private notifyListeners(error: AppError) {
    this.errorListeners.forEach(listener => {
      try {
        listener(error)
      } catch (err) {
        console.error('Error in error listener:', err)
      }
    })
  }

  // Utility method to check if an error is retryable
  isRetryable(error: AppError): boolean {
    const retryableCodes = [
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'WEBSOCKET_ERROR'
    ]
    return retryableCodes.includes(error.code || '')
  }

  // Utility method to get retry delay based on attempt count
  getRetryDelay(attempt: number, baseDelay: number = 1000): number {
    return Math.min(baseDelay * Math.pow(2, attempt), 30000)
  }
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance()
