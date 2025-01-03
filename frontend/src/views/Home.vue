<![CDATA[<template>
  <div class="home">
    <div class="welcome-section">
      <h1>Welcome to InnovateOS Klipper Installer</h1>
      <p class="subtitle">Simple, fast, and reliable way to install Klipper on your 3D printer</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <img src="@/assets/icons/settings.svg" alt="Easy Setup" class="feature-icon">
        <h3>Easy Setup</h3>
        <p>Automated installation process with step-by-step guidance</p>
      </div>

      <div class="feature-card">
        <img src="@/assets/icons/success.svg" alt="Board Support" class="feature-icon">
        <h3>Wide Board Support</h3>
        <p>Compatible with most popular 3D printer control boards</p>
      </div>

      <div class="feature-card">
        <img src="@/assets/icons/settings.svg" alt="Configuration" class="feature-icon">
        <h3>Smart Configuration</h3>
        <p>Intelligent default settings based on your hardware</p>
      </div>
    </div>

    <div class="action-section">
      <h2>Ready to start?</h2>
      <p>Follow our simple installation process to get Klipper running on your printer</p>
      <router-link to="/select-board" class="btn btn-primary">
        Start Installation
      </router-link>
    </div>

    <div class="requirements-section">
      <h3>System Requirements</h3>
      <ul>
        <li>Raspberry Pi or compatible SBC</li>
        <li>Compatible 3D printer control board</li>
        <li>USB connection to printer</li>
        <li>Internet connection for installation</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useMainStore } from '@/store'

export default defineComponent({
  name: 'Home',
  
  setup() {
    const store = useMainStore()

    // Reset the store state when entering the home page
    store.resetState()

    return {}
  }
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-section {
  text-align: center;
  margin-bottom: 4rem;
}

.welcome-section h1 {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--text-light);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: var(--background-alt);
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
}

.action-section {
  text-align: center;
  margin: 4rem 0;
  padding: 3rem;
  background: var(--background-alt);
  border-radius: 12px;
}

.action-section h2 {
  margin-bottom: 1rem;
}

.action-section .btn {
  margin-top: 2rem;
  font-size: 1.2rem;
  padding: 1rem 2rem;
}

.requirements-section {
  max-width: 600px;
  margin: 0 auto;
}

.requirements-section ul {
  list-style-type: none;
  padding: 0;
}

.requirements-section li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
}

.requirements-section li::before {
  content: "•";
  color: var(--primary-color);
  position: absolute;
  left: 0;
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }

  .welcome-section h1 {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>]]>
