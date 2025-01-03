<![CDATA[<template>
  <div class="board-selector">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>Loading available boards...</p>
    </div>

    <div class="search-box">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search for your board..."
        :disabled="loading"
      >
    </div>

    <div class="boards-grid">
      <div 
        v-for="board in filteredBoards" 
        :key="board.id"
        class="board-card"
        :class="{ 
          'selected': selectedBoard?.id === board.id,
          'disabled': loading 
        }"
        @click="selectBoard(board)"
      >
        <img :src="board.image" :alt="board.name">
        <h3>{{ board.name }}</h3>
        <p>{{ board.description }}</p>
      </div>
    </div>

    <div class="board-details" v-if="selectedBoard">
      <h3>Selected Board: {{ selectedBoard.name }}</h3>
      <div class="specs">
        <div class="spec-item">
          <span class="label">Processor:</span>
          <span>{{ selectedBoard.processor }}</span>
        </div>
        <div class="spec-item">
          <span class="label">Flash Size:</span>
          <span>{{ selectedBoard.flashSize }}</span>
        </div>
        <div class="spec-item">
          <span class="label">Interfaces:</span>
          <span>{{ selectedBoard.interfaces.join(', ') }}</span>
        </div>
      </div>
      <button 
        class="confirm-button"
        @click="confirmSelection"
        :disabled="loading || !selectedBoard"
      >
        Continue with this board
      </button>
    </div>

    <ErrorDisplay
      v-if="error"
      :error="error"
      @dismiss="error = null"
      @retry="loadBoards"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useMainStore } from '@/store'
import { useApi } from '@/composables/useApi'
import ErrorDisplay from './ErrorDisplay.vue'
import type { Board, ErrorInfo } from '@/types'

export default defineComponent({
  name: 'BoardSelector',
  
  components: {
    ErrorDisplay
  },

  setup(props, { emit }) {
    const store = useMainStore()
    const { getBoards, loading, error } = useApi()
    
    const searchQuery = ref('')
    const boards = ref<Board[]>([])
    const selectedBoard = ref<Board | null>(store.selectedBoard)

    const filteredBoards = computed(() => {
      const query = searchQuery.value.toLowerCase()
      return boards.value.filter(board => 
        board.name.toLowerCase().includes(query) ||
        board.description.toLowerCase().includes(query)
      )
    })

    const loadBoards = async () => {
      const result = await getBoards()
      if (result) {
        boards.value = result
      }
    }

    const selectBoard = (board: Board) => {
      selectedBoard.value = board
    }

    const confirmSelection = async () => {
      if (selectedBoard.value) {
        try {
          store.setSelectedBoard(selectedBoard.value)
          emit('board-selected', selectedBoard.value)
        } catch (e: any) {
          store.addError({
            title: 'Selection Error',
            message: 'Failed to save board selection',
            severity: 'error',
            details: e.message
          })
        }
      }
    }

    onMounted(() => {
      loadBoards()
    })

    return {
      searchQuery,
      boards,
      selectedBoard,
      filteredBoards,
      loading,
      error,
      selectBoard,
      confirmSelection
    }
  }
})
</script>

<style scoped>
/* Existing styles remain the same */

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.board-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Rest of the existing styles... */
</style>]]>
