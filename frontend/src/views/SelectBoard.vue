<![CDATA[<template>
  <div class="select-board">
    <div class="page-header">
      <h1>Select Your Board</h1>
      <p>Choose your 3D printer control board to begin the installation process</p>
    </div>

    <BoardSelector
      @board-selected="onBoardSelected"
      @error="handleError"
    />

    <ErrorDisplay
      v-if="error"
      :error="error"
      @dismiss="error = null"
      @retry="retryBoardSelection"
    />

    <div class="navigation-buttons">
      <router-link to="/" class="btn btn-outline">
        Back to Home
      </router-link>
      <router-link 
        v-if="canProceed"
        to="/configure" 
        class="btn btn-primary"
      >
        Continue to Configuration
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useMainStore } from '@/store'
import BoardSelector from '@/components/BoardSelector.vue'
import ErrorDisplay from '@/components/ErrorDisplay.vue'
import type { Board, ErrorInfo } from '@/types'

export default defineComponent({
  name: 'SelectBoard',

  components: {
    BoardSelector,
    ErrorDisplay
  },

  setup() {
    const store = useMainStore()
    const error = ref<ErrorInfo | null>(null)

    const canProceed = computed(() => store.selectedBoard !== null)

    const onBoardSelected = (board: Board) => {
      try {
        store.setSelectedBoard(board)
        error.value = null
      } catch (e) {
        handleError('Failed to select board')
      }
    }

    const handleError = (message: string) => {
      error.value = {
        title: 'Board Selection Error',
        message,
        severity: 'error',
        canRetry: true
      }
    }

    const retryBoardSelection = () => {
      error.value = null
      // Additional retry logic if needed
    }

    return {
      error,
      canProceed,
      onBoardSelected,
      handleError,
      retryBoardSelection
    }
  }
})
</script>

<style scoped>
.select-board {
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

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 3rem;
  padding: 1rem 0;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .select-board {
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
