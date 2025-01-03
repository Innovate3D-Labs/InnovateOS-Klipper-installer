<![CDATA[<template>
  <div>
    <div v-if="error" class="error-boundary">
      <div class="error-content">
        <div class="error-icon">
          <img 
            src="@/assets/icons/error.svg" 
            alt="Error"
          >
        </div>
        
        <h2>{{ error.title || 'Something went wrong' }}</h2>
        <p class="error-message">{{ error.message }}</p>
        
        <div v-if="error.details" class="error-details">
          <button 
            @click="showDetails = !showDetails"
            class="details-toggle"
          >
            {{ showDetails ? 'Hide' : 'Show' }} Technical Details
          </button>
          
          <pre v-if="showDetails" class="details-content">
            {{ error.details }}
          </pre>
        </div>

        <div class="action-buttons">
          <button 
            @click="retry"
            class="btn btn-primary"
          >
            Try Again
          </button>
          
          <button 
            @click="reset"
            class="btn btn-outline"
          >
            Reset Application
          </button>
        </div>
      </div>
    </div>
    
    <slot v-else></slot>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/store'
import type { ErrorInfo } from '@/types'

export default defineComponent({
  name: 'ErrorBoundary',

  props: {
    shouldReset: {
      type: Boolean,
      default: true
    }
  },

  setup(props, { emit }) {
    const router = useRouter()
    const store = useMainStore()
    
    const error = ref<ErrorInfo | null>(null)
    const showDetails = ref(false)

    onErrorCaptured((err: Error, component, info) => {
      error.value = {
        title: 'Component Error',
        message: err.message,
        details: `
Component: ${component?.$.type.name}
Info: ${info}
Stack: ${err.stack}
        `.trim(),
        severity: 'critical'
      }

      // Emit error for parent components
      emit('error', error.value)
      
      // Prevent error from propagating
      return false
    })

    const retry = () => {
      error.value = null
      emit('retry')
    }

    const reset = async () => {
      if (props.shouldReset) {
        // Reset application state
        store.resetState()
        
        // Disconnect WebSocket if connected
        if (store.wsConnected) {
          store.disconnectWebSocket()
        }
        
        // Navigate to home
        await router.push('/')
        
        // Clear error
        error.value = null
        
        // Emit reset event
        emit('reset')
      }
    }

    return {
      error,
      showDetails,
      retry,
      reset
    }
  }
})
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--background-color);
}

.error-content {
  max-width: 600px;
  text-align: center;
  background: var(--background-alt);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.error-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
}

.error-icon img {
  width: 100%;
  height: 100%;
}

.error-message {
  color: var(--text-light);
  margin: 1rem 0;
}

.error-details {
  margin: 1.5rem 0;
}

.details-toggle {
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.details-content {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9rem;
  text-align: left;
  white-space: pre-wrap;
  overflow-x: auto;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .error-boundary {
    padding: 1rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .btn {
    width: 100%;
  }
}
</style>]]>
