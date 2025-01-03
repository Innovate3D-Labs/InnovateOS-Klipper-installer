import { defineStore } from 'pinia'
import { websocketService, installationEvents } from '@/services/websocket'
import type { Board, PrinterConfig, InstallationStatus, ErrorInfo } from '@/types'

interface State {
  selectedBoard: Board | null
  printerConfig: PrinterConfig | null
  installationStatus: InstallationStatus
  installationProgress: number
  currentStep: string
  errors: ErrorInfo[]
  wsConnected: boolean
}

export const useMainStore = defineStore('main', {
  state: (): State => ({
    selectedBoard: null,
    printerConfig: null,
    installationStatus: 'not_started',
    installationProgress: 0,
    currentStep: '',
    errors: [],
    wsConnected: false
  }),

  getters: {
    isConfigurationComplete: (state) => {
      return state.selectedBoard !== null && state.printerConfig !== null
    },
    
    canProceedToInstallation: (state) => {
      return state.selectedBoard !== null && 
             state.printerConfig !== null && 
             state.errors.filter(e => e.severity === 'critical').length === 0
    },
    
    currentErrors: (state) => {
      return state.errors
    }
  },

  actions: {
    // Board and Config Actions
    setSelectedBoard(board: Board) {
      this.selectedBoard = board
    },

    setPrinterConfig(config: PrinterConfig) {
      this.printerConfig = config
    },

    // Installation Progress Actions
    updateInstallationProgress(progress: number, step: string) {
      this.installationProgress = progress
      this.currentStep = step
    },

    setInstallationStatus(status: InstallationStatus) {
      this.installationStatus = status
    },

    // Error Management
    addError(error: ErrorInfo) {
      this.errors.push({
        ...error,
        id: Date.now().toString()
      })
    },

    removeError(errorId: string) {
      this.errors = this.errors.filter(error => error.id !== errorId)
    },

    clearErrors() {
      this.errors = []
    },

    // WebSocket Management
    async initializeWebSocket() {
      try {
        await websocketService.connect()
        this.wsConnected = true
        this.setupWebSocketListeners()
      } catch (error: any) {
        this.addError({
          title: 'Connection Error',
          message: 'Failed to connect to installation service',
          severity: 'critical',
          details: error.message
        })
      }
    },

    setupWebSocketListeners() {
      installationEvents.onProgress(({ progress, status, currentStep }) => {
        this.installationProgress = progress
        this.installationStatus = status
        this.currentStep = currentStep
      })

      installationEvents.onError(({ message, details }) => {
        this.addError({
          title: 'Installation Error',
          message,
          details,
          severity: 'critical'
        })
      })

      installationEvents.onComplete(({ success, message }) => {
        this.installationStatus = success ? 'completed' : 'failed'
        if (!success) {
          this.addError({
            title: 'Installation Failed',
            message,
            severity: 'critical'
          })
        }
      })
    },

    disconnectWebSocket() {
      websocketService.disconnect()
      this.wsConnected = false
    },

    // Reset State
    resetState() {
      this.selectedBoard = null
      this.printerConfig = null
      this.installationStatus = 'not_started'
      this.installationProgress = 0
      this.currentStep = ''
      this.errors = []
      if (this.wsConnected) {
        this.disconnectWebSocket()
      }
    }
  }
})
