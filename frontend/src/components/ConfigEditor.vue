<![CDATA[<template>
  <div class="config-editor">
    <form @submit.prevent="saveConfig" class="config-form">
      <!-- Printer Basic Info -->
      <div class="form-section">
        <h3>Basic Information</h3>
        <div class="form-group">
          <label for="printerName">Printer Name</label>
          <input
            id="printerName"
            v-model="config.printerName"
            type="text"
            required
            :disabled="loading"
          >
        </div>
      </div>

      <!-- Printer Dimensions -->
      <div class="form-section">
        <h3>Printer Dimensions</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="dimensionX">X Axis (mm)</label>
            <input
              id="dimensionX"
              v-model.number="config.dimensions.x"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="dimensionY">Y Axis (mm)</label>
            <input
              id="dimensionY"
              v-model.number="config.dimensions.y"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="dimensionZ">Z Axis (mm)</label>
            <input
              id="dimensionZ"
              v-model.number="config.dimensions.z"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
        </div>
      </div>

      <!-- Maximum Velocities -->
      <div class="form-section">
        <h3>Maximum Velocities</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="velocityX">X Axis (mm/s)</label>
            <input
              id="velocityX"
              v-model.number="config.maxVelocity.x"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="velocityY">Y Axis (mm/s)</label>
            <input
              id="velocityY"
              v-model.number="config.maxVelocity.y"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="velocityZ">Z Axis (mm/s)</label>
            <input
              id="velocityZ"
              v-model.number="config.maxVelocity.z"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
        </div>
      </div>

      <!-- Maximum Accelerations -->
      <div class="form-section">
        <h3>Maximum Accelerations</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="accelX">X Axis (mm/s²)</label>
            <input
              id="accelX"
              v-model.number="config.maxAcceleration.x"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="accelY">Y Axis (mm/s²)</label>
            <input
              id="accelY"
              v-model.number="config.maxAcceleration.y"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="accelZ">Z Axis (mm/s²)</label>
            <input
              id="accelZ"
              v-model.number="config.maxAcceleration.z"
              type="number"
              min="0"
              required
              :disabled="loading"
            >
          </div>
        </div>
      </div>

      <!-- Advanced Settings Toggle -->
      <div class="form-section">
        <button 
          type="button"
          class="btn btn-outline"
          @click="showAdvanced = !showAdvanced"
        >
          {{ showAdvanced ? 'Hide' : 'Show' }} Advanced Settings
        </button>
      </div>

      <!-- Advanced Settings -->
      <div v-if="showAdvanced" class="form-section advanced-settings">
        <h3>Advanced Settings</h3>
        <div class="form-group">
          <label for="firmwareVersion">Firmware Version</label>
          <select
            id="firmwareVersion"
            v-model="config.firmwareVersion"
            :disabled="loading"
          >
            <option value="latest">Latest</option>
            <option value="stable">Stable</option>
            <option value="legacy">Legacy</option>
          </select>
        </div>

        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="config.enablePressureAdvance"
              :disabled="loading"
            >
            Enable Pressure Advance
          </label>
        </div>

        <div class="form-group">
          <label>
            <input
              type="checkbox"
              v-model="config.enableInputShaping"
              :disabled="loading"
            >
            Enable Input Shaping
          </label>
        </div>
      </div>

      <div class="form-actions">
        <button
          type="button"
          class="btn btn-outline"
          @click="loadDefaults"
          :disabled="loading"
        >
          Load Defaults
        </button>
        
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="loading || !isValid"
        >
          Save Configuration
        </button>
      </div>
    </form>

    <ErrorDisplay
      v-if="error"
      :error="error"
      @dismiss="error = null"
      @retry="validateConfig"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useMainStore } from '@/store'
import { useApi } from '@/composables/useApi'
import ErrorDisplay from './ErrorDisplay.vue'
import type { PrinterConfig } from '@/types'

export default defineComponent({
  name: 'ConfigEditor',

  components: {
    ErrorDisplay
  },

  setup(props, { emit }) {
    const store = useMainStore()
    const { getDefaultConfig, validateConfig: validateConfigApi, saveConfig: saveConfigApi } = useApi()

    const loading = ref(false)
    const error = ref(null)
    const showAdvanced = ref(false)

    const defaultConfig: PrinterConfig = {
      printerName: '',
      dimensions: { x: 0, y: 0, z: 0 },
      maxVelocity: { x: 0, y: 0, z: 0 },
      maxAcceleration: { x: 0, y: 0, z: 0 },
      firmwareVersion: 'latest',
      enablePressureAdvance: false,
      enableInputShaping: false
    }

    const config = ref<PrinterConfig>({ ...defaultConfig })

    const isValid = computed(() => {
      return config.value.printerName &&
        config.value.dimensions.x > 0 &&
        config.value.dimensions.y > 0 &&
        config.value.dimensions.z > 0 &&
        config.value.maxVelocity.x > 0 &&
        config.value.maxVelocity.y > 0 &&
        config.value.maxVelocity.z > 0 &&
        config.value.maxAcceleration.x > 0 &&
        config.value.maxAcceleration.y > 0 &&
        config.value.maxAcceleration.z > 0
    })

    const loadDefaults = async () => {
      loading.value = true
      error.value = null

      try {
        const defaults = await getDefaultConfig()
        if (defaults) {
          config.value = defaults
        }
      } catch (e: any) {
        error.value = {
          title: 'Failed to Load Defaults',
          message: e.message,
          severity: 'error'
        }
      } finally {
        loading.value = false
      }
    }

    const validateConfig = async () => {
      loading.value = true
      error.value = null

      try {
        const result = await validateConfigApi(config.value)
        if (!result.valid) {
          error.value = {
            title: 'Invalid Configuration',
            message: 'Please check the following errors:',
            details: result.errors?.join('\n'),
            severity: 'error'
          }
          return false
        }
        return true
      } catch (e: any) {
        error.value = {
          title: 'Validation Failed',
          message: e.message,
          severity: 'error'
        }
        return false
      } finally {
        loading.value = false
      }
    }

    const saveConfig = async () => {
      if (!isValid.value) return

      const isValidConfig = await validateConfig()
      if (!isValidConfig) return

      loading.value = true
      error.value = null

      try {
        await saveConfigApi(config.value)
        store.setPrinterConfig(config.value)
        emit('config-saved', config.value)
      } catch (e: any) {
        error.value = {
          title: 'Save Failed',
          message: e.message,
          severity: 'error'
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      if (store.printerConfig) {
        config.value = { ...store.printerConfig }
      } else {
        loadDefaults()
      }
    })

    return {
      config,
      loading,
      error,
      showAdvanced,
      isValid,
      loadDefaults,
      saveConfig
    }
  }
})
</script>

<style scoped>
.config-editor {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: var(--background-alt);
  padding: 1.5rem;
  border-radius: 8px;
}

.form-section h3 {
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--text-light);
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--background-color);
  color: var(--text-color);
}

.form-group input[type="checkbox"] {
  margin-right: 0.5rem;
}

.advanced-settings {
  border: 1px dashed var(--border-color);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .config-editor {
    padding: 1rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
  }
}
</style>]]>
