<template>
  <div id="app">
    <header class="header">
      <h1>InnovateOS Klipper Installer</h1>
    </header>
    
    <main class="main-content">
      <div class="installation-steps">
        <!-- Schritt 1: Drucker auswählen -->
        <div class="step" :class="{ active: currentStep === 1 }">
          <h2>1. Drucker auswählen</h2>
          <div v-if="currentStep === 1">
            <select v-model="selectedPrinter" @change="onPrinterChange">
              <option value="">Bitte Drucker auswählen</option>
              <option v-for="printer in printers" :key="printer.id" :value="printer.id">
                {{ printer.manufacturer }} - {{ printer.name }}
              </option>
            </select>
            
            <!-- Board-Konfiguration -->
            <div class="board-config" v-if="selectedPrinter">
              <h3>Board-Konfiguration</h3>
              <div class="board-detection">
                <button @click="detectBoard" :disabled="boardDetectionInProgress">
                  {{ boardDetectionInProgress ? 'Suche Board...' : 'Board automatisch erkennen' }}
                </button>
                <span v-if="detectedBoard" class="detected-board">
                  Erkanntes Board: {{ detectedBoard }}
                </span>
              </div>
              
              <div class="board-settings">
                <div class="setting-group">
                  <label>Board-Typ:</label>
                  <select v-model="boardConfig.board">
                    <option value="STM32F103">STM32F103 (Ender 3)</option>
                    <option value="STM32F446">STM32F446 (Voron 2.4)</option>
                    <option value="STM32F407">STM32F407 (RatRig VCore)</option>
                  </select>
                </div>
                
                <div class="setting-group">
                  <label>Bootloader-Größe:</label>
                  <select v-model="boardConfig.bootloader">
                    <option :value="28672">28KiB (Standard)</option>
                    <option :value="32768">32KiB</option>
                  </select>
                </div>
                
                <div class="setting-group">
                  <label>Serieller Port:</label>
                  <select v-model="boardConfig.serial">
                    <option v-for="port in serialPorts" :key="port" :value="port">
                      {{ port }}
                    </option>
                  </select>
                  <button @click="refreshSerialPorts" class="refresh-button">
                    <span class="refresh-icon">↻</span>
                  </button>
                </div>
                
                <div class="setting-group">
                  <label>Baudrate:</label>
                  <select v-model="boardConfig.baud">
                    <option value="250000">250000 (Standard)</option>
                    <option value="115200">115200</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Schritt 2: Weboberfläche wählen -->
        <div class="step" :class="{ active: currentStep === 2 }">
          <h2>2. Weboberfläche wählen</h2>
          <div v-if="currentStep === 2">
            <div class="webInterface-options">
              <div class="webInterface-option" 
                   v-for="webInterface in webInterfaces" 
                   :key="webInterface.id"
                   :class="{ selected: selectedWebInterface === webInterface.id }"
                   @click="selectedWebInterface = webInterface.id">
                {{ webInterface.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- Schritt 3: Installation -->
        <div class="step" :class="{ active: currentStep === 3 }">
          <h2>3. Installation</h2>
          <div v-if="currentStep === 3">
            <div class="installation-progress">
              <div class="progress-step" v-for="(step, index) in installationSteps" 
                   :key="index"
                   :class="{ 
                     active: currentInstallStep === step.id,
                     completed: step.completed,
                     error: step.error
                   }">
                <div class="step-icon">
                  <span v-if="step.completed">✓</span>
                  <span v-else-if="step.error">✗</span>
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="step-content">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-description">{{ step.description }}</div>
                  <div v-if="step.error" class="step-error">{{ step.error }}</div>
                </div>
              </div>
            </div>
            
            <div class="progress-container">
              <div class="progress-bar" :style="{ width: installProgress + '%' }"></div>
              <div class="progress-label">{{ installProgress }}%</div>
            </div>
            
            <div class="status-message" :class="{ error: installationError }">
              {{ statusMessage }}
            </div>
            
            <div class="log-container" v-if="showLog">
              <div class="log-header">
                <span>Installations-Log</span>
                <button @click="showLog = false">Schließen</button>
              </div>
              <pre>{{ installationLog }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="navigation-buttons">
        <button @click="previousStep" 
                :disabled="currentStep === 1 || installationInProgress">
          Zurück
        </button>
        
        <button v-if="currentStep < 3" 
                @click="nextStep"
                :disabled="!canProceed || installationInProgress"
                :class="{ 'start-install': currentStep === 2 }">
          {{ currentStep === 2 ? 'Installation starten' : 'Weiter' }}
        </button>
        
        <button v-else-if="installationComplete" 
                @click="showLog = !showLog">
          {{ showLog ? 'Log ausblenden' : 'Log anzeigen' }}
        </button>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const currentStep = ref(1)
    const selectedPrinter = ref('')
    const selectedWebInterface = ref('')
    const installProgress = ref(0)
    const statusMessage = ref('')
    const installationLog = ref('')
    const printers = ref([])
    const webInterfaces = ref([])
    const showLog = ref(false)
    const installationComplete = ref(false)
    const installationError = ref(false)
    const installationInProgress = ref(false)
    const boardDetectionInProgress = ref(false)
    const detectedBoard = ref(null)
    const serialPorts = ref([])

    const boardConfig = ref({
      board: '',
      bootloader: 28672,
      serial: '',
      baud: 250000
    })

    const installationSteps = ref([
      {
        id: 'dependencies',
        title: 'Systemabhängigkeiten',
        description: 'Installation der benötigten Systempakete',
        completed: false,
        error: null
      },
      {
        id: 'klipper',
        title: 'Klipper',
        description: 'Klipper-Repository wird geklont',
        completed: false,
        error: null
      },
      {
        id: 'firmware',
        title: 'Firmware',
        description: 'Kompilierung und Upload der Firmware',
        completed: false,
        error: null
      },
      {
        id: 'config',
        title: 'Konfiguration',
        description: 'Einrichtung der Druckerkonfiguration',
        completed: false,
        error: null
      },
      {
        id: 'service',
        title: 'Systemdienst',
        description: 'Klipper-Dienst wird eingerichtet',
        completed: false,
        error: null
      }
    ])

    const currentInstallStep = ref('')

    const canProceed = computed(() => {
      if (currentStep.value === 1) {
        return selectedPrinter.value && boardConfig.value.board && boardConfig.value.serial
      }
      if (currentStep.value === 2) return selectedWebInterface.value
      return true
    })

    const loadPrinters = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/printers')
        printers.value = response.data.printers
      } catch (error) {
        console.error('Fehler beim Laden der Drucker:', error)
      }
    }

    const loadWebInterfaces = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/interfaces')
        webInterfaces.value = response.data.webInterfaces
      } catch (error) {
        console.error('Fehler beim Laden der Weboberflächen:', error)
      }
    }

    const detectBoard = async () => {
      boardDetectionInProgress.value = true
      try {
        const response = await axios.get('http://localhost:8000/api/detect-board')
        detectedBoard.value = response.data.board
        if (detectedBoard.value) {
          boardConfig.value.board = detectedBoard.value
        }
      } catch (error) {
        console.error('Fehler bei der Board-Erkennung:', error)
      } finally {
        boardDetectionInProgress.value = false
      }
    }

    const refreshSerialPorts = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/serial-ports')
        serialPorts.value = response.data.ports
      } catch (error) {
        console.error('Fehler beim Laden der seriellen Ports:', error)
      }
    }

    const onPrinterChange = async () => {
      if (selectedPrinter.value) {
        try {
          const response = await axios.get(`http://localhost:8000/api/printer-config/${selectedPrinter.value}`)
          boardConfig.value = { ...boardConfig.value, ...response.data.board_config }
        } catch (error) {
          console.error('Fehler beim Laden der Board-Konfiguration:', error)
        }
      }
    }

    const startInstallation = async () => {
      installationInProgress.value = true
      installationError.value = false
      currentInstallStep.value = 'dependencies'
      
      try {
        const response = await axios.post('http://localhost:8000/api/install', {
          printer_id: selectedPrinter.value,
          webInterface_id: selectedWebInterface.value,
          board_config: boardConfig.value
        })
        
        if (response.data.status === 'started') {
          // WebSocket-Verbindung für Live-Updates
          const ws = new WebSocket('ws://localhost:8000/ws')
          
          ws.onmessage = (event) => {
            const data = JSON.parse(event.data)
            installProgress.value = data.progress
            statusMessage.value = data.message
            
            if (data.step) {
              currentInstallStep.value = data.step
              const step = installationSteps.value.find(s => s.id === data.step)
              if (step) {
                step.completed = data.progress === 100
                step.error = data.error
              }
            }
            
            if (data.log) {
              installationLog.value += data.log + '\n'
            }
            
            if (data.error) {
              installationError.value = true
            }
            
            if (data.progress === 100) {
              installationComplete.value = true
              installationInProgress.value = false
              ws.close()
            }
          }
        }
      } catch (error) {
        console.error('Fehler beim Starten der Installation:', error)
        statusMessage.value = 'Fehler beim Starten der Installation'
        installationError.value = true
        installationInProgress.value = false
      }
    }

    const nextStep = () => {
      if (currentStep.value === 2) {
        startInstallation()
      }
      currentStep.value++
    }

    const previousStep = () => {
      if (currentStep.value > 1) {
        currentStep.value--
      }
    }

    onMounted(() => {
      loadPrinters()
      loadWebInterfaces()
      refreshSerialPorts()
    })

    return {
      currentStep,
      selectedPrinter,
      selectedWebInterface,
      installProgress,
      statusMessage,
      installationLog,
      printers,
      webInterfaces,
      canProceed,
      nextStep,
      previousStep,
      showLog,
      installationComplete,
      installationError,
      installationInProgress,
      boardDetectionInProgress,
      detectedBoard,
      boardConfig,
      serialPorts,
      installationSteps,
      currentInstallStep,
      detectBoard,
      refreshSerialPorts,
      onPrinterChange
    }
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.step {
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  opacity: 0.6;
}

