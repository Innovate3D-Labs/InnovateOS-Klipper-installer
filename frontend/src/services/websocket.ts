import type { WebSocketMessage, WebSocketOptions, InstallationStatus, InstallationLog } from '@/types'

export class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private options: Required<WebSocketOptions>
  private reconnectTimer: number | null = null
  private messageQueue: WebSocketMessage[] = []
  private retryCount: number = 0
  private listeners: {
    message: ((data: any) => void)[]
    status: ((status: InstallationStatus) => void)[]
    log: ((log: InstallationLog) => void)[]
    error: ((error: Error) => void)[]
  } = {
    message: [],
    status: [],
    log: [],
    error: []
  }

  constructor(url: string, options: WebSocketOptions = {}) {
    this.url = url
    this.options = {
      reconnectInterval: options.reconnectInterval || 1000,
      maxRetries: options.maxRetries || 5,
      debug: options.debug || false
    }
  }

  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          this.log('WebSocket connected')
          this.retryCount = 0
          this.flushMessageQueue()
          resolve()
        }

        this.ws.onclose = (event) => {
          this.log(`WebSocket closed: ${event.code} ${event.reason}`)
          this.handleDisconnect()
        }

        this.ws.onerror = (event) => {
          const error = new Error('WebSocket error')
          this.notifyError(error)
          reject(error)
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (err) {
            this.log('Failed to parse WebSocket message:', err)
          }
        }

      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to create WebSocket')
        this.notifyError(error)
        reject(error)
      }
    })
  }

  disconnect() {
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  async send(message: WebSocketMessage): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.messageQueue.push(message)
      await this.connect()
      return
    }

    try {
      this.ws.send(JSON.stringify(message))
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to send message')
      this.notifyError(error)
      throw error
    }
  }

  // Event listeners
  onMessage(callback: (data: any) => void) {
    this.listeners.message.push(callback)
    return () => {
      const index = this.listeners.message.indexOf(callback)
      if (index > -1) {
        this.listeners.message.splice(index, 1)
      }
    }
  }

  onInstallationStatus(callback: (status: InstallationStatus) => void) {
    this.listeners.status.push(callback)
    return () => {
      const index = this.listeners.status.indexOf(callback)
      if (index > -1) {
        this.listeners.status.splice(index, 1)
      }
    }
  }

  onInstallationLog(callback: (log: InstallationLog) => void) {
    this.listeners.log.push(callback)
    return () => {
      const index = this.listeners.log.indexOf(callback)
      if (index > -1) {
        this.listeners.log.splice(index, 1)
      }
    }
  }

  onError(callback: (error: Error) => void) {
    this.listeners.error.push(callback)
    return () => {
      const index = this.listeners.error.indexOf(callback)
      if (index > -1) {
        this.listeners.error.splice(index, 1)
      }
    }
  }

  // Private methods
  private handleMessage(message: WebSocketMessage) {
    this.log('Received message:', message)

    // Notify general message listeners
    this.listeners.message.forEach(callback => callback(message))

    // Handle specific message types
    switch (message.type) {
      case 'installation_status':
        this.listeners.status.forEach(callback => callback(message.data))
        break
      case 'installation_log':
        this.listeners.log.forEach(callback => callback(message.data))
        break
      default:
        this.log('Unknown message type:', message.type)
    }
  }

  private handleDisconnect() {
    if (this.retryCount >= this.options.maxRetries) {
      this.notifyError(new Error('Max reconnection attempts reached'))
      return
    }

    this.retryCount++
    this.reconnectTimer = window.setTimeout(() => {
      this.log(`Reconnecting... Attempt ${this.retryCount}`)
      this.connect().catch(error => {
        this.log('Reconnection failed:', error)
      })
    }, this.options.reconnectInterval * Math.pow(2, this.retryCount - 1))
  }

  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      if (message) {
        this.send(message).catch(error => {
          this.log('Failed to send queued message:', error)
        })
      }
    }
  }

  private notifyError(error: Error) {
    this.log('WebSocket error:', error)
    this.listeners.error.forEach(callback => callback(error))
  }

  private log(...args: any[]) {
    if (this.options.debug) {
      console.log('[WebSocket]', ...args)
    }
  }
}
