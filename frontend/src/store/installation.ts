import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { apiClient } from '@/services/api'
import type { Board } from '@/types'

export const useInstallationStore = defineStore('installation', () => {
  // State
  const selectedBoard = ref<Board | null>(null)
  const installationId = ref<string | null>(null)
  const status = ref<string>('not_started')
  const progress = ref<number>(0)
  const currentStep = ref<string>('')
  const currentMessage = ref<string>('')
  const logs = ref<Array<{ timestamp: Date; level: string; message: string }>>([])
  const error = ref<Error | null>(null)

  // WebSocket
  const { sendMessage } = useWebSocket()

  // Computed
  const isInstalling = computed(() => status.value === 'installing')
  const isCompleted = computed(() => status.value === 'completed')
  const hasError = computed(() => status.value === 'error')

  // Actions
  const setBoard = (board: Board) => {
    selectedBoard.value = board
  }

  const setStatus = (newStatus: string) => {
    status.value = newStatus
  }

  const setProgress = (newProgress: number) => {
    progress.value = newProgress
  }

  const setStep = (step: string, message: string) => {
    currentStep.value = step
    currentMessage.value = message
  }

  const addLog = (level: string, message: string) => {
    logs.value.push({
      timestamp: new Date(),
      level,
      message
    })
  }

  const clearLogs = () => {
    logs.value = []
  }

  const startInstallation = async () => {
    try {
      if (!selectedBoard.value) {
        throw new Error('No board selected')
      }

      // Reset state
      status.value = 'starting'
      progress.value = 0
      error.value = null
      clearLogs()

      // Start installation
      const response = await apiClient.post('/api/installation/start', {
        board: selectedBoard.value,
        config: {} // Add configuration when needed
      })

      installationId.value = response.data.installation_id
      status.value = 'installing'

      // Subscribe to installation updates
      sendMessage({
        type: 'subscribe',
        installation_id: installationId.value
      })

      return true
    } catch (err) {
      error.value = err as Error
      status.value = 'error'
      return false
    }
  }

  const cancelInstallation = async () => {
    try {
      if (!installationId.value) {
        return true
      }

      await apiClient.post(`/api/installation/${installationId.value}/cancel`)
      status.value = 'cancelled'
      return true
    } catch (err) {
      error.value = err as Error
      return false
    }
  }

  const retryInstallation = async () => {
    error.value = null
    return startInstallation()
  }

  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'progress':
        progress.value = message.progress
        break
      case 'status':
        status.value = message.status
        break
      case 'step':
        setStep(message.step, message.message)
        break
      case 'log':
        addLog(message.level, message.message)
        break
      case 'error':
        error.value = new Error(message.message)
        status.value = 'error'
        break
      case 'complete':
        status.value = 'completed'
        progress.value = 100
        break
    }
  }

  const reset = () => {
    selectedBoard.value = null
    installationId.value = null
    status.value = 'not_started'
    progress.value = 0
    currentStep.value = ''
    currentMessage.value = ''
    error.value = null
    clearLogs()
  }

  return {
    // State
    selectedBoard,
    installationId,
    status,
    progress,
    currentStep,
    currentMessage,
    logs,
    error,

    // Computed
    isInstalling,
    isCompleted,
    hasError,

    // Actions
    setBoard,
    setStatus,
    setProgress,
    setStep,
    addLog,
    startInstallation,
    cancelInstallation,
    retryInstallation,
    handleWebSocketMessage,
    reset
  }
})
