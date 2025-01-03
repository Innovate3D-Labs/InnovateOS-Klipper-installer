<![CDATA[<template>
  <div class="configure">
    <div class="page-header">
      <h1>Configure Your Printer</h1>
      <p>Set up the configuration for your {{ boardName }}</p>
    </div>

    <div class="configuration-warning" v-if="!selectedBoard">
      <img src="@/assets/icons/warning.svg" alt="Warning" class="warning-icon">
      <p>Please select a board before proceeding with configuration</p>
      <router-link to="/select-board" class="btn btn-primary">
        Select Board
      </router-link>
    </div>

    <template v-else>
      <ConfigEditor
        @config-saved="onConfigSaved"
        @error="handleError"
      />

      <ErrorDisplay
        v-if="error"
        :error="error"
        @dismiss="error = null"
        @retry="retryConfiguration"
      />

      <div class="navigation-buttons">
        <router-link to="/select-board" class="btn btn-outline">
          Back to Board Selection
        </router-link>
        <router-link 
          v-if="canProceed"
          to="/install" 
          class="btn btn-primary"
        >
          Start Installation
        </router-link>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMainStore } from '@/store'
import ConfigEditor from '@/components/ConfigEditor.vue'
import ErrorDisplay from '@/components/ErrorDisplay.vue'
import type { PrinterConfig, ErrorInfo } from '@/types'

export default defineComponent({
  name: 'Configure',

  components: {
    ConfigEditor,
    ErrorDisplay
  },

  setup() {
    const router = useRouter()
    const store = useMainStore()
    const error = ref<ErrorInfo | null>(null)

    // Computed properties
    const selectedBoard = computed(() => store.selectedBoard)
    const boardName = computed(() => selectedBoard.value?.name ?? 'printer')
    const canProceed = computed(() => store.isConfigurationComplete)

    // If no board is selected, redirect to board selection
    if (!selectedBoard.value) {
      router.push('/select-board')
    }

    const onConfigSaved = (config: PrinterConfig) => {
      try {
        store.setPrinterConfig(config)
        error.value = null
      } catch (e) {
        handleError('Failed to save configuration')
      }
    }

    const handleError = (message: string) => {
      error.value = {
        title: 'Configuration Error',
        message,
        severity: 'error',
        canRetry: true
      }
    }

    const retryConfiguration = () => {
      error.value = null
      // Additional retry logic if needed
    }

    return {
      selectedBoard,
      boardName,
      error,
      canProceed,
      onConfigSaved,
      handleError,
      retryConfiguration
    }
  }
})
</script>

<style scoped>
.configure {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.configuration-warning {
  text-align: center;
  padding: 2rem;
  background: var(--background-alt);
  border-radius: 8px;
  margin: 2rem 0;
}

.warning-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 3rem;
  padding: 1rem 0;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .configure {
    padding: 1rem;
  }

  .navigation-buttons {
    flex-direction: column;
    gap: 1rem;
  }

  .navigation-buttons .btn {
    width: 100%;
    text-align: center;
  }
}
</style>]]>
