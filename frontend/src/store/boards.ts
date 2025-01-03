import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Board, BoardType } from '@/types'

export const useBoardStore = defineStore('boards', () => {
  // State
  const availableBoards = ref<Board[]>([])
  const supportedBoardTypes = ref<BoardType[]>([])
  const isScanning = ref(false)
  const lastScanError = ref<string | null>(null)
  const lastScanTime = ref<Date | null>(null)

  // Computed
  const hasAvailableBoards = computed(() => 
    availableBoards.value.length > 0
  )

  const groupedBoards = computed(() => {
    const groups: Record<string, Board[]> = {}
    availableBoards.value.forEach(board => {
      if (!groups[board.name]) {
        groups[board.name] = []
      }
      groups[board.name].push(board)
    })
    return groups
  })

  const getBoardByPort = computed(() => (port: string) =>
    availableBoards.value.find(board => board.port === port)
  )

  // Actions
  async function scanBoards() {
    isScanning.value = true
    lastScanError.value = null

    try {
      const response = await fetch('/api/boards/detect')
      
      if (!response.ok) {
        throw new Error('Failed to detect boards')
      }

      availableBoards.value = await response.json()
      lastScanTime.value = new Date()

    } catch (err) {
      lastScanError.value = err instanceof Error ? err.message : 'Board detection failed'
      throw err
    } finally {
      isScanning.value = false
    }
  }

  async function loadBoardTypes() {
    try {
      const response = await fetch('/api/boards/types')
      
      if (!response.ok) {
        throw new Error('Failed to load board types')
      }

      supportedBoardTypes.value = await response.json()

    } catch (err) {
      console.error('Failed to load board types:', err)
      throw err
    }
  }

  function isBoardSupported(board: Board): boolean {
    return board.types.some(type => 
      supportedBoardTypes.value.includes(type)
    )
  }

  function getBoardTypeInfo(type: BoardType) {
    const typeInfo = {
      MEGA: {
        name: 'Arduino Mega',
        description: 'Popular 8-bit board with good community support',
        features: ['Basic motion control', 'Limited advanced features']
      },
      DUE: {
        name: 'Arduino Due',
        description: '32-bit board with improved performance',
        features: ['Fast processing', 'Advanced motion planning']
      },
      SKR: {
        name: 'SKR',
        description: 'Modern 32-bit board with extensive features',
        features: ['Input shaping', 'Pressure advance', 'Multiple drivers']
      },
      RAMPS: {
        name: 'RAMPS',
        description: 'Classic RepRap board',
        features: ['Basic motion control', 'Wide compatibility']
      },
      EINSY: {
        name: 'Einsy Rambo',
        description: 'High-end 32-bit board',
        features: ['TMC drivers', 'Advanced features']
      },
      OCTOPUS: {
        name: 'BTT Octopus',
        description: 'Premium board with extensive I/O',
        features: ['Multiple drivers', 'Advanced features', 'Expandability']
      },
      SPIDER: {
        name: 'BTT Spider',
        description: 'High-performance board',
        features: ['Fast processing', 'Multiple drivers', 'Advanced features']
      }
    }

    return typeInfo[type] || {
      name: type,
      description: 'Generic board',
      features: ['Basic functionality']
    }
  }

  function reset() {
    availableBoards.value = []
    lastScanError.value = null
    lastScanTime.value = null
  }

  // Initialize
  loadBoardTypes().catch(console.error)

  return {
    // State
    availableBoards,
    supportedBoardTypes,
    isScanning,
    lastScanError,
    lastScanTime,

    // Computed
    hasAvailableBoards,
    groupedBoards,
    getBoardByPort,

    // Actions
    scanBoards,
    loadBoardTypes,
    isBoardSupported,
    getBoardTypeInfo,
    reset
  }
})
