<template>
  <v-app>
    <Header />

    <div v-if="store.error" class="error-banner">
      <span><strong>Error:</strong> {{ store.error }}</span>
      <button @click="store.error = null">
        <v-icon size="small">mdi-close</v-icon>
      </button>
    </div>

    <div v-if="store.loading && !store.metadata" class="loading-state">
      <v-progress-circular indeterminate size="24" width="2" class="mr-3"></v-progress-circular>
      Loading...
    </div>

    <template v-else>
      <!-- Poincare Toggle - above everything -->
      <div class="poincare-toggle-row">
        <PoincareToggle
          :isOpen="showPoincareWindow"
          @toggle="showPoincareWindow = !showPoincareWindow"
        />
      </div>

      <!-- Main content area with sidebar -->
      <div class="app-main">
        <!-- Sidebar -->
        <Sidebar />

        <!-- ECG area -->
        <div class="ecg-area">
          <!-- ECG Plot -->
          <ECGPlot />

          <!-- Status/Save -->
          <StatusPanel />
        </div>
      </div>

      <!-- Floating Poincare Plot Window -->
      <FloatingWindow
        title="Poincare Plot"
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
  </v-app>
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

<style scoped>
.poincare-toggle-row {
  padding: 8px 16px 0 16px;
}
</style>
