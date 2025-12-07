<template>
  <div id="app">
    <Header />

    <div v-if="store.error" class="error">
      <strong>Error:</strong> {{ store.error }}
      <button @click="store.error = null" style="float: right; padding: 2px 8px;">✕</button>
    </div>

    <div v-if="store.loading && !store.metadata" class="loading">
      Loading...
    </div>

    <template v-else>
      <!-- Main content area with sidebar -->
      <div class="main-content">
        <!-- Sidebar -->
        <Sidebar />

        <!-- ECG area -->
        <div class="ecg-area">
          <!-- Poincare Toggle - directly above ECG panel -->
          <div class="poincare-toggle-row">
            <PoincareToggle
              :isOpen="showPoincareWindow"
              @toggle="showPoincareWindow = !showPoincareWindow"
            />
          </div>

          <!-- ECG Plot -->
          <ECGPlot />

          <!-- Status/Save -->
          <StatusPanel />
        </div>
      </div>

      <!-- Floating Poincare Plot Window -->
      <FloatingWindow
        title="Poincaré Plot"
        :visible="showPoincareWindow"
        :initialWidth="750"
        :initialHeight="800"
        :minWidth="400"
        :minHeight="450"
        @close="showPoincareWindow = false"
      >
        <PoincarePlot />
      </FloatingWindow>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useECGStore } from './stores/ecg'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'
import PoincareToggle from './components/PoincareToggle.vue'
import FloatingWindow from './components/FloatingWindow.vue'
import PoincarePlot from './components/PoincarePlot.vue'
import ECGPlot from './components/ECGPlot.vue'
import StatusPanel from './components/StatusPanel.vue'

const store = useECGStore()
const showPoincareWindow = ref(false)

function handleKeydown(event) {
  // Ignore if user is typing in an input field
  if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT' || event.target.tagName === 'TEXTAREA') {
    return
  }

  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    store.navigate('left')
  } else if (event.key === 'ArrowRight') {
    event.preventDefault()
    store.navigate('right')
  }
}

onMounted(async () => {
  await store.loadFiles()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
