<![CDATA[<template>
  <div class="installation-complete">
    <div class="complete-content">
      <div class="status-icon">
        <img 
          src="@/assets/icons/success.svg"
          alt="Success"
          class="success-icon"
        >
      </div>

      <h1>Installation Complete!</h1>
      <p class="subtitle">
        Klipper has been successfully installed on your printer
      </p>

      <div class="installation-summary">
        <h2>Installation Summary</h2>
        <div class="summary-items">
          <div class="summary-item">
            <h3>Board Information</h3>
            <p>{{ boardInfo }}</p>
          </div>
          <div class="summary-item">
            <h3>Firmware Version</h3>
            <p>{{ firmwareVersion }}</p>
          </div>
          <div class="summary-item">
            <h3>Installation Time</h3>
            <p>{{ installationTime }}</p>
          </div>
        </div>
      </div>

      <div class="next-steps">
        <h2>Next Steps</h2>
        <div class="steps-grid">
          <div 
            v-for="(step, index) in nextSteps"
            :key="index"
            class="step-card"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
            <a 
              v-if="step.link"
              :href="step.link"
              target="_blank"
              rel="noopener noreferrer"
              class="step-link"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button 
          @click="downloadLog"
          class="btn btn-outline"
        >
          Download Installation Log
        </button>
        <button 
          @click="$router.push('/config')"
          class="btn btn-primary"
        >
          Configure Printer
        </button>
      </div>

      <div class="support-info">
        <p>
          Need help? Check out our 
          <a 
            href="https://docs.innovateos.dev/getting-started"
            target="_blank"
            rel="noopener noreferrer"
          >
            documentation
          </a>
          or join our 
          <a 
            href="https://discord.gg/innovateos"
            target="_blank"
            rel="noopener noreferrer"
          >
            Discord community
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useInstallationStore } from '@/store/installation'
import { formatDuration } from '@/utils/time'

export default defineComponent({
  name: 'InstallationComplete',

  setup() {
    const router = useRouter()
    const installationStore = useInstallationStore()

    const boardInfo = computed(() => {
      const board = installationStore.selectedBoard
      return board ? `${board.name} (${board.port})` : 'Unknown'
    })

    const firmwareVersion = computed(() => {
      return installationStore.firmwareVersion || 'Latest'
    })

    const installationTime = computed(() => {
      const duration = installationStore.installationDuration
      return formatDuration(duration)
    })

    const nextSteps = [
      {
        title: 'Configure Your Printer',
        description: 'Set up your printer parameters and calibrate the axes.',
        link: 'https://docs.innovateos.dev/configuration'
      },
      {
        title: 'Connect to Klipper',
        description: 'Learn how to connect and control your printer using Klipper.',
        link: 'https://docs.innovateos.dev/connection'
      },
      {
        title: 'First Print',
        description: 'Follow our guide for your first print with Klipper.',
        link: 'https://docs.innovateos.dev/first-print'
      },
      {
        title: 'Advanced Features',
        description: 'Explore advanced features like pressure advance and input shaping.',
        link: 'https://docs.innovateos.dev/advanced'
      }
    ]

    const downloadLog = () => {
      const logs = installationStore.installationLogs
      const logText = logs
        .map(log => `[${log.timestamp}] [${log.level}] ${log.message}`)
        .join('\n')

      const blob = new Blob([logText], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `klipper-installation-${new Date().toISOString()}.log`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    return {
      boardInfo,
      firmwareVersion,
      installationTime,
      nextSteps,
      downloadLog
    }
  }
})
</script>

<style scoped>
.installation-complete {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.complete-content {
  text-align: center;
}

.status-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 2rem;
}

.success-icon {
  width: 100%;
  height: 100%;
  color: var(--success-color);
}

h1 {
  font-size: 2.5rem;
  color: var(--success-color);
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--text-light);
  margin-bottom: 3rem;
}

.installation-summary {
  margin: 3rem 0;
}

.summary-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.summary-item {
  background: var(--background-alt);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: left;
}

.summary-item h3 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
}

.summary-item p {
  margin: 0;
  color: var(--text-light);
}

.next-steps {
  margin: 3rem 0;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.step-card {
  background: var(--background-alt);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: left;
  position: relative;
}

.step-number {
  position: absolute;
  top: -1rem;
  left: -1rem;
  width: 2.5rem;
  height: 2.5rem;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.step-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
}

.step-card p {
  margin: 0 0 1rem 0;
  color: var(--text-light);
}

.step-link {
  color: var(--primary-color);
  text-decoration: none;
}

.step-link:hover {
  text-decoration: underline;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin: 3rem 0;
}

.support-info {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.support-info a {
  color: var(--primary-color);
  text-decoration: none;
}

.support-info a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .installation-complete {
    padding: 1rem;
  }

  .status-icon {
    width: 80px;
    height: 80px;
  }

  h1 {
    font-size: 2rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .btn {
    width: 100%;
  }
}
</style>]]>
