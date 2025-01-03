<![CDATA[<template>
  <div class="app">
    <header class="app-header">
      <nav class="nav-container">
        <router-link to="/" class="logo">
          InnovateOS Klipper
        </router-link>
        
        <div class="installation-progress" v-if="showProgress">
          <div class="progress-steps">
            <div 
              v-for="(step, index) in installationSteps" 
              :key="step.route"
              class="step"
              :class="{
                'active': currentStepIndex === index,
                'completed': currentStepIndex > index
              }"
            >
              {{ step.name }}
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main class="app-content">
      <router-view v-slot="{ Component }">
        <transition 
          name="fade" 
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="app-footer">
      <div class="footer-content">
        <p>&copy; {{ currentYear }} InnovateOS. All rights reserved.</p>
        <div class="footer-links">
          <a href="https://github.com/InnovateOS/Klipper-installer" target="_blank">GitHub</a>
          <a href="https://docs.innovateos.dev" target="_blank">Documentation</a>
          <router-link to="/about">About</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMainStore } from '@/store'

export default defineComponent({
  name: 'App',

  setup() {
    const route = useRoute()
    const store = useMainStore()

    const installationSteps = [
      { name: 'Select Board', route: '/select-board' },
      { name: 'Configure', route: '/configure' },
      { name: 'Install', route: '/install' },
      { name: 'Complete', route: '/complete' }
    ]

    const currentStepIndex = computed(() => {
      return installationSteps.findIndex(step => step.route === route.path)
    })

    const showProgress = computed(() => {
      return currentStepIndex.value !== -1 && route.path !== '/'
    })

    const currentYear = computed(() => new Date().getFullYear())

    return {
      installationSteps,
      currentStepIndex,
      showProgress,
      currentYear
    }
  }
})
</script>

<style>
/* Import global styles */
@import './styles/main.css';

/* App-specific styles */
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  text-decoration: none;
}

.installation-progress {
  flex-grow: 1;
  margin-left: 2rem;
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.step {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  color: var(--text-light);
  position: relative;
}

.step::after {
  content: "→";
  position: absolute;
  right: -1rem;
  color: var(--text-light);
}

.step:last-child::after {
  display: none;
}

.step.active {
  background-color: var(--primary-color);
  color: white;
}

.step.completed {
  background-color: var(--background-alt);
  color: var(--primary-color);
}

.app-content {
  flex-grow: 1;
  background-color: var(--background-color);
}

.app-footer {
  background-color: var(--background-alt);
  padding: 1rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-links {
  display: flex;
  gap: 1rem;
}

.footer-links a {
  color: var(--text-light);
  text-decoration: none;
}

.footer-links a:hover {
  color: var(--primary-color);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }

  .installation-progress {
    margin-left: 0;
    width: 100%;
    overflow-x: auto;
  }

  .progress-steps {
    padding: 0.5rem;
  }

  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>]]>
