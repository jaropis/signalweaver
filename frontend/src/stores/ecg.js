import { defineStore } from 'pinia'
import api from '../services/api'

export const useECGStore = defineStore('ecg', {
  state: () => ({
    // File list and selection
    files: [],
    currentFile: null,

    // ECG metadata
    metadata: null,

    // ECG trace data
    traceData: null,

    // Poincaré data
    poincareData: null,

    // UI state
    loading: false,
    loadingTrace: false,
    error: null,
    saveStatus: null,

    // Window configuration
    windowLength: 300,  // Default to 5 minutes (matches backend default for long recordings)
    position: 0,

    // Available window options (matching backend)
    windowOptions: [
      { label: '15 s', value: 15 },
      { label: '1 min', value: 60 },
      { label: '3 min', value: 180 },
      { label: '5 min', value: 300 },
      { label: '10 min', value: 600 },
      { label: '20 min', value: 1200 }
    ]
  }),

  actions: {
    async loadFiles() {
      this.loading = true
      this.error = null
      try {
        const result = await api.listFiles()
        if (result.success) {
          this.files = result.data
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async loadECG(filePath) {
      this.loading = true
      this.error = null
      try {
        const result = await api.loadECG(filePath)
        if (result.success) {
          this.currentFile = result.data.filename
          await this.refreshAll()
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async refreshAll() {
      // Fetch metadata first to get correct position and windowLength
      await this.fetchMetadata()
      // Then fetch trace and poincare in parallel (they depend on metadata values)
      await Promise.all([
        this.fetchTrace(),
        this.fetchPoincare()
      ])
    },

    async fetchMetadata() {
      try {
        const result = await api.getMetadata()
        if (result.success) {
          this.metadata = result.data
          this.position = result.data.position
          this.windowLength = result.data.window_length
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async fetchTrace() {
      this.loadingTrace = true
      try {
        const result = await api.getTrace(this.position, this.windowLength)
        if (result.success) {
          this.traceData = result.data
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingTrace = false
      }
    },

    async fetchPoincare() {
      try {
        const result = await api.getPoincare()
        if (result.success) {
          this.poincareData = result.data
        }
      } catch (error) {
        // Poincaré might not be available, don't show error
        console.warn('Poincaré data not available:', error)
      }
    },

    async invertECG() {
      this.loading = true
      try {
        const result = await api.invertECG()
        if (result.success) {
          await this.refreshAll()
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async navigate(direction) {
      try {
        const result = await api.navigate(direction, this.windowLength)
        if (result.success) {
          this.position = result.data.position
          await this.fetchTrace()
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async updateWindowLength(windowLength) {
      this.windowLength = windowLength
      try {
        const result = await api.updateWindow(windowLength)
        if (result.success) {
          await this.fetchTrace()
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async navigateToPoincare(pointNumber) {
      try {
        const result = await api.navigatePoincare(pointNumber)
        if (result.success) {
          this.position = result.data.position
          await this.fetchTrace()
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async navigateToPosition(positionInSeconds) {
      // Clamp position to valid range
      if (this.metadata) {
        const maxPosition = Math.max(0, this.metadata.duration - this.windowLength)
        positionInSeconds = Math.max(0, Math.min(positionInSeconds, maxPosition))
      }
      this.position = positionInSeconds
      try {
        await this.fetchTrace()
      } catch (error) {
        this.error = error.message
      }
    },

    async classifyPeak(timePosition, annotation) {
      try {
        const result = await api.classifyPeak(timePosition, annotation)
        if (result.success && result.data.changed) {
          await Promise.all([this.fetchTrace(), this.fetchPoincare()])
        } else if (!result.success) {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async insertPeak(timePosition) {
      try {
        const result = await api.insertPeak(timePosition)
        if (result.success && result.data.changed) {
          await Promise.all([this.fetchTrace(), this.fetchPoincare()])
        } else if (!result.success) {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async removePeak(timePosition) {
      try {
        const result = await api.removePeak(timePosition)
        if (result.success) {
          await Promise.all([this.fetchTrace(), this.fetchPoincare()])
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = error.message
      }
    },

    async save() {
      this.loading = true
      this.saveStatus = null
      try {
        const result = await api.save()
        if (result.success) {
          this.saveStatus = 'Saved successfully!'
        } else {
          this.saveStatus = 'Save failed: ' + result.error
        }
      } catch (error) {
        this.saveStatus = 'Save failed: ' + error.message
      } finally {
        this.loading = false
        // Clear status after 3 seconds
        setTimeout(() => {
          this.saveStatus = null
        }, 3000)
      }
    }
  }
})
