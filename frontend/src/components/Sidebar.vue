<template>
  <div class="sidebar" :class="{ collapsed: !isOpen }">
    <!-- Sidebar content -->
    <div class="sidebar-content" v-show="isOpen">
      <!-- Navigation Section -->
      <div class="sidebar-section">
        <div class="section-title">Navigation</div>
        <div class="nav-buttons">
          <button
            class="nav-btn"
            @click="moveLeft"
            :disabled="store.loading"
          >
            <v-icon size="16">mdi-chevron-left</v-icon>
            <span>Left</span>
          </button>
          <button
            class="nav-btn"
            @click="moveRight"
            :disabled="store.loading"
          >
            <span>Right</span>
            <v-icon size="16">mdi-chevron-right</v-icon>
          </button>
        </div>
      </div>

      <!-- Controls Section -->
      <div class="sidebar-section">
        <div class="section-title">Controls</div>

        <div class="form-group">
          <label class="form-label">File</label>
          <select
            class="form-select"
            v-model="selectedFile"
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

        <div class="form-group">
          <label class="form-label">Window</label>
          <select
            class="form-select"
            v-model="selectedWindow"
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

        <label class="form-checkbox">
          <input
            type="checkbox"
            v-model="inverted"
            :disabled="store.loading"
          />
          <span>Invert ECG</span>
        </label>

        <a :href="exportURL" class="download-link" download>
          <v-icon size="14">mdi-download</v-icon>
          <span>Export RR Intervals</span>
        </a>
      </div>
    </div>

    <!-- Toggle button - positioned to align with track center -->
    <button
      class="sidebar-toggle"
      @click="isOpen = !isOpen"
      :title="isOpen ? 'Collapse sidebar' : 'Expand sidebar'"
    >
      <v-icon size="18">{{ isOpen ? 'mdi-chevron-left' : 'mdi-chevron-right' }}</v-icon>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useECGStore } from '../stores/ecg'
import api from '../services/api'

const store = useECGStore()

const isOpen = ref(true)

const exportURL = computed(() => api.getExportURL())

// Computed with getter/setter for window length - binds directly to store
const selectedWindow = computed({
  get: () => store.windowLength,
  set: (value) => store.updateWindowLength(value)
})

// Computed with getter/setter for file selection - derives from store.currentFile
const selectedFile = computed({
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

// Computed for inverted checkbox - binds directly to store metadata
const inverted = computed({
  get: () => store.metadata?.inverted ?? false,
  set: () => store.invertECG()
})

// Navigation functions
async function moveLeft() {
  await store.navigate('left')
}

async function moveRight() {
  await store.navigate('right')
}

// Initialize: load first file when files become available
watch(() => store.files, (files) => {
  if (files.length > 0 && !store.currentFile) {
    store.loadECG(files[0].value)
  }
}, { immediate: true })
</script>

<style scoped>
.sidebar {
  position: relative;
  display: flex;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: width 0.2s ease;
  width: 200px;
  flex-shrink: 0;
  align-self: stretch;
}

.sidebar.collapsed {
  width: 28px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
}

.sidebar-toggle {
  position: absolute;
  right: 0;
  top: 0;
  width: 28px;
  height: 28px;
  background: var(--color-surface);
  border: none;
  border-left: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  border-radius: 0 var(--radius-md) 0 var(--radius-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  padding: 0;
  transition: all var(--transition);
}

.sidebar-toggle:hover {
  background: #f5f5f5;
  color: var(--color-text-primary);
}

.sidebar-content {
  padding: 16px;
  width: 100%;
  overflow: hidden;
}

.sidebar-section {
  margin-bottom: 20px;
}

.sidebar-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-border);
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all var(--transition);
}

.nav-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #bdbdbd;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-group {
  margin-bottom: 12px;
}

.form-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-select {
  width: 100%;
  padding: 6px 8px;
  font-size: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color var(--transition);
}

.form-select:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--color-text-primary);
  cursor: pointer;
  margin-bottom: 12px;
}

.form-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.download-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 0.75rem;
  color: var(--color-accent);
  text-decoration: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all var(--transition);
  width: 100%;
}

.download-link:hover {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}
</style>
