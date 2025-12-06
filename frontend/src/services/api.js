import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // File operations
  async listFiles() {
    const response = await api.get('/files')
    return response.data
  },

  async loadECG(filePath) {
    const response = await api.post('/ecg/load', { file_path: filePath })
    return response.data
  },

  async getMetadata() {
    const response = await api.get('/ecg/metadata')
    return response.data
  },

  // ECG data
  async getTrace(position = null, windowLength = null) {
    const params = {}
    if (position !== null) params.position = position
    if (windowLength !== null) params.window_length = windowLength

    const response = await api.get('/ecg/trace', { params })
    return response.data
  },

  async getPoincare() {
    const response = await api.get('/ecg/poincare')
    return response.data
  },

  // Manipulation
  async invertECG() {
    const response = await api.post('/ecg/invert')
    return response.data
  },

  async navigate(direction, windowLength = null) {
    const response = await api.post('/ecg/navigate', {
      direction,
      window_length: windowLength
    })
    return response.data
  },

  async updateWindow(windowLength) {
    const response = await api.post('/ecg/window', { window_length: windowLength })
    return response.data
  },

  async navigatePoincare(pointNumber) {
    const response = await api.post('/ecg/navigate/poincare', { point_number: pointNumber })
    return response.data
  },

  // Annotations
  async classifyPeak(timePosition, annotation) {
    const response = await api.post('/ecg/peak/classify', {
      time_position: timePosition,
      annotation
    })
    return response.data
  },

  async insertPeak(timePosition) {
    const response = await api.post('/ecg/peak/insert', { time_position: timePosition })
    return response.data
  },

  async removePeak(timePosition) {
    const response = await api.post('/ecg/peak/remove', { time_position: timePosition })
    return response.data
  },

  async save() {
    const response = await api.post('/ecg/save')
    return response.data
  },

  // Export
  getExportURL() {
    return '/api/ecg/export/rr'
  }
}
