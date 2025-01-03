<![CDATA[<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>Page Not Found</h1>
      <p>Sorry, we couldn't find the page you're looking for.</p>
      
      <div class="suggestions">
        <h2>You might want to:</h2>
        <ul>
          <li>
            <router-link to="/" class="link">
              Return to Home
            </router-link>
          </li>
          <li>
            <router-link 
              v-if="lastValidRoute"
              :to="lastValidRoute"
              class="link"
            >
              Go Back to Previous Page
            </router-link>
          </li>
          <li>
            <router-link to="/config" class="link">
              Check Printer Configuration
            </router-link>
          </li>
          <li>
            <a 
              href="https://docs.innovateos.dev"
              target="_blank"
              rel="noopener noreferrer"
              class="link"
            >
              Visit Documentation
            </a>
          </li>
        </ul>
      </div>

      <div class="support">
        <p>
          If you believe this is a bug, please 
          <a 
            href="https://github.com/InnovateOS/Klipper-installer/issues"
            target="_blank"
            rel="noopener noreferrer"
            class="link"
          >
            report it
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'NotFound',

  setup() {
    const router = useRouter()
    const lastValidRoute = ref<string | null>(null)

    onMounted(() => {
      // Get the last valid route from history
      const history = router.options.history
      const previousRoute = history.state.back
      
      if (previousRoute && previousRoute !== router.currentRoute.value.fullPath) {
        lastValidRoute.value = previousRoute
      }
    })

    return {
      lastValidRoute
    }
  }
})
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.not-found-content {
  max-width: 600px;
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: var(--primary-color);
  line-height: 1;
  margin-bottom: 1rem;
  opacity: 0.5;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  color: var(--text-light);
  margin-bottom: 2rem;
}

.suggestions {
  margin: 2rem 0;
  text-align: left;
}

.suggestions h2 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.suggestions ul {
  list-style: none;
  padding: 0;
}

.suggestions li {
  margin: 0.5rem 0;
}

.link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.3s ease;
}

.link:hover {
  color: var(--primary-color-dark);
  text-decoration: underline;
}

.support {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .error-code {
    font-size: 6rem;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>]]>
