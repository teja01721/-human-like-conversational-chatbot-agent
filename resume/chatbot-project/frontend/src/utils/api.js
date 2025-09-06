import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const chatAPI = {
  sendMessage: (data) => api.post('/api/chat/message', data),
  getSessions: (userId) => api.get(`/api/chat/sessions/${userId}`),
  getChatHistory: (sessionId, limit = 50) => api.get(`/api/chat/history/${sessionId}?limit=${limit}`),
  deleteSession: (sessionId) => api.delete(`/api/chat/sessions/${sessionId}`),
  submitFeedback: (data) => api.post('/api/chat/feedback', data),
  getAnalytics: (userId) => api.get(`/api/chat/analytics/${userId}`),
}

export const userAPI = {
  createUser: (data) => api.post('/api/users/', data),
  getUser: (userId) => api.get(`/api/users/${userId}`),
  updateUser: (userId, data) => api.put(`/api/users/${userId}`, data),
  deleteUser: (userId) => api.delete(`/api/users/${userId}`),
  getUserMemories: (userId, memoryType = null, limit = 50) => {
    const params = new URLSearchParams({ limit })
    if (memoryType) params.append('memory_type', memoryType)
    return api.get(`/api/users/${userId}/memories?${params}`)
  },
  addUserMemory: (userId, data) => api.post(`/api/users/${userId}/memories`, data),
  deleteUserMemory: (userId, memoryId) => api.delete(`/api/users/${userId}/memories/${memoryId}`),
  getUserProfile: (userId) => api.get(`/api/users/${userId}/profile`),
}

export const healthAPI = {
  check: () => api.get('/health/'),
  detailed: () => api.get('/health/detailed'),
}

export default api
