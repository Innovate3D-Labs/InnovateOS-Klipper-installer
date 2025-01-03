import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      authStore.reset()
      router.push({
        name: 'home',
        query: { redirect: router.currentRoute.value.fullPath }
      })
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      router.push({ name: 'not-found' })
    }

    return Promise.reject(error)
  }
)

export { apiClient }

// API Endpoints
export const api = {
  // Auth
  auth: {
    login: (data: { username: string; password: string }) =>
      apiClient.post('/auth/login', data),
    logout: () => apiClient.post('/auth/logout'),
    profile: () => apiClient.get('/auth/profile'),
    updateProfile: (data: any) => apiClient.put('/auth/profile', data),
    changePassword: (data: {
      current_password: string
      new_password: string
    }) => apiClient.put('/auth/password', data)
  },

  // Hardware
  hardware: {
    detectBoards: () => apiClient.get('/hardware/detect'),
    testConnection: (port: string) =>
      apiClient.post('/hardware/test-connection', { port }),
    getBoardInfo: (port: string) =>
      apiClient.get(`/hardware/board-info/${port}`)
  },

  // Configuration
  config: {
    getProfiles: () => apiClient.get('/config/profiles'),
    getProfile: (name: string) => apiClient.get(`/config/profiles/${name}`),
    validateConfig: (config: any) =>
      apiClient.post('/config/validate', config),
    saveConfig: (config: any) => apiClient.post('/config/save', config),
    backupConfig: (name: string) =>
      apiClient.post(`/config/backup/${name}`),
    restoreConfig: (file: File) => {
      const formData = new FormData()
      formData.append('config', file)
      return apiClient.post('/config/restore', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },

  // Installation
  installation: {
    start: (data: { board: any; config: any }) =>
      apiClient.post('/installation/start', data),
    getStatus: (id: string) =>
      apiClient.get(`/installation/${id}/status`),
    cancel: (id: string) =>
      apiClient.post(`/installation/${id}/cancel`),
    getActive: () => apiClient.get('/installation/active')
  },

  // System
  system: {
    getMetrics: () => apiClient.get('/system/metrics'),
    getLogs: (params?: {
      level?: string
      limit?: number
      start?: string
      end?: string
    }) => apiClient.get('/system/logs', { params }),
    getVersion: () => apiClient.get('/system/version')
  }
}
