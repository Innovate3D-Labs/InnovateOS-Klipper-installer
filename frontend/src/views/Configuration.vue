`<template>
  <div class="configuration-view">
    <div class="config-container">
      <!-- Profile Selection -->
      <div class="section">
        <h2>Printer Profile</h2>
        <div class="profile-selector">
          <select v-model="selectedProfile">
            <option value="">Select a printer profile</option>
            <option
              v-for="profile in profiles"
              :key="profile.name"
              :value="profile"
            >
              {{ profile.manufacturer }} {{ profile.model }}
            </option>
          </select>
          <button
            class="btn-secondary"
            @click="loadProfile"
            :disabled="!selectedProfile"
          >
            Load Profile
          </button>
        </div>
      </div>

      <!-- Printer Configuration -->
      <form @submit.prevent="saveConfiguration" class="config-form">
        <!-- Basic Settings -->
        <div class="section">
          <h3>Basic Settings</h3>
          <div class="form-group">
            <label for="printerName">Printer Name</label>
            <input
              id="printerName"
              v-model="config.name"
              type="text"
              required
            />
          </div>
        </div>

        <!-- Dimensions -->
        <div class="section">
          <h3>Printer Dimensions</h3>
          <div class="form-grid">
            <div class="form-group">
              <label for="bedSizeX">Bed Size X (mm)</label>
              <input
                id="bedSizeX"
                v-model.number="config.dimensions.x"
                type="number"
                required
                min="0"
              />
            </div>
            <div class="form-group">
              <label for="bedSizeY">Bed Size Y (mm)</label>
              <input
                id="bedSizeY"
                v-model.number="config.dimensions.y"
                type="number"
                required
                min="0"
              />
            </div>
            <div class="form-group">
              <label for="bedSizeZ">Bed Size Z (mm)</label>
              <input
                id="bedSizeZ"
                v-model.number="config.dimensions.z"
                type="number"
                required
                min="0"
              />
            </div>
          </div>
        </div>

        <!-- Speeds -->
        <div class="section">
          <h3>Speed Settings</h3>
          <div class="form-grid">
            <div class="form-group">
              <label for="maxVelocity">Max Velocity (mm/s)</label>
              <input
                id="maxVelocity"
                v-model.number="config.speeds.max_velocity"
                type="number"
                required
                min="0"
              />
            </div>
            <div class="form-group">
              <label for="maxAccel">Max Acceleration (mm/s²)</label>
              <input
                id="maxAccel"
                v-model.number="config.speeds.max_accel"
                type="number"
                required
                min="0"
              />
            </div>
            <div class="form-group">
              <label for="maxZVelocity">Max Z Velocity (mm/s)</label>
              <input
                id="maxZVelocity"
                v-model.number="config.speeds.max_z_velocity"
                type="number"
                required
                min="0"
              />
            </div>
            <div class="form-group">
              <label for="maxZAccel">Max Z Acceleration (mm/s²)</label>
              <input
                id="maxZAccel"
                v-model.number="config.speeds.max_z_accel"
                type="number"
                required
                min="0"
              />
            </div>
          </div>
        </div>

        <!-- Features -->
        <div class="section">
          <h3>Features</h3>
          <div class="features-grid">
            <div class="feature-toggle">
              <input
                id="pressureAdvance"
                v-model="config.features.pressure_advance"
                type="checkbox"
              />
              <label for="pressureAdvance">Pressure Advance</label>
            </div>
            <div class="feature-toggle">
              <input
                id="inputShaping"
                v-model="config.features.input_shaping"
                type="checkbox"
              />
              <label for="inputShaping">Input Shaping</label>
            </div>
            <div class="feature-toggle">
              <input
                id="bedMesh"
                v-model="config.features.bed_mesh"
                type="checkbox"
              />
              <label for="bedMesh">Bed Mesh Leveling</label>
            </div>
            <div class="feature-toggle">
              <input
                id="bltouch"
                v-model="config.features.bltouch"
                type="checkbox"
              />
              <label for="bltouch">BLTouch</label>
            </div>
          </div>
        </div>

        <!-- Preview -->
        <div class="section" v-if="configPreview">
          <h3>Configuration Preview</h3>
          <div class="config-preview">
            <pre><code>{{ configPreview }}</code></pre>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button
            type="button"
            class="btn-secondary"
            @click="previewConfig"
            :disabled="!isValid"
          >
            Preview
          </button>
          <button
            type="submit"
            class="btn-primary"
            :disabled="!isValid"
          >
            Save Configuration
          </button>
        </div>
      </form>

      <!-- Backup/Restore -->
      <div class="section">
        <h3>Backup & Restore</h3>
        <div class="backup-actions">
          <button
            class="btn-secondary"
            @click="backupConfig"
            :disabled="!hasConfig"
          >
            Backup Configuration
          </button>
          <button
            class="btn-secondary"
            @click="restoreConfig"
          >
            Restore from Backup
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useConfigStore } from '@/store/config'
import { validateConfig } from '@/utils/validators'
import type { PrinterProfile, PrinterConfig } from '@/types'

const router = useRouter()
const configStore = useConfigStore()

// State
const selectedProfile = ref<PrinterProfile | null>(null)
const profiles = ref<PrinterProfile[]>([])
const configPreview = ref<string>('')
const config = ref<PrinterConfig>({
  name: '',
  dimensions: { x: 0, y: 0, z: 0 },
  speeds: {
    max_velocity: 0,
    max_accel: 0,
    max_z_velocity: 0,
    max_z_accel: 0
  },
  features: {
    pressure_advance: false,
    input_shaping: false,
    bed_mesh: false,
    bltouch: false
  }
})

// Computed
const isValid = computed(() => {
  const result = validateConfig(config.value)
  return result.success
})

const hasConfig = computed(() => config.value.name !== '')

// Methods
const loadProfile = async () => {
  if (selectedProfile.value) {
    const profile = await configStore.loadProfile(selectedProfile.value.name)
    if (profile) {
      config.value = { ...profile }
    }
  }
}

const previewConfig = async () => {
  configPreview.value = await configStore.generatePreview(config.value)
}

const saveConfiguration = async () => {
  if (isValid.value) {
    await configStore.saveConfig(config.value)
    router.push('/installation')
  }
}

const backupConfig = async () => {
  const success = await configStore.backupConfig(config.value.name)
  if (success) {
    // Show success message
  }
}

const restoreConfig = async () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const restored = await configStore.restoreConfig(file)
      if (restored) {
        config.value = restored
      }
    }
  }
  input.click()
}

// Lifecycle
onMounted(async () => {
  profiles.value = await configStore.getProfiles()
  const savedConfig = configStore.getCurrentConfig()
  if (savedConfig) {
    config.value = savedConfig
  }
})
</script>

<style scoped>
.configuration-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.config-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.section {
  margin-bottom: 2rem;
}

.section h2, .section h3 {
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.profile-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.profile-selector select {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.feature-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.config-preview {
  background: var(--color-background-dark);
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
}

.config-preview pre {
  margin: 0;
  font-family: monospace;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.backup-actions {
  display: flex;
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
