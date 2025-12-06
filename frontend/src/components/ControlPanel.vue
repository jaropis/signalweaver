<template>
  <div class="panel">
    <h3>⚙️ Controls</h3>

    <div class="checkbox-group">
      <input
        type="checkbox"
        id="invert"
        v-model="inverted"
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
        v-model="selectedWindow"
        @change="handleWindowChange"
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
        v-model="selectedFile"
        @change="handleFileChange"
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
import { ref, computed, watch } from 'vue'
import { useECGStore } from '../stores/ecg'
import api from '../services/api'

const store = useECGStore()
const inverted = ref(false)
const selectedWindow = ref(60)
const selectedFile = ref(null)

const exportURL = computed(() => api.getExportURL())

// Watch for metadata changes to update inverted state
watch(() => store.metadata, (metadata) => {
  if (metadata) {
    inverted.value = metadata.inverted
    selectedWindow.value = metadata.window_length
  }
})

// Watch for currentFile changes to sync dropdown
watch(() => store.currentFile, (currentFile) => {
  if (currentFile) {
    // Find the matching file value from the files list
    const matchingFile = store.files.find(f => f.label === currentFile || f.value === currentFile)
    if (matchingFile) {
      selectedFile.value = matchingFile.value
    }
  }
})

// Initialize selected file when files load
watch(() => store.files, (files) => {
  if (files.length > 0 && !selectedFile.value) {
    selectedFile.value = files[0].value
    store.loadECG(selectedFile.value)
  }
})

async function handleInvert() {
  await store.invertECG()
}

async function handleWindowChange() {
  await store.updateWindowLength(selectedWindow.value)
}

async function handleFileChange() {
  if (selectedFile.value) {
    await store.loadECG(selectedFile.value)
  }
}
</script>
