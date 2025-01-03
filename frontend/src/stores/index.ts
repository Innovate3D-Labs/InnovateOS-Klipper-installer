import { createPinia } from 'pinia'
import { markRaw } from 'vue'
import router from '@/router'
import type { Router } from 'vue-router'

declare module 'pinia' {
  export interface PiniaCustomProperties {
    router: Router
  }
}

const pinia = createPinia()

// Add router to stores
pinia.use(({ store }) => {
  store.router = markRaw(router)
})

export default pinia
