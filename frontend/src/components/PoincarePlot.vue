<template>
  <div class="panel">
    <h3>📊 Poincaré Plot</h3>
    <div v-if="store.poincareData" ref="plotDiv" class="plot-container"></div>
    <div v-else class="loading">Loading Poincaré data...</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { useECGStore } from '../stores/ecg'
import Plotly from 'plotly.js-dist-min'

const store = useECGStore()
const plotDiv = ref(null)

async function handlePlotClick(data) {
  if (!data || !data.points || data.points.length === 0) return

  const pointNumber = data.points[0].pointNumber
  await store.navigateToPoincare(pointNumber)
}

function renderPlot() {
  if (!plotDiv.value || !store.poincareData) return

  const { xi, xii, range } = store.poincareData
  const plotSize = 700

  const trace = {
    x: xi,
    y: xii,
    mode: 'markers',
    type: 'scattergl',
    marker: {
      size: 12,
      color: 'black',
      opacity: 0.2
    },
    name: 'Poincaré plot',
    hovertemplate: '<b>RR<sub>i</sub></b>: %{x:.3f} s<br>' +
                   '<b>RR<sub>i+1</sub></b>: %{y:.3f} s<br>' +
                   '<extra></extra>'
  }

  const layout = {
    title: 'Poincaré plot',
    hovermode: 'closest',
    width: plotSize,
    height: plotSize,
    xaxis: {
      title: 'RR<sub>i</sub>',
      showline: true,
      linewidth: 1,
      linecolor: 'black',
      range: [range.start, range.end],
      constraintoward: 'left'
    },
    yaxis: {
      title: 'RR<sub>i+1</sub>',
      showline: true,
      linewidth: 1,
      linecolor: 'black',
      range: [range.start, range.end],
      constraintoward: 'bottom'
    }
  }

  Plotly.newPlot(plotDiv.value, [trace], layout, {
    responsive: true,
    displayModeBar: false
  })

  // Add click handler
  plotDiv.value.on('plotly_click', handlePlotClick)
}

watch(() => store.poincareData, async () => {
  await nextTick()
  renderPlot()
}, { deep: true })

onMounted(() => {
  if (store.poincareData) {
    renderPlot()
  }
})
</script>

<style scoped>
.plot-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
