<![CDATA[<template>
  <div 
    v-if="error"
    class="error-display"
    :class="type"
  >
    <div class="error-content">
      <div class="error-icon">
        <img 
          :src="iconSrc"
          :alt="type"
        >
      </div>

      <div class="error-message">
        <h3 v-if="title">{{ title }}</h3>
        <p>{{ error }}</p>
        <div 
          v-if="details"
          class="error-details"
        >
          <button 
            @click="showDetails = !showDetails"
            class="details-toggle"
          >
            {{ showDetails ? 'Hide Details' : 'Show Details' }}
          </button>
          <pre v-if="showDetails">{{ details }}</pre>
        </div>
      </div>

      <div class="error-actions">
        <slot name="actions">
          <button 
            v-if="retryable"
            @click="$emit('retry')"
            class="btn btn-primary"
          >
            Retry
          </button>
          <button 
            v-if="dismissible"
            @click="$emit('dismiss')"
            class="btn btn-outline"
          >
            Dismiss
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue'

export default defineComponent({
  name: 'ErrorDisplay',

  props: {
    error: {
      type: [String, Error],
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    details: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'error',
      validator: (value: string) => {
        return ['error', 'warning', 'info'].includes(value)
      }
    },
    retryable: {
      type: Boolean,
      default: false
    },
    dismissible: {
      type: Boolean,
      default: true
    }
  },

  emits: ['retry', 'dismiss'],

  setup(props) {
    const showDetails = ref(false)

    const iconSrc = computed(() => {
      switch (props.type) {
        case 'warning':
          return require('@/assets/icons/warning.svg')
        case 'info':
          return require('@/assets/icons/info.svg')
        default:
          return require('@/assets/icons/error.svg')
      }
    })

    return {
      showDetails,
      iconSrc
    }
  }
})
</script>

<style scoped>
.error-display {
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 8px;
  background: var(--background-alt);
  border-left: 4px solid;
}

.error-display.error {
  border-left-color: var(--error-color);
}

.error-display.warning {
  border-left-color: var(--warning-color);
}

.error-display.info {
  border-left-color: var(--info-color);
}

.error-content {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.error-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.error-icon img {
  width: 100%;
  height: 100%;
}

.error-message {
  flex-grow: 1;
}

.error-message h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.error-message p {
  margin: 0;
  color: var(--text-light);
}

.error-details {
  margin-top: 1rem;
}

.details-toggle {
  background: none;
  border: none;
  color: var(--primary-color);
  padding: 0;
  font-size: 0.9rem;
  cursor: pointer;
}

.details-toggle:hover {
  text-decoration: underline;
}

.error-details pre {
  margin: 0.5rem 0 0 0;
  padding: 1rem;
  background: var(--background-color);
  border-radius: 4px;
  font-size: 0.9rem;
  overflow-x: auto;
}

.error-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

@media (max-width: 768px) {
  .error-content {
    flex-direction: column;
  }

  .error-actions {
    margin-left: 0;
    margin-top: 1rem;
    justify-content: flex-end;
  }
}
</style>]]>
