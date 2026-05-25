import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const fetchBitableData = async (params) => {
  const response = await apiClient.post('/fetch/', params)
  if (response.data.success) {
    return response.data.data
  } else {
    throw new Error(response.data.error)
  }
}

export const checkHealth = async () => {
  const response = await apiClient.get('/health/')
  return response.data
}
