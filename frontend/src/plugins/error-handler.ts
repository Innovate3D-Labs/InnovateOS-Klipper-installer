import { App } from 'vue'
import { useErrorStore } from '@/store/error'
import { AxiosError } from 'axios'

interface ErrorResponse {
  error_code: string
  message: string
  details?: Record<string, any>
}

export class ErrorHandler {
  private static errorStore = useErrorStore()

  static install(app: App): void {
    app.config.errorHandler = (error: unknown, instance, info) => {
      console.error('Vue Error:', error)
      this.handleError(error)
    }

    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled Promise Rejection:', event.reason)
      this.handleError(event.reason)
    })

    window.addEventListener('error', (event) => {
      console.error('Global Error:', event.error)
      this.handleError(event.error)
    })
  }

  static handleError(error: unknown): void {
    if (error instanceof AxiosError) {
      this.handleApiError(error)
    } else if (error instanceof Error) {
      this.handleGenericError(error)
    } else {
      this.handleUnknownError(error)
    }
  }

  private static handleApiError(error: AxiosError<ErrorResponse>): void {
    const response = error.response?.data
    
    if (response) {
      switch (response.error_code) {
        case 'VALIDATION_ERROR':
          this.handleValidationError(response)
          break
        case 'BOARD_ERROR':
          this.handleBoardError(response)
          break
        case 'INSTALLATION_ERROR':
          this.handleInstallationError(response)
          break
        default:
          this.handleGenericApiError(response)
      }
    } else {
      this.errorStore.setError({
        type: 'network',
        message: 'Network error occurred',
        details: { status: error.status }
      })
    }
  }

  private static handleValidationError(response: ErrorResponse): void {
    this.errorStore.setError({
      type: 'validation',
      message: 'Validation error',
      details: response.details
    })
  }

  private static handleBoardError(response: ErrorResponse): void {
    this.errorStore.setError({
      type: 'board',
      message: response.message,
      details: response.details
    })
  }

  private static handleInstallationError(response: ErrorResponse): void {
    this.errorStore.setError({
      type: 'installation',
      message: response.message,
      details: response.details
    })
  }

  private static handleGenericApiError(response: ErrorResponse): void {
    this.errorStore.setError({
      type: 'api',
      message: response.message,
      details: response.details
    })
  }

  private static handleGenericError(error: Error): void {
    this.errorStore.setError({
      type: 'application',
      message: error.message,
      details: { stack: error.stack }
    })
  }

  private static handleUnknownError(error: unknown): void {
    this.errorStore.setError({
      type: 'unknown',
      message: 'An unexpected error occurred',
      details: { error }
    })
  }

  static clearError(): void {
    this.errorStore.clearError()
  }

  static isErrorActive(): boolean {
    return this.errorStore.hasError
  }
}

export default {
  install(app: App): void {
    ErrorHandler.install(app)
  }
}
