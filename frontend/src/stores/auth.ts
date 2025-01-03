import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/services/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const activeInstallation = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const hasActiveInstallation = computed(() => !!activeInstallation.value)
  const currentUser = computed(() => user.value)

  // Actions
  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      })

      token.value = response.data.token
      user.value = response.data.user

      // Load active installation if exists
      await checkActiveInstallation()

      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      token.value = null
      user.value = null
      activeInstallation.value = null
    }
  }

  const checkAuth = async () => {
    try {
      const response = await apiClient.get('/auth/check')
      user.value = response.data.user
      return true
    } catch (error) {
      token.value = null
      user.value = null
      return false
    }
  }

  const checkActiveInstallation = async () => {
    try {
      const response = await apiClient.get('/installation/active')
      activeInstallation.value = response.data.installation_id
      return true
    } catch (error) {
      activeInstallation.value = null
      return false
    }
  }

  const updateProfile = async (profile: Partial<User>) => {
    try {
      const response = await apiClient.put('/auth/profile', profile)
      user.value = response.data
      return true
    } catch (error) {
      console.error('Profile update failed:', error)
      return false
    }
  }

  const changePassword = async (
    currentPassword: string,
    newPassword: string
  ) => {
    try {
      await apiClient.put('/auth/password', {
        current_password: currentPassword,
        new_password: newPassword
      })
      return true
    } catch (error) {
      console.error('Password change failed:', error)
      return false
    }
  }

  const setActiveInstallation = (installationId: string | null) => {
    activeInstallation.value = installationId
  }

  const reset = () => {
    token.value = null
    user.value = null
    activeInstallation.value = null
  }

  return {
    // State
    user,
    token,
    activeInstallation,

    // Getters
    isAuthenticated,
    hasActiveInstallation,
    currentUser,

    // Actions
    login,
    logout,
    checkAuth,
    checkActiveInstallation,
    updateProfile,
    changePassword,
    setActiveInstallation,
    reset
  }
})
