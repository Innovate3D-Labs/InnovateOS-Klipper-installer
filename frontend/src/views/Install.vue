<![CDATA[<template>
  <div class="install">
    <h1>Installing Klipper</h1>

    <div class="installation-status">
      <div class="progress-container">
        <div 
          class="progress-bar"
          :style="{ width: `${installationProgress}%` }"
          :class="{ 
            'paused': isPaused,
            'error': hasError 
          }"
        ></div>
      </div>

      <div class="status-info">
        <div class="status-text">
          <span class="label">Status:</span>
          <span :class="statusClass">{{ statusText }}</span>
        </div>
        <div class="progress-text">
          {{ installationProgress }}% Complete
        </div>
      </div>

      <div class="current-step">
        <h3>Current Step:</h3>
        <p>{{ currentStep }}</p>
      </div>
    </div>

    <div class="installation-log">
      <h3>Installation Log</h3>
      <div class="log-container" ref="logContainer">
        <div 
          v-for="(log, index) in logs"
          :key="index"
          class="log-entry"
          :class="log.level"
        >
          <span class="timestamp">{{ formatTimestamp(log.timestamp) }}</span>
          <span class="message">{{ log.message }}</span>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button 
        v-if="canPause"
        @click="togglePause"
        class="btn"
        :class="isPaused ? 'btn-primary' : 'btn-outline'"
      >
        {{ isPaused ? 'Resume' : 'Pause' }}
      </button>

      <button
        v-if="canCancel"
        @click="showCancelConfirm = true"
        class="btn btn-danger"
      >
        Cancel Installation
      </button>

      <button
        v-if="canRetry"
        @click="retryInstallation"
        class="btn btn-primary"
      >
        Retry Installation
      </button>

      <router-link
        v-if="isComplete"
        to="/complete"
        class="btn btn-primary"
      >
        View Results
      </router-link>
    </div>

    <!-- Cancel Confirmation Dialog -->
    <ConfirmDialog
      v-if="showCancelConfirm"
      title="Cancel Installation?"
      message="Are you sure you want to cancel the installation? This action cannot be undone."
      confirmText="Yes, Cancel"
      cancelText="No, Continue"
      @confirm="cancelInstallation"
      @cancel="showCancelConfirm = false"
    />

    <!-- Error Display -->
    <ErrorDisplay
      v-for="error in errors"
      :key="error.id"
      :error="error"
      @dismiss="dismissError(error.id)"
      @retry="retryInstallation"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/store'
import { useApi } from '@/composables/useApi'
import { installationEvents } from '@/services/websocket'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import ErrorDisplay from '@/components/ErrorDisplay.vue'
import type { LogEntry } from '@/types'

export default defineComponent({
  name: 'Install',

  components: {
    ConfirmDialog,
    ErrorDisplay
  },

  setup() {
    const router = useRouter()
    const store = useMainStore()
    const { startInstallation, pauseInstallation, resumeInstallation, cancelInstallation } = useApi()

    const logs = ref<LogEntry[]>([])
    const showCancelConfirm = ref(false)
    const logContainer = ref<HTMLElement | null>(null)

    const installationProgress = computed(() => store.installationProgress)
    const currentStep = computed(() => store.currentStep)
    const errors = computed(() => store.currentErrors)
    
    const statusText = computed(() => {
      switch (store.installationStatus) {
        case 'not_started': return 'Not Started'
        case 'in_progress': return 'Installing'
        case 'paused': return 'Paused'
        case 'completed': return 'Completed'
        case 'failed': return 'Failed'
        default: return 'Unknown'
      }
    })

    const statusClass = computed(() => {
      return `status-${store.installationStatus}`
    })

    const isPaused = computed(() => store.installationStatus === 'paused')
    const isComplete = computed(() => store.installationStatus === 'completed')
    const hasError = computed(() => store.installationStatus === 'failed')

    const canPause = computed(() => 
      store.installationStatus === 'in_progress' || 
      store.installationStatus === 'paused'
    )

    const canCancel = computed(() => 
      store.installationStatus !== 'completed' && 
      store.installationStatus !== 'failed'
    )

    const canRetry = computed(() => 
      store.installationStatus === 'failed'
    )

    const formatTimestamp = (timestamp: string) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const scrollToBottom = () => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    }

    const togglePause = async () => {
      try {
        if (isPaused.value) {
          await resumeInstallation()
        } else {
          await pauseInstallation()
        }
      } catch (error: any) {
        store.addError({
          title: isPaused.value ? 'Resume Failed' : 'Pause Failed',
          message: error.message,
          severity: 'error'
        })
      }
    }

    const retryInstallation = async () => {
      try {
        store.clearErrors()
        await startInstallation()
      } catch (error: any) {
        store.addError({
          title: 'Retry Failed',
          message: error.message,
          severity: 'error'
        })
      }
    }

    const dismissError = (errorId: string) => {
      store.removeError(errorId)
    }

    onMounted(async () => {
      // Initialize WebSocket connection
      await store.initializeWebSocket()

      // Set up log handling
      installationEvents.onLog((log) => {
        logs.value.push(log)
        scrollToBottom()
      })

      // Start installation
      try {
        await startInstallation()
      } catch (error: any) {
        store.addError({
          title: 'Installation Failed',
          message: error.message,
          severity: 'critical'
        })
      }
    })

    onUnmounted(() => {
      if (!isComplete.value) {
        store.disconnectWebSocket()
      }
    })

    return {
      installationProgress,
      currentStep,
      statusText,
      statusClass,
      isPaused,
      isComplete,
      hasError,
      canPause,
      canCancel,
      canRetry,
      logs,
      errors,
      showCancelConfirm,
      logContainer,
      togglePause,
      retryInstallation,
      dismissError,
      formatTimestamp,
      cancelInstallation
    }
  }
})
</script>

<style scoped>
.install {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.installation-status {
  margin: 2rem 0;
}

.progress-container {
  height: 20px;
  background: var(--background-alt);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-bar {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-bar.paused {
  background: var(--warning-color);
}

.progress-bar.error {
  background: var(--error-color);
}

.status-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-text {
  display: flex;
  gap: 0.5rem;
}

.label {
  font-weight: 500;
  color: var(--text-light);
}

.status-in_progress { color: var(--primary-color); }
.status-paused { color: var(--warning-color); }
.status-completed { color: var(--success-color); }
.status-failed { color: var(--error-color); }

.current-step {
  background: var(--background-alt);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.installation-log {
  background: var(--background-alt);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.log-container {
  height: 300px;
  overflow-y: auto;
  font-family: monospace;
  background: var(--background-color);
  padding: 1rem;
  border-radius: 4px;
}

.log-entry {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.log-entry .timestamp {
  color: var(--text-light);
  margin-right: 1rem;
}

.log-entry.info { color: var(--text-color); }
.log-entry.warning { color: var(--warning-color); }
.log-entry.error { color: var(--error-color); }

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

@media (max-width: 768px) {
  .install {
    padding: 1rem;
  }

  .status-info {
    flex-direction: column;
    gap: 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .btn {
    width: 100%;
  }
}
</style>]]>
