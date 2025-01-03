<![CDATA[<template>
  <div class="about">
    <div class="about-header">
      <h1>About InnovateOS Klipper Installer</h1>
      <p class="version">Version {{ version }}</p>
    </div>

    <div class="about-content">
      <section class="about-section">
        <h2>Overview</h2>
        <p>
          InnovateOS Klipper Installer is an open-source tool designed to simplify
          the installation and configuration of Klipper firmware on 3D printers.
          Our goal is to make advanced 3D printing technology accessible to everyone.
        </p>
      </section>

      <section class="about-section">
        <h2>Features</h2>
        <ul class="feature-list">
          <li>
            <span class="feature-icon">🔧</span>
            <div class="feature-info">
              <h3>Easy Setup</h3>
              <p>Simple step-by-step installation process</p>
            </div>
          </li>
          <li>
            <span class="feature-icon">🎯</span>
            <div class="feature-info">
              <h3>Board Support</h3>
              <p>Wide range of 3D printer control boards supported</p>
            </div>
          </li>
          <li>
            <span class="feature-icon">⚡</span>
            <div class="feature-info">
              <h3>Smart Configuration</h3>
              <p>Intelligent default settings based on your hardware</p>
            </div>
          </li>
          <li>
            <span class="feature-icon">🔄</span>
            <div class="feature-info">
              <h3>Auto Updates</h3>
              <p>Keeps your firmware up to date automatically</p>
            </div>
          </li>
        </ul>
      </section>

      <section class="about-section">
        <h2>System Requirements</h2>
        <div class="requirements-grid">
          <div class="requirement">
            <h3>Operating System</h3>
            <ul>
              <li>Linux (Recommended)</li>
              <li>Windows 10/11</li>
              <li>macOS 10.15+</li>
            </ul>
          </div>
          <div class="requirement">
            <h3>Hardware</h3>
            <ul>
              <li>Compatible 3D printer board</li>
              <li>USB connection</li>
              <li>Internet connection</li>
            </ul>
          </div>
          <div class="requirement">
            <h3>Software</h3>
            <ul>
              <li>Python 3.7+</li>
              <li>Git</li>
              <li>Web browser</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2>Contributors</h2>
        <div class="contributors">
          <div 
            v-for="contributor in contributors"
            :key="contributor.id"
            class="contributor"
          >
            <img 
              :src="contributor.avatar"
              :alt="contributor.name"
              class="contributor-avatar"
            >
            <div class="contributor-info">
              <h3>{{ contributor.name }}</h3>
              <p>{{ contributor.role }}</p>
              <div class="contributor-links">
                <a 
                  v-if="contributor.github"
                  :href="contributor.github"
                  target="_blank"
                  class="social-link"
                >
                  GitHub
                </a>
                <a 
                  v-if="contributor.twitter"
                  :href="contributor.twitter"
                  target="_blank"
                  class="social-link"
                >
                  Twitter
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="about-section">
        <h2>License</h2>
        <p>
          InnovateOS Klipper Installer is open source software licensed under the
          MIT license. You are free to use, modify, and distribute this software
          according to the terms of the license.
        </p>
        <a 
          href="https://github.com/InnovateOS/Klipper-installer/blob/main/LICENSE"
          target="_blank"
          class="license-link"
        >
          View License
        </a>
      </section>

      <section class="about-section">
        <h2>Support</h2>
        <div class="support-links">
          <a 
            href="https://github.com/InnovateOS/Klipper-installer"
            target="_blank"
            class="support-link"
          >
            GitHub Repository
          </a>
          <a 
            href="https://docs.innovateos.dev"
            target="_blank"
            class="support-link"
          >
            Documentation
          </a>
          <a 
            href="https://github.com/InnovateOS/Klipper-installer/issues"
            target="_blank"
            class="support-link"
          >
            Report an Issue
          </a>
          <a 
            href="https://discord.gg/innovateos"
            target="_blank"
            class="support-link"
          >
            Join Discord
          </a>
        </div>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'About',

  setup() {
    const version = ref('1.0.0')
    
    const contributors = ref([
      {
        id: 1,
        name: 'John Doe',
        role: 'Lead Developer',
        avatar: 'https://github.com/johndoe.png',
        github: 'https://github.com/johndoe',
        twitter: 'https://twitter.com/johndoe'
      },
      // Add more contributors as needed
    ])

    return {
      version,
      contributors
    }
  }
})
</script>

<style scoped>
.about {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.about-header {
  text-align: center;
  margin-bottom: 3rem;
}

.version {
  color: var(--text-light);
}

.about-section {
  margin-bottom: 3rem;
}

.about-section h2 {
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}

.feature-list {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-list li {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-alt);
  border-radius: 8px;
}

.feature-icon {
  font-size: 1.5rem;
}

.feature-info h3 {
  margin: 0 0 0.5rem 0;
}

.feature-info p {
  margin: 0;
  color: var(--text-light);
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.requirement {
  background: var(--background-alt);
  padding: 1.5rem;
  border-radius: 8px;
}

.requirement h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
}

.requirement ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirement li {
  padding: 0.5rem 0;
  color: var(--text-light);
}

.contributors {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.contributor {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-alt);
  border-radius: 8px;
}

.contributor-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
}

.contributor-info h3 {
  margin: 0 0 0.25rem 0;
}

.contributor-info p {
  margin: 0;
  color: var(--text-light);
}

.contributor-links {
  margin-top: 0.5rem;
}

.social-link {
  color: var(--primary-color);
  text-decoration: none;
  margin-right: 1rem;
}

.license-link,
.support-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: var(--background-alt);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  margin-top: 1rem;
}

.support-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .about {
    padding: 1rem;
  }

  .feature-list,
  .requirements-grid,
  .contributors,
  .support-links {
    grid-template-columns: 1fr;
  }
}
</style>]]>
