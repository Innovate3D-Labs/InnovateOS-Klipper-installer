import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/board-selection',
    name: 'board-selection',
    component: () => import('@/views/BoardSelection.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/configuration',
    name: 'configuration',
    component: () => import('@/views/Configuration.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/installation',
    name: 'installation',
    component: () => import('@/views/Installation.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/complete',
    name: 'complete',
    component: () => import('@/views/Complete.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/views/Help.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth

  // Check if route requires authentication
  if (requiresAuth) {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      // Redirect to login with return path
      next({
        name: 'home',
        query: { redirect: to.fullPath }
      })
      return
    }

    // Check installation state
    if (to.name !== 'installation' && authStore.hasActiveInstallation) {
      next({ name: 'installation' })
      return
    }
  }

  // Proceed to route
  next()
})

export default router