.step.active {
  opacity: 1;
  border-color: #4CAF50;
}

.board-config {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.board-detection {
  margin-bottom: 15px;
}

.detected-board {
  margin-left: 10px;
  color: #4CAF50;
}

.board-settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.setting-group {
  display: flex;
  flex-direction: column;
}

.setting-group label {
  margin-bottom: 5px;
  font-weight: bold;
}

.refresh-button {
  padding: 5px 10px;
  margin-left: 5px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.3s;
}

.refresh-button:hover .refresh-icon {
  transform: rotate(180deg);
}

.installation-progress {
  margin-bottom: 20px;
}

.progress-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.progress-step.active {
  background-color: #e8f5e9;
  border-color: #4CAF50;
}

.progress-step.completed {
  background-color: #f1f8e9;
  border-color: #8bc34a;
}

.progress-step.error {
  background-color: #ffebee;
  border-color: #ef5350;
}

.step-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.step-description {
  color: #666;
  font-size: 0.9em;
}

.step-error {
  color: #d32f2f;
  margin-top: 5px;
  font-size: 0.9em;
}

.webInterface-options {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.webInterface-option {
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.webInterface-option.selected {
  border-color: #4CAF50;
  background-color: #e8f5e9;
}

.progress-container {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 20px 0;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.progress-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #000;
  font-size: 12px;
  font-weight: bold;
}

.status-message {
  margin: 10px 0;
  padding: 10px;
  border-radius: 4px;
}

.status-message.error {
  background-color: #ffebee;
  color: #d32f2f;
}

.log-container {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
  margin-top: 20px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #4CAF50;
  color: white;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

button.start-install {
  background-color: #2196F3;
}

button.start-install:hover:not(:disabled) {
  background-color: #1976D2;
}

select {
  width: 100%;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 16px;
  background-color: white;
}

select:focus {
  outline: none;
  border-color: #4CAF50;
}
</style>
