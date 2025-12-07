<template>
  <div class="panel">
    <h3>⚙️ Controls</h3>

    <div class="checkbox-group">
      <input
        type="checkbox"
        id="invert"
        :checked="store.metadata?.inverted ?? false"
        @change="handleInvert"
        :disabled="store.loading"
      />
      <label for="invert">Invert ECG</label>
    </div>

    <div class="download-link-container" style="margin-bottom: 15px;">
      <a :href="exportURL" class="download-link" download>
        📥 Download RRs and classifications
      </a>
    </div>

    <div class="form-group">
      <label>Select viewing length</label>
      <select
        v-model="windowLengthModel"
        :disabled="store.loading"
      >
        <option
          v-for="option in store.windowOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label>Select file</label>
      <select
        v-model="selectedFileModel"
        :disabled="store.loading"
      >
        <option
          v-for="file in store.files"
          :key="file.value"
          :value="file.value"
        >
          {{ file.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useECGStore } from '../stores/ecg'
import api from '../services/api'

const store = useECGStore()

const exportURL = computed(() => api.getExportURL())

// Computed with getter/setter for window length
const windowLengthModel = computed({
  get: () => store.windowLength,
  set: (value) => store.updateWindowLength(value)
})

// Computed with getter/setter for file selection
const selectedFileModel = computed({
  get: () => {
    if (!store.currentFile || store.files.length === 0) return null
    const matchingFile = store.files.find(f => f.label === store.currentFile)
    return matchingFile?.value ?? null
  },
  set: (value) => {
    if (value) {
      store.loadECG(value)
    }
  }
})

async function handleInvert() {
  await store.invertECG()
}
</script>
