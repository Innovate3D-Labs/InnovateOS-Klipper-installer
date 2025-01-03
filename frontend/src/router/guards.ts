import { NavigationGuardWithThis, RouteLocationNormalized } from 'vue-router'
import { useInstallationStore } from '@/store/installation'
import { useConfigStore } from '@/store/config'

export const requireBoardSelection: NavigationGuardWithThis<undefined> = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: Function
) => {
  const installationStore = useInstallationStore()
  
  if (!installationStore.selectedBoard) {
    next({ name: 'home', query: { redirect: to.fullPath } })
  } else {
    next()
  }
}

export const requireConfig: NavigationGuardWithThis<undefined> = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: Function
) => {
  const configStore = useConfigStore()
  
  if (!configStore.isConfigValid) {
    next({ 
      name: 'config', 
      query: { 
        redirect: to.fullPath,
        error: 'Please complete the configuration first'
      } 
    })
  } else {
    next()
  }
}

export const requireInstallationInProgress: NavigationGuardWithThis<undefined> = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: Function
) => {
  const installationStore = useInstallationStore()
  
  if (!installationStore.isInstallationStarted) {
    next({ 
      name: 'home',
      query: { 
        error: 'No installation in progress'
      } 
    })
  } else {
    next()
  }
}

export const preventWhenInstalling: NavigationGuardWithThis<undefined> = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: Function
) => {
  const installationStore = useInstallationStore()
  
  if (installationStore.isInstalling) {
    next(false) // Prevent navigation
  } else {
    next()
  }
}

export const requireInstallationComplete: NavigationGuardWithThis<undefined> = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: Function
) => {
  const installationStore = useInstallationStore()
  
  if (!installationStore.isInstallationComplete) {
    next({ 
      name: 'home',
      query: { 
        error: 'Installation not completed'
      } 
    })
  } else {
    next()
  }
}
