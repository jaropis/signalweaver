<template>
  <div class="sidebar-container" :class="{ collapsed: !isOpen }">
    <!-- Toggle button -->
    <button
      class="sidebar-toggle"
      @click="isOpen = !isOpen"
      :title="isOpen ? 'Collapse sidebar' : 'Expand sidebar'"
    >
      <span class="toggle-arrow">{{ isOpen ? '‹' : '›' }}</span>
    </button>

    <!-- Sidebar content -->
    <div class="sidebar-content" v-show="isOpen">
      <!-- Navigation Section -->
      <div class="sidebar-section">
        <h4>Navigation</h4>
        <div class="nav-buttons">
          <button
            class="nav-btn"
            @click="moveLeft"
            :disabled="store.loading"
            title="Move Left"
          >
            <span class="btn-icon">←</span>
            <span class="btn-text">Left</span>
          </button>
          <button
            class="nav-btn"
            @click="moveRight"
            :disabled="store.loading"
            title="Move Right"
          >
            <span class="btn-icon">→</span>
            <span class="btn-text">Right</span>
          </button>
        </div>
      </div>

      <!-- Controls Section -->
      <div class="sidebar-section">
        <h4>Controls</h4>

        <div class="control-item">
          <label>File</label>
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

        <div class="control-item">
          <label>Window</label>
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

        <div class="control-item checkbox">
          <input
            type="checkbox"
            id="sidebar-invert"
            v-model="inverted"
            @change="handleInvert"
            :disabled="store.loading"
          />
          <label for="sidebar-invert">Invert ECG</label>
        </div>

        <div class="control-item">
          <a :href="exportURL" class="download-btn" download>
            <span class="btn-icon">↓</span>
            <span class="btn-text">Download RRs</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useECGStore } from '../stores/ecg'
import api from '../services/api'

const store = useECGStore()

const isOpen = ref(true)
const inverted = ref(false)
const selectedWindow = ref(60)
const selectedFile = ref(null)

const exportURL = computed(() => api.getExportURL())

// Navigation functions
async function moveLeft() {
  await store.navigate('left')
}

async function moveRight() {
  await store.navigate('right')
}

// Control functions
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
</script>

<style scoped>
.sidebar-container {
  position: relative;
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
  width: 180px;
  flex-shrink: 0;
}

.sidebar-container.collapsed {
  width: 32px;
}

.sidebar-toggle {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 0 6px 6px 0;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  padding: 0;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.sidebar-toggle:hover {
  background: linear-gradient(135deg, #5568d3 0%, #653a91 100%);
}

.toggle-arrow {
  line-height: 1;
}

.sidebar-content {
  padding: 12px;
  width: 100%;
  overflow: hidden;
}

.sidebar-section {
  margin-bottom: 16px;
}

.sidebar-section:last-child {
  margin-bottom: 0;
}

.sidebar-section h4 {
  color: #667eea;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 10px;
  padding-bottom: 4px;
  border-bottom: 1px solid #eee;
}

.nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5568d3 0%, #653a91 100%);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 14px;
}

.btn-text {
  font-size: 11px;
}

.control-item {
  margin-bottom: 10px;
}

.control-item:last-child {
  margin-bottom: 0;
}

.control-item label {
  display: block;
  font-size: 11px;
  color: #555;
  margin-bottom: 4px;
  font-weight: 500;
}

.control-item select {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 11px;
  background: white;
}

.control-item select:focus {
  outline: none;
  border-color: #667eea;
}

.control-item.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-item.checkbox label {
  display: inline;
  margin-bottom: 0;
  font-size: 11px;
}

.control-item.checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 10px;
  background: #f8f9fa;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 4px;
  text-decoration: none;
  font-size: 11px;
  font-weight: 500;
  transition: all 0.2s;
}

.download-btn:hover {
  background: #667eea;
  color: white;
}

.download-btn .btn-icon {
  font-size: 12px;
}
</style>
