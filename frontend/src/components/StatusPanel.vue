<template>
  <div class="panel">
    <h3>🎯 Actions</h3>
    <button @click="handleSave" :disabled="store.loading" class="button-primary">
      💾 Save Results
    </button>

    <div v-if="store.saveStatus" class="status-indicator status-success">
      {{ store.saveStatus }}
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
