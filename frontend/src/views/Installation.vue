`<template>
  <div class="installation-view">
    <div class="installation-container">
      <!-- Header -->
      <div class="header">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </div>

      <!-- Progress Section -->
      <div class="progress-section">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${progress}%` }"
            :class="{ error: hasError }"
          ></div>
        </div>
        <div class="progress-text">
          {{ progress }}% Complete
        </div>
      </div>

      <!-- Status Section -->
      <div class="status-section">
        <div class="status-icon" :class="statusClass">
          <i :class="statusIcon"></i>
        </div>
        <div class="status-details">
          <h3>{{ currentStep }}</h3>
          <p>{{ currentMessage }}</p>
        </div>
      </div>

      <!-- Log Section -->
      <div class="log-section" v-if="showLogs">
        <div class="log-header">
          <h3>Installation Logs</h3>
          <button @click="toggleLogs">
            {{ showLogs ? 'Hide' : 'Show' }} Logs
          </button>
        </div>
        <div class="log-content" ref="logContent">
          <div v-for="(log, index) in logs" :key="index" class="log-entry">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span :class="['log-level', log.level]">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <!-- Error Section -->
      <div v-if="hasError" class="error-section">
        <ErrorDisplay
          :error="error"
          :canRetry="canRetry"
          @retry="handleRetry"
          @cancel="handleCancel"
        />
      </div>

      <!-- Actions -->
      <div class="actions">
        <button
          v-if="canCancel"
          class="btn-secondary"
          @click="handleCancel"
          :disabled="isCompleted"
        >
          Cancel
        </button>
        <button
          v-if="isCompleted"
          class="btn-primary"
          @click="handleComplete"
        >
          Continue
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInstallationStore } from '@/store/installation'
import { useWebSocket } from '@/composables/useWebSocket'
import ErrorDisplay from '@/components/ErrorDisplay.vue'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const installationStore = useInstallationStore()
const { connect, disconnect, sendMessage } = useWebSocket()

// State
const showLogs = ref(false)
const logs = ref<Array<{ timestamp: Date; level: string; message: string }>>([])
const error = ref<Error | null>(null)

// Computed
const progress = computed(() => installationStore.progress)
const currentStep = computed(() => installationStore.currentStep)
const currentMessage = computed(() => installationStore.currentMessage)
const hasError = computed(() => !!error.value)
const isCompleted = computed(() => installationStore.status === 'completed')
const canCancel = computed(() => !isCompleted.value)
const canRetry = computed(() => hasError.value && !isCompleted.value)

const title = computed(() => {
  if (isCompleted.value) return 'Installation Complete'
  if (hasError.value) return 'Installation Error'
  return 'Installing Klipper'
})

const subtitle = computed(() => {
  if (isCompleted.value) return 'Your printer is ready to use'
  if (hasError.value) return 'An error occurred during installation'
  return 'Please wait while we install Klipper on your printer'
})

const statusClass = computed(() => ({
  'status-running': !hasError.value && !isCompleted.value,
  'status-error': hasError.value,
  'status-complete': isCompleted.value
}))

const statusIcon = computed(() => ({
  'fas fa-spinner fa-spin': !hasError.value && !isCompleted.value,
  'fas fa-times': hasError.value,
  'fas fa-check': isCompleted.value
}))

// Methods
const toggleLogs = () => {
  showLogs.value = !showLogs.value
}

const formatTime = (timestamp: Date) => {
  return formatDateTime(timestamp)
}

const handleRetry = async () => {
  error.value = null
  await installationStore.retryInstallation()
}

const handleCancel = async () => {
  if (await installationStore.cancelInstallation()) {
    router.push('/board-selection')
  }
}

const handleComplete = () => {
  router.push('/complete')
}

const handleWebSocketMessage = (message: any) => {
  switch (message.type) {
    case 'progress':
      installationStore.setProgress(message.progress)
      break
    case 'status':
      installationStore.setStatus(message.status)
      break
    case 'log':
      logs.value.push({
        timestamp: new Date(),
        level: message.level,
        message: message.message
      })
      break
    case 'error':
      error.value = new Error(message.message)
      break
  }
}

// Lifecycle
onMounted(async () => {
  try {
    await connect()
    await installationStore.startInstallation()
  } catch (err) {
    error.value = err as Error
  }
})

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.installation-view {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.installation-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.8rem;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.header p {
  color: var(--color-text-secondary);
}

.progress-section {
  margin-bottom: 2rem;
}

.progress-bar {
  height: 8px;
  background: var(--color-background-light);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-fill.error {
  background: var(--color-error);
}

.progress-text {
  text-align: center;
  margin-top: 0.5rem;
  color: var(--color-text-secondary);
}

.status-section {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--color-background-light);
  border-radius: 4px;
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.status-running {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.status-error {
  background: var(--color-error-light);
  color: var(--color-error);
}

.status-complete {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-details h3 {
  margin: 0;
  color: var(--color-text-primary);
}

.status-details p {
  margin: 0.25rem 0 0;
  color: var(--color-text-secondary);
}

.log-section {
  margin-bottom: 2rem;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.log-content {
  height: 200px;
  overflow-y: auto;
  background: var(--color-background-dark);
  border-radius: 4px;
  padding: 1rem;
  font-family: monospace;
}

.log-entry {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.log-time {
  color: var(--color-text-secondary);
  margin-right: 0.5rem;
}

.log-level {
  padding: 0.25rem 0.5rem;
  border-radius: 2px;
  margin-right: 0.5rem;
  font-size: 0.8rem;
}

.log-level.info {
  background: var(--color-info-light);
  color: var(--color-info);
}

.log-level.warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.log-level.error {
  background: var(--color-error-light);
  color: var(--color-error);
}

.log-message {
  color: var(--color-text-primary);
}

.error-section {
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-background-light);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>`
