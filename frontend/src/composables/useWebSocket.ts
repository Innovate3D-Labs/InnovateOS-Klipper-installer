import { ref } from 'vue'
import { WebSocketService } from '@/services/websocket'
import type { WebSocketMessage, WebSocketOptions } from '@/types'

let wsInstance: WebSocketService | null = null

export function useWebSocket(options: WebSocketOptions = {}) {
  const isConnected = ref(false)
  const lastError = ref<Error | null>(null)

  function getInstance(): WebSocketService {
    if (!wsInstance) {
      const url = import.meta.env.VITE_WS_URL
      wsInstance = new WebSocketService(url, options)

      // Set up connection status tracking
      wsInstance.onMessage(() => {
        isConnected.value = true
      })

      wsInstance.onError((error) => {
        isConnected.value = false
        lastError.value = error
      })
    }
    return wsInstance
  }

  async function connect(): Promise<void> {
    lastError.value = null
    try {
      await getInstance().connect()
      isConnected.value = true
    } catch (err) {
      isConnected.value = false
      lastError.value = err instanceof Error ? err : new Error('Connection failed')
      throw lastError.value
    }
  }

  function disconnect() {
    if (wsInstance) {
      wsInstance.disconnect()
      isConnected.value = false
    }
  }

  async function send(message: WebSocketMessage) {
    try {
      await getInstance().send(message)
    } catch (err) {
      lastError.value = err instanceof Error ? err : new Error('Send failed')
      throw lastError.value
    }
  }

  return {
    isConnected,
    lastError,
    connect,
    disconnect,
    send,
    onMessage: (callback: (data: any) => void) => getInstance().onMessage(callback),
    onInstallationStatus: (callback: (status: any) => void) => getInstance().onInstallationStatus(callback),
    onInstallationLog: (callback: (log: any) => void) => getInstance().onInstallationLog(callback),
    onError: (callback: (error: Error) => void) => getInstance().onError(callback)
  }
}
