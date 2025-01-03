<![CDATA[<template>
  <div class="dialog-overlay" @click="$emit('cancel')">
    <div class="dialog" @click.stop>
      <div class="dialog-header">
        <h3>{{ title }}</h3>
        <button 
          class="close-button"
          @click="$emit('cancel')"
        >
          ×
        </button>
      </div>

      <div class="dialog-content">
        <p>{{ message }}</p>
      </div>

      <div class="dialog-actions">
        <button 
          @click="$emit('cancel')"
          class="btn btn-outline"
        >
          {{ cancelText }}
        </button>
        <button 
          @click="$emit('confirm')"
          class="btn"
          :class="confirmButtonClass"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'ConfirmDialog',

  props: {
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    type: {
      type: String,
      default: 'primary',
      validator: (value: string) => {
        return ['primary', 'danger', 'warning'].includes(value)
      }
    }
  },

  emits: ['confirm', 'cancel'],

  setup(props) {
    const confirmButtonClass = computed(() => {
      switch (props.type) {
        case 'danger': return 'btn-danger'
        case 'warning': return 'btn-warning'
        default: return 'btn-primary'
      }
    })

    return {
      confirmButtonClass
    }
  }
})
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--background-color);
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-light);
  cursor: pointer;
  padding: 0.5rem;
  line-height: 1;
}

.close-button:hover {
  color: var(--text-color);
}

.dialog-content {
  padding: 1.5rem;
}

.dialog-content p {
  margin: 0;
  color: var(--text-light);
}

.dialog-actions {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

@media (max-width: 768px) {
  .dialog {
    width: 95%;
  }

  .dialog-actions {
    flex-direction: column-reverse;
  }

  .dialog-actions .btn {
    width: 100%;
  }
}
</style>]]>
