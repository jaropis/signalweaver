<template>
  <div class="poincare-wrapper" ref="wrapperDiv">
    <div v-if="store.poincareData" ref="plotDiv" class="plot-container"></div>
    <div v-else class="loading">Loading Poincaré data...</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useECGStore } from '../stores/ecg'
import Plotly from 'plotly.js-dist-min'

const store = useECGStore()
const plotDiv = ref(null)
const wrapperDiv = ref(null)
let resizeObserver = null

async function handlePlotClick(data) {
  if (!data || !data.points || data.points.length === 0) return

  const pointNumber = data.points[0].pointNumber
  await store.navigateToPoincare(pointNumber)
}

function renderPlot() {
  if (!plotDiv.value || !store.poincareData || !wrapperDiv.value) return

  const { xi, xii, range } = store.poincareData

  // Get container dimensions for responsive sizing
  const containerWidth = wrapperDiv.value.clientWidth
  const containerHeight = wrapperDiv.value.clientHeight
  // Use the smaller dimension to keep the plot square, with some padding
  const plotSize = Math.min(containerWidth - 20, containerHeight - 20, 700)

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

// Handle container resize
function handleResize() {
  if (store.poincareData) {
    renderPlot()
  }
}

watch(() => store.poincareData, async () => {
  await nextTick()
  renderPlot()
}, { deep: true })

onMounted(() => {
  if (store.poincareData) {
    renderPlot()
  }

  // Set up resize observer to re-render on container size change
  if (wrapperDiv.value) {
    resizeObserver = new ResizeObserver(() => {
      handleResize()
    })
    resizeObserver.observe(wrapperDiv.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.poincare-wrapper {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.plot-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #667eea;
}
</style>
