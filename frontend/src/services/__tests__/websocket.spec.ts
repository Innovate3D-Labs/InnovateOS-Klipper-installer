import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { WebSocketService } from '../websocket'
import { ref } from 'vue'

// Mock WebSocket
class MockWebSocket {
  url: string
  onopen: Function | null = null
  onclose: Function | null = null
  onmessage: Function | null = null
  onerror: Function | null = null
  readyState: number = WebSocket.CONNECTING

  constructor(url: string) {
    this.url = url
  }

  send(data: string) {
    // Mock implementation
  }

  close() {
    this.readyState = WebSocket.CLOSED
    if (this.onclose) {
      this.onclose({ code: 1000, reason: 'Normal closure' })
    }
  }

  // Helper methods for testing
  simulateOpen() {
    this.readyState = WebSocket.OPEN
    if (this.onopen) {
      this.onopen({ type: 'open' })
    }
  }

  simulateMessage(data: any) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) })
    }
  }

  simulateError(error: Error) {
    if (this.onerror) {
      this.onerror({ error })
    }
  }
}

// Mock window.WebSocket
vi.stubGlobal('WebSocket', MockWebSocket)

describe('WebSocketService', () => {
  let wsService: WebSocketService
  let mockWs: MockWebSocket

  beforeEach(() => {
    wsService = new WebSocketService('ws://localhost:8000/ws')
    mockWs = (wsService as any).ws
  })

  afterEach(() => {
    wsService.disconnect()
    vi.clearAllMocks()
  })

  it('should connect to WebSocket server', async () => {
    const connectSpy = vi.spyOn(wsService, 'connect')
    
    await wsService.connect()
    mockWs.simulateOpen()

    expect(connectSpy).toHaveBeenCalled()
    expect(wsService.isConnected.value).toBe(true)
  })

  it('should handle connection errors', async () => {
    const error = new Error('Connection failed')
    const errorHandler = vi.fn()
    
    wsService.onError(errorHandler)
    mockWs.simulateError(error)

    expect(errorHandler).toHaveBeenCalledWith(error)
    expect(wsService.isConnected.value).toBe(false)
  })

  it('should send messages', async () => {
    const sendSpy = vi.spyOn(mockWs, 'send')
    const message = { type: 'test', data: { foo: 'bar' } }

    mockWs.simulateOpen()
    await wsService.send(message)

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(message))
  })

  it('should receive messages', () => {
    const messageHandler = vi.fn()
    const message = { type: 'test', data: { foo: 'bar' } }

    wsService.onMessage(messageHandler)
    mockWs.simulateOpen()
    mockWs.simulateMessage(message)

    expect(messageHandler).toHaveBeenCalledWith(message)
  })

  it('should handle reconnection', async () => {
    const maxRetries = 3
    wsService = new WebSocketService('ws://localhost:8000/ws', { maxRetries })
    mockWs = (wsService as any).ws

    mockWs.simulateOpen()
    expect(wsService.isConnected.value).toBe(true)

    mockWs.close()
    expect(wsService.isConnected.value).toBe(false)

    // Wait for reconnection attempts
    await new Promise(resolve => setTimeout(resolve, 1000))

    expect((wsService as any).retryCount).toBeLessThanOrEqual(maxRetries)
  })

  it('should handle message queue when disconnected', async () => {
    const sendSpy = vi.spyOn(mockWs, 'send')
    const message = { type: 'test', data: { foo: 'bar' } }

    // Send message while disconnected
    await wsService.send(message)
    expect(sendSpy).not.toHaveBeenCalled()

    // Connect and verify queued message is sent
    mockWs.simulateOpen()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(sendSpy).toHaveBeenCalledWith(JSON.stringify(message))
  })

  it('should handle installation status updates', () => {
    const statusHandler = vi.fn()
    wsService.onInstallationStatus(statusHandler)

    const status = {
      type: 'installation_status',
      data: {
        status: 'in_progress',
        message: 'Installing...',
        progress: 50
      }
    }

    mockWs.simulateOpen()
    mockWs.simulateMessage(status)

    expect(statusHandler).toHaveBeenCalledWith(status.data)
  })

  it('should handle installation logs', () => {
    const logHandler = vi.fn()
    wsService.onInstallationLog(logHandler)

    const log = {
      type: 'installation_log',
      data: {
        level: 'info',
        message: 'Download complete',
        timestamp: '2025-01-03T17:00:00Z'
      }
    }

    mockWs.simulateOpen()
    mockWs.simulateMessage(log)

    expect(logHandler).toHaveBeenCalledWith(log.data)
  })

  it('should clean up resources on disconnect', () => {
    const closeSpy = vi.spyOn(mockWs, 'close')
    
    wsService.disconnect()

    expect(closeSpy).toHaveBeenCalled()
    expect(wsService.isConnected.value).toBe(false)
  })
})
