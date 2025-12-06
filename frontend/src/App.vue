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
      <!-- Controls and Poincare Plot Row -->
      <div class="row">
        <div class="col-4">
          <ControlPanel />
        </div>
        <div class="col-8">
          <PoincarePlot />
        </div>
      </div>

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
import { onMounted } from 'vue'
import { useECGStore } from './stores/ecg'
import Header from './components/Header.vue'
import ControlPanel from './components/ControlPanel.vue'
import PoincarePlot from './components/PoincarePlot.vue'
import NavigationPanel from './components/NavigationPanel.vue'
import ECGPlot from './components/ECGPlot.vue'
import StatusPanel from './components/StatusPanel.vue'

const store = useECGStore()

onMounted(async () => {
  await store.loadFiles()
})
</script>
