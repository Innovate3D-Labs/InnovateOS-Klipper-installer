<![CDATA[<template>
  <div class="install-progress">
    <!-- Progress Overview -->
    <div class="progress-overview">
      <div class="progress-circle">
        <svg viewBox="0 0 36 36" class="circular-progress">
          <path
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            :stroke="progressColor"
            stroke-width="2"
            :stroke-dasharray="`${progress}, 100`"
          />
          <text
            x="18"
            y="20.35"
            class="percentage"
            :fill="progressColor"
          >
            {{ progress }}%
          </text>
        </svg>
      </div>

      <div class="status-info">
        <h3>{{ statusText }}</h3>
        <p>{{ currentStep }}</p>
      </div>
    </div>

    <!-- Installation Steps -->
    <div class="installation-steps">
      <div 
        v-for="(step, index) in steps"
        :key="index"
        class="step"
        :class="{
          'completed': step.completed,
          'current': step.current,
          'error': step.error
        }"
      >
        <div class="step-icon">
          <img 
            :src="getStepIcon(step)"
            :alt="step.status"
          >
        </div>
        <div class="step-content">
          <h4>{{ step.name }}</h4>
          <p>{{ step.description }}</p>
          <div v-if="step.error" class="step-error">
            {{ step.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- Installation Log -->
    <div class="installation-log">
      <div class="log-header">
        <h3>Installation Log</h3>
        <div class="log-filters">
          <label>
            <input 
              type="checkbox" 
              v-model="showInfo"
            > Info
          </label>
          <label>
            <input 
              type="checkbox" 
              v-model="showWarnings"
            > Warnings
          </label>
          <label>
            <input 
              type="checkbox" 
              v-model="showErrors"
            > Errors
          </label>
        </div>
      </div>

      <div class="log-content" ref="logContainer">
        <div 
          v-for="(log, index) in filteredLogs"
          :key="index"
          class="log-entry"
          :class="log.level"
        >
          <span class="timestamp">{{ formatTimestamp(log.timestamp) }}</span>
          <span class="message">{{ log.message }}</span>
        </div>
      </div>

      <div class="log-actions">
        <button 
          @click="clearLogs"
          class="btn btn-outline"
        >
          Clear Log
        </button>
        <button 
          @click="downloadLogs"
          class="btn btn-outline"
        >
          Download Log
        </button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button 
        v-if="canPause"
        @click="$emit('pause')"
        class="btn"
        :class="isPaused ? 'btn-primary' : 'btn-outline'"
      >
        {{ isPaused ? 'Resume' : 'Pause' }}
      </button>

      <button
        v-if="canCancel"
        @click="$emit('cancel')"
        class="btn btn-danger"
      >
        Cancel
      </button>

      <button
        v-if="canRetry"
        @click="$emit('retry')"
        class="btn btn-primary"
      >
        Retry
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue'
import type { InstallationStep, LogEntry } from '@/types'

export default defineComponent({
  name: 'InstallProgress',

  props: {
    progress: {
      type: Number,
      required: true
    },
    status: {
      type: String,
      required: true
    },
    currentStep: {
      type: String,
      required: true
    },
    steps: {
      type: Array as () => InstallationStep[],
      required: true
    },
    logs: {
      type: Array as () => LogEntry[],
      required: true
    }
  },

  emits: ['pause', 'cancel', 'retry'],

  setup(props) {
    const logContainer = ref<HTMLElement | null>(null)
    const showInfo = ref(true)
    const showWarnings = ref(true)
    const showErrors = ref(true)

    const statusText = computed(() => {
      switch (props.status) {
        case 'not_started': return 'Not Started'
        case 'in_progress': return 'Installing'
        case 'paused': return 'Paused'
        case 'completed': return 'Completed'
        case 'failed': return 'Failed'
        default: return 'Unknown'
      }
    })

    const progressColor = computed(() => {
      switch (props.status) {
        case 'completed': return 'var(--success-color)'
        case 'failed': return 'var(--error-color)'
        case 'paused': return 'var(--warning-color)'
        default: return 'var(--primary-color)'
      }
    })

    const isPaused = computed(() => props.status === 'paused')
    
    const canPause = computed(() => 
      props.status === 'in_progress' || props.status === 'paused'
    )
    
    const canCancel = computed(() => 
      props.status !== 'completed' && props.status !== 'failed'
    )
    
    const canRetry = computed(() => props.status === 'failed')

    const filteredLogs = computed(() => {
      return props.logs.filter(log => {
        switch (log.level) {
          case 'info': return showInfo.value
          case 'warning': return showWarnings.value
          case 'error': return showErrors.value
          default: return true
        }
      })
    })

    const getStepIcon = (step: InstallationStep) => {
      if (step.error) return require('@/assets/icons/error.svg')
      if (step.completed) return require('@/assets/icons/success.svg')
      if (step.current) return require('@/assets/icons/loading.svg')
      return require('@/assets/icons/pending.svg')
    }

    const formatTimestamp = (timestamp: string) => {
      return new Date(timestamp).toLocaleTimeString()
    }

    const clearLogs = () => {
      // Emit event to clear logs in parent
      // This keeps the source of truth in the parent
    }

    const downloadLogs = () => {
      const logText = props.logs
        .map(log => `[${log.timestamp}] [${log.level}] ${log.message}`)
        .join('\n')

      const blob = new Blob([logText], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `installation-log-${new Date().toISOString()}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    // Auto-scroll log when new entries are added
    watch(() => props.logs.length, () => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })

    return {
      logContainer,
      showInfo,
      showWarnings,
      showErrors,
      statusText,
      progressColor,
      isPaused,
      canPause,
      canCancel,
      canRetry,
      filteredLogs,
      getStepIcon,
      formatTimestamp,
      clearLogs,
      downloadLogs
    }
  }
})
</script>

<style scoped>
.install-progress {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.progress-overview {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.progress-circle {
  width: 120px;
  height: 120px;
}

.circular-progress {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.circular-progress path {
  transition: stroke-dasharray 0.3s ease;
}

.circular-progress text {
  transform: rotate(90deg);
  text-anchor: middle;
  font-size: 8px;
}

.status-info h3 {
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.installation-steps {
  margin-bottom: 2rem;
}

.step {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-alt);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.step-icon {
  width: 24px;
  height: 24px;
}

.step-icon img {
  width: 100%;
  height: 100%;
}

.step.completed {
  border-left: 4px solid var(--success-color);
}

.step.current {
  border-left: 4px solid var(--primary-color);
}

.step.error {
  border-left: 4px solid var(--error-color);
}

.step-error {
  color: var(--error-color);
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.installation-log {
  background: var(--background-alt);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.log-filters {
  display: flex;
  gap: 1rem;
}

.log-filters label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.log-content {
  height: 300px;
  overflow-y: auto;
  font-family: monospace;
  background: var(--background-color);
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
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

.log-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

@media (max-width: 768px) {
  .install-progress {
    padding: 1rem;
  }

  .progress-overview {
    flex-direction: column;
    text-align: center;
  }

  .log-header {
    flex-direction: column;
    gap: 1rem;
  }

  .log-actions,
  .action-buttons {
    flex-direction: column;
  }

  .log-actions .btn,
  .action-buttons .btn {
    width: 100%;
  }
}
</style>]]>
