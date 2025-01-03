import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { boardsApi, configApi, installationApi } from '../api'
import type { Board, PrinterConfig } from '@/types'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      interceptors: {
        response: {
          use: vi.fn()
        }
      }
    }))
  }
}))

describe('API Services', () => {
  let mockAxios: any

  beforeEach(() => {
    mockAxios = axios.create()
    vi.clearAllMocks()
  })

  describe('boardsApi', () => {
    const mockBoards: Board[] = [
      {
        id: '1',
        name: 'Test Board',
        processor: 'STM32',
        flashSize: '256KB',
        interfaces: ['USB', 'UART'],
        description: 'Test board description'
      }
    ]

    it('should fetch all boards', async () => {
      mockAxios.get.mockResolvedValueOnce({ data: mockBoards })
      const result = await boardsApi.getBoards()
      expect(result).toEqual(mockBoards)
      expect(mockAxios.get).toHaveBeenCalledWith('/boards')
    })

    it('should fetch board by id', async () => {
      const board = mockBoards[0]
      mockAxios.get.mockResolvedValueOnce({ data: board })
      const result = await boardsApi.getBoardById('1')
      expect(result).toEqual(board)
      expect(mockAxios.get).toHaveBeenCalledWith('/boards/1')
    })

    it('should handle errors when fetching boards', async () => {
      const error = new Error('Network error')
      mockAxios.get.mockRejectedValueOnce(error)
      await expect(boardsApi.getBoards()).rejects.toThrow()
    })
  })

  describe('configApi', () => {
    const mockConfig: PrinterConfig = {
      printerName: 'Test Printer',
      dimensions: { x: 200, y: 200, z: 200 },
      maxVelocity: { x: 300, y: 300, z: 20 },
      maxAcceleration: { x: 3000, y: 3000, z: 100 }
    }

    it('should save configuration', async () => {
      mockAxios.post.mockResolvedValueOnce({ data: mockConfig })
      await configApi.saveConfig(mockConfig)
      expect(mockAxios.post).toHaveBeenCalledWith('/config', mockConfig)
    })

    it('should validate configuration', async () => {
      const validationResult = { valid: true }
      mockAxios.post.mockResolvedValueOnce({ data: validationResult })
      const result = await configApi.validateConfig(mockConfig)
      expect(result).toEqual(validationResult)
      expect(mockAxios.post).toHaveBeenCalledWith('/config/validate', mockConfig)
    })

    it('should handle validation errors', async () => {
      const validationError = {
        valid: false,
        errors: ['Invalid printer dimensions']
      }
      mockAxios.post.mockResolvedValueOnce({ data: validationError })
      const result = await configApi.validateConfig(mockConfig)
      expect(result.valid).toBe(false)
      expect(result.errors).toContain('Invalid printer dimensions')
    })
  })

  describe('installationApi', () => {
    it('should start installation', async () => {
      mockAxios.post.mockResolvedValueOnce({ data: { status: 'started' } })
      await installationApi.startInstallation()
      expect(mockAxios.post).toHaveBeenCalledWith('/install/start')
    })

    it('should pause installation', async () => {
      mockAxios.post.mockResolvedValueOnce({ data: { status: 'paused' } })
      await installationApi.pauseInstallation()
      expect(mockAxios.post).toHaveBeenCalledWith('/install/pause')
    })

    it('should resume installation', async () => {
      mockAxios.post.mockResolvedValueOnce({ data: { status: 'in_progress' } })
      await installationApi.resumeInstallation()
      expect(mockAxios.post).toHaveBeenCalledWith('/install/resume')
    })

    it('should get installation status', async () => {
      const status = {
        status: 'in_progress' as const,
        progress: 50,
        currentStep: 'Installing dependencies'
      }
      mockAxios.get.mockResolvedValueOnce({ data: status })
      const result = await installationApi.getInstallationStatus()
      expect(result).toEqual(status)
      expect(mockAxios.get).toHaveBeenCalledWith('/install/status')
    })
  })
})
