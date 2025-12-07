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
      <!-- Controls and Poincare Toggle Row -->
      <div class="row">
        <div class="col-4">
          <ControlPanel />
        </div>
        <div class="col-8 poincare-toggle-container">
          <PoincareToggle
            :isOpen="showPoincareWindow"
            @toggle="showPoincareWindow = !showPoincareWindow"
          />
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

      <!-- Navigation -->
      <NavigationPanel />

      <!-- ECG Plot -->
      <ECGPlot />

      <!-- Status/Save -->
      <StatusPanel />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useECGStore } from './stores/ecg'
import Header from './components/Header.vue'
import ControlPanel from './components/ControlPanel.vue'
import PoincareToggle from './components/PoincareToggle.vue'
import FloatingWindow from './components/FloatingWindow.vue'
import PoincarePlot from './components/PoincarePlot.vue'
import NavigationPanel from './components/NavigationPanel.vue'
import ECGPlot from './components/ECGPlot.vue'
import StatusPanel from './components/StatusPanel.vue'

const store = useECGStore()
const showPoincareWindow = ref(false)

onMounted(async () => {
  await store.loadFiles()
})
</script>
