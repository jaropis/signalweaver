<template>
  <div class="ecg-panel panel">
    <div class="ecg-header">
      <span class="ecg-title">ECG Signal</span>
      <span v-if="store.metadata" class="window-position">{{ windowPositionText }}</span>
    </div>
    <div class="plot-wrapper">
      <!-- Left navigation arrow -->
      <button
        class="nav-arrow nav-arrow-left"
        @click="navigateLeft"
        :disabled="store.loading"
        title="Move Left (← arrow key)"
      >
        <v-icon size="48">mdi-chevron-left</v-icon>
      </button>

      <div v-if="store.traceData" ref="plotDiv" class="plot-container" :class="{ 'loading-dim': store.loadingTrace }"></div>
      <div v-else class="loading-state">Loading ECG data...</div>

      <!-- Loading overlay -->
      <div v-if="store.loadingTrace && store.traceData" class="loading-overlay">
        <v-progress-circular indeterminate size="48" width="4" color="primary"></v-progress-circular>
      </div>

      <!-- Right navigation arrow -->
      <button
        class="nav-arrow nav-arrow-right"
        @click="navigateRight"
        :disabled="store.loading"
        title="Move Right (→ arrow key)"
      >
        <v-icon size="48">mdi-chevron-right</v-icon>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useECGStore } from '../stores/ecg'
import Plotly from 'plotly.js-dist-min'

const store = useECGStore()
const plotDiv = ref(null)
let resizeObserver = null

// Format time duration for display (e.g., "5 min" or "2 hours 30 min")
function formatDuration(seconds) {
  if (seconds < 60) {
    return `${Math.round(seconds)} s`
  } else if (seconds < 3600) {
    const minutes = Math.round(seconds / 60)
    return `${minutes} min`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.round((seconds % 3600) / 60)
    if (minutes === 0) {
      return `${hours} hour${hours !== 1 ? 's' : ''}`
    }
    return `${hours} hour${hours !== 1 ? 's' : ''} ${minutes} min`
  }
}

// Format position as minutes or hours:minutes
function formatPosition(seconds) {
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)} min`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.round((seconds % 3600) / 60)
    return `${hours}:${minutes.toString().padStart(2, '0')}`
  }
}

// Computed property for window position text
const windowPositionText = computed(() => {
  if (!store.metadata) return ''

  const position = store.position
  const windowLength = store.windowLength
  const totalDuration = store.metadata.duration

  const startPos = formatPosition(position)
  const endPos = formatPosition(position + windowLength)
  const total = formatDuration(totalDuration)

  return `window position: ${startPos} - ${endPos} of ${total}`
})

// Navigation functions
async function navigateLeft() {
  await store.navigate('left')
}

async function navigateRight() {
  await store.navigate('right')
}

// Constants from original implementation
const PHYSICAL_LINE_HEIGHT = 100
const OFFSET_OVER_TRACE = 0.05

function formatTimeForTooltip(timeInSeconds) {
  if (timeInSeconds < 60) {
    return `${timeInSeconds.toFixed(3)} s`
  } else if (timeInSeconds < 3600) {
    const minutes = Math.floor(timeInSeconds / 60)
    const seconds = timeInSeconds % 60
    return `${minutes}:${seconds.toFixed(3).padStart(6, '0')}`
  } else {
    const hours = Math.floor(timeInSeconds / 3600)
    const minutes = Math.floor((timeInSeconds % 3600) / 60)
    const seconds = timeInSeconds % 60
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toFixed(3).padStart(6, '0')}`
  }
}

function foldIndices(vector, down, up, startingSample, samplingPeriod) {
  return vector.map((v, i) =>
    v >= down * samplingPeriod + startingSample &&
    v < up * samplingPeriod + startingSample
  )
}

function createFoldedFigure(traceData) {
  const { time, voltage, peaks, window_config } = traceData
  const { number_of_lines, single_line_height } = window_config
  const samplingPeriod = time.length > 1 ? time[1] - time[0] : 0.005

  const localWinLength = Math.floor(time.length / number_of_lines)
  const startingSample = time[0]
  const lineShift = single_line_height * 3 / 2

  const traces = []

  for (let idx = 0; idx < number_of_lines; idx++) {
    const lineIndicesDown = idx * localWinLength
    const localIndicesUp = Math.min((idx + 1) * localWinLength, time.length)

    if (lineIndicesDown >= time.length) break

    const currentXShift = time[lineIndicesDown] - startingSample
    const lineTime = time.slice(lineIndicesDown, localIndicesUp)
    const lineVoltage = voltage.slice(lineIndicesDown, localIndicesUp)

    if (lineVoltage.length === 0) continue

    const yBaseline = Math.min(...lineVoltage)
    const yMax = Math.max(...lineVoltage.map(v => v - yBaseline))

    // ECG trace - use hovertemplate instead of hoverinfo:'skip' to preserve click detection
    traces.push({
      x: lineTime.map(t => t - currentXShift),
      y: lineVoltage.map(v => (v - yBaseline) / yMax - idx * lineShift),
      mode: 'lines',
      line: { color: 'black', width: 2 },
      name: 'ECG trace',
      hovertemplate: '<extra></extra>',
      showlegend: false
    })

    // Helper function to add peak markers
    // IMPORTANT: Always add trace even if empty to maintain consistent curve numbering
    const addPeakMarkers = (peakData, color, label) => {
      const indices = foldIndices(peakData.time, lineIndicesDown, localIndicesUp, startingSample, samplingPeriod)
      const filteredTime = peakData.time.filter((_, i) => indices[i])
      const filteredVoltage = peakData.voltage.filter((_, i) => indices[i])

      traces.push({
        x: filteredTime.map(t => t - currentXShift),
        y: filteredVoltage.map(v => (v - yBaseline) / yMax + OFFSET_OVER_TRACE - idx * lineShift),
        mode: 'markers',
        marker: { size: 12, color },
        name: label,
        customdata: filteredTime.map(t => formatTimeForTooltip(t - currentXShift)),
        hovertemplate: `<b>${label}</b><br>Time: %{customdata}<br><extra></extra>`,
        showlegend: false
      })
    }

    // Add all peak types - must always add all 5 traces per line for correct curve numbering
    addPeakMarkers(peaks.normal, 'green', 'Normal beat')
    addPeakMarkers(peaks.ventricular, 'blue', 'Ventricular beat')
    addPeakMarkers(peaks.supraventricular, 'magenta', 'Supraventricular beat')
    addPeakMarkers(peaks.artifacts, 'red', 'Artifact')
  }

  const layout = {
    hovermode: 'closest',
    clickmode: 'event',
    height: number_of_lines * single_line_height * PHYSICAL_LINE_HEIGHT,
    showlegend: false,
    margin: { l: 10, r: 10, b: 10, t: 10, pad: 4 },
    xaxis: {
      showgrid: false,
      showticklabels: false,
      zeroline: false,
      showline: false
    },
    yaxis: {
      showgrid: false,
      showticklabels: false,
      zeroline: false,
      showline: false
    }
  }

  return { traces, layout }
}

