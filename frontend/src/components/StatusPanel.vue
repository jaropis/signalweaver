<template>
  <div class="status-panel panel">
    <div class="status-content">
      <button
        class="save-btn"
        @click="handleSave"
        :disabled="store.loading"
      >
        <v-icon size="16">mdi-content-save</v-icon>
        <span>Save Results</span>
      </button>

      <div v-if="store.saveStatus" class="status-message">
        <v-icon size="14" color="success">mdi-check-circle</v-icon>
        {{ store.saveStatus }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { useECGStore } from '../stores/ecg'

const store = useECGStore()

async function handleSave() {
  await store.save()
}
</script>

<style scoped>
.status-panel {
  padding: 12px 16px;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: #2e7d32;
}
</style>
