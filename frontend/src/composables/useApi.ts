import { ref } from 'vue'
import type { Ref } from 'vue'
import { boardsApi, configApi, installationApi } from '@/services/api'
import type { Board, PrinterConfig, InstallationStatus } from '@/types'

export function useApi() {
  const loading = ref(false)
  const error: Ref<Error | null> = ref(null)

  const wrapApiCall = async <T>(apiCall: () => Promise<T>): Promise<T | null> => {
    loading.value = true
    error.value = null

    try {
      const result = await apiCall()
      return result
    } catch (e: any) {
      error.value = e
      return null
    } finally {
      loading.value = false
    }
  }

  // Boards API
  const getBoards = () => wrapApiCall(() => boardsApi.getBoards())
  
  const getBoardById = (id: string) => 
    wrapApiCall(() => boardsApi.getBoardById(id))
  
  const getBoardConfiguration = (id: string) => 
    wrapApiCall(() => boardsApi.getBoardConfiguration(id))

  // Configuration API
  const saveConfig = (config: PrinterConfig) => 
    wrapApiCall(() => configApi.saveConfig(config))
  
  const validateConfig = (config: PrinterConfig) => 
    wrapApiCall(() => configApi.validateConfig(config))
  
  const getDefaultConfig = () => 
    wrapApiCall(() => configApi.getDefaultConfig())

  // Installation API
  const startInstallation = () => 
    wrapApiCall(() => installationApi.startInstallation())
  
  const pauseInstallation = () => 
    wrapApiCall(() => installationApi.pauseInstallation())
  
  const resumeInstallation = () => 
    wrapApiCall(() => installationApi.resumeInstallation())
  
  const cancelInstallation = () => 
    wrapApiCall(() => installationApi.cancelInstallation())
  
  const getInstallationStatus = () => 
    wrapApiCall(() => installationApi.getInstallationStatus())

  return {
    // State
    loading,
    error,

    // Board methods
    getBoards,
    getBoardById,
    getBoardConfiguration,

    // Config methods
    saveConfig,
    validateConfig,
    getDefaultConfig,

    // Installation methods
    startInstallation,
    pauseInstallation,
    resumeInstallation,
    cancelInstallation,
    getInstallationStatus
  }
}