function unfoldClickData(clickData, windowConfig) {
  if (!clickData || !clickData.points || clickData.points.length === 0) return null

  const point = clickData.points[0]
  const curveNumber = point.curveNumber
  const lineNumber = Math.floor(curveNumber / 5) // 5 traces per line
  const relativeCurve = curveNumber % 5
  const windowLength = store.windowLength
  const numberOfLines = windowConfig.number_of_lines
  // xUnfolded reconstructs the absolute time position:
  // - point.x is the displayed x (absolute_time - currentXShift for that line)
  // - Adding back lineNumber * lineLength restores the absolute time
  const xUnfolded = point.x + lineNumber * Math.ceil(windowLength / numberOfLines)

  return {
    curveNumber: relativeCurve,
    x: xUnfolded,
    absoluteX: xUnfolded  // Already absolute time, don't add store.position
  }
}

async function handlePlotClick(data) {
  if (!store.traceData) return

  const clickData = unfoldClickData(data, store.traceData.window_config)
  if (!clickData) return

  const { curveNumber, absoluteX } = clickData

  // Click behavior cycles through annotation types:
  // curveNumber 0 = ECG trace -> insert new peak (default: normal)
  // curveNumber 1 = normal (green) -> advance to ventricular (blue, annotation 1)
  // curveNumber 2 = ventricular (blue) -> advance to supraventricular (magenta, annotation 2)
  // curveNumber 3 = supraventricular (magenta) -> advance to artifact (red, annotation 3)
  // curveNumber 4 = artifact (red) -> remove peak

  if (curveNumber === 0) {
    // Insert new peak at clicked position
    await store.insertPeak(absoluteX)
  } else if (curveNumber === 1) {
    // Normal -> Ventricular
    await store.classifyPeak(absoluteX, 1)
  } else if (curveNumber === 2) {
    // Ventricular -> Supraventricular
    await store.classifyPeak(absoluteX, 2)
  } else if (curveNumber === 3) {
    // Supraventricular -> Artifact
    await store.classifyPeak(absoluteX, 3)
  } else if (curveNumber === 4) {
    // Artifact -> Remove
    await store.removePeak(absoluteX)
  }
}

function renderPlot() {
  if (!plotDiv.value || !store.traceData) return

  // Clean up previous observer
  if (resizeObserver) {
    resizeObserver.disconnect()
  }

  const { traces, layout } = createFoldedFigure(store.traceData)

  Plotly.newPlot(plotDiv.value, traces, layout, {
    responsive: false,
    displayModeBar: false
  })

  // Handle resize manually - only update width, preserve calculated height
  resizeObserver = new ResizeObserver(() => {
    if (plotDiv.value) {
      Plotly.relayout(plotDiv.value, {
        width: plotDiv.value.clientWidth
      })
    }
  })
  resizeObserver.observe(plotDiv.value)

  // Add click handler
  plotDiv.value.on('plotly_click', handlePlotClick)
}

watch(() => store.traceData, async () => {
  await nextTick()
  renderPlot()
}, { deep: true })

onMounted(() => {
  if (store.traceData) {
    renderPlot()
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.ecg-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.ecg-header {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ecg-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.window-position {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.plot-wrapper {
  position: relative;
  flex: 1;
  padding: 8px;
}

.plot-container {
  width: 100%;
  transition: opacity 0.2s ease;
}

.plot-container.loading-dim {
  opacity: 0.4;
}

.plot-container :deep(.js-plotly-plot),
.plot-container :deep(.plot-container),
.plot-container :deep(.svg-container) {
  width: 100% !important;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background: rgba(158, 158, 158, 0.15);
  color: rgba(97, 97, 97, 0.5);
  border: none;
  width: 48px;
  height: 96px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.nav-arrow:hover:not(:disabled) {
  background: rgba(158, 158, 158, 0.25);
  color: rgba(97, 97, 97, 0.8);
}

.nav-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-arrow-left {
  left: 16px;
  border-radius: var(--radius-sm);
}

.nav-arrow-right {
  right: 16px;
  border-radius: var(--radius-sm);
}

.loading-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
  pointer-events: none;
}
</style>
