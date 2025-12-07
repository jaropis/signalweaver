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
import { ref, onMounted } from 'vue'
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

onMounted(async () => {
  await store.loadFiles()
})
</script>
