import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'
import type { PrinterProfile, PrinterConfig } from '@/types'

export const useConfigStore = defineStore('config', () => {
  // State
  const currentConfig = ref<PrinterConfig | null>(null)
  const profiles = ref<PrinterProfile[]>([])
  const configErrors = ref<string[]>([])

  // Getters
  const getCurrentConfig = computed(() => currentConfig.value)
  const getConfigErrors = computed(() => configErrors.value)
  const hasValidConfig = computed(() => currentConfig.value !== null && configErrors.value.length === 0)

  // Actions
  const loadProfiles = async () => {
    try {
      const response = await apiClient.get('/api/config/profiles')
      profiles.value = response.data
      return profiles.value
    } catch (error) {
      console.error('Failed to load printer profiles:', error)
      return []
    }
  }

  const loadProfile = async (name: string) => {
    try {
      const response = await apiClient.get(`/api/config/profiles/${name}`)
      return response.data as PrinterProfile
    } catch (error) {
      console.error('Failed to load printer profile:', error)
      return null
    }
  }

  const generatePreview = async (config: PrinterConfig) => {
    try {
      const response = await apiClient.post('/api/config/preview', config)
      return response.data.config as string
    } catch (error) {
      console.error('Failed to generate config preview:', error)
      return ''
    }
  }

  const validateConfig = async (config: PrinterConfig) => {
    try {
      const response = await apiClient.post('/api/config/validate', config)
      configErrors.value = response.data.errors
      return configErrors.value.length === 0
    } catch (error) {
      console.error('Failed to validate config:', error)
      return false
    }
  }

  const saveConfig = async (config: PrinterConfig) => {
    try {
      if (await validateConfig(config)) {
        const response = await apiClient.post('/api/config/save', config)
        currentConfig.value = response.data
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to save config:', error)
      return false
    }
  }

  const backupConfig = async (name: string) => {
    try {
      const response = await apiClient.post(`/api/config/backup/${name}`)
      const blob = new Blob([response.data], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${name}_backup_${new Date().toISOString()}.json`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      return true
    } catch (error) {
      console.error('Failed to backup config:', error)
      return false
    }
  }

  const restoreConfig = async (file: File) => {
    try {
      const formData = new FormData()
      formData.append('config', file)
      const response = await apiClient.post('/api/config/restore', formData)
      currentConfig.value = response.data
      return currentConfig.value
    } catch (error) {
      console.error('Failed to restore config:', error)
      return null
    }
  }

  const reset = () => {
    currentConfig.value = null
    configErrors.value = []
  }

  return {
    // State
    currentConfig,
    profiles,
    configErrors,

    // Getters
    getCurrentConfig,
    getConfigErrors,
    hasValidConfig,

    // Actions
    loadProfiles,
    loadProfile,
    generatePreview,
    validateConfig,
    saveConfig,
    backupConfig,
    restoreConfig,
    reset
  }
})
