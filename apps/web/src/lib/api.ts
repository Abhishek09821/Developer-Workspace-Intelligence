/**
 * Axios instance wired to the Canary API.
 * All requests go through here so the auth token is attached automatically.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
})

// Attach the JWT bearer token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('canary_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401 redirect to login (except when already on auth routes)
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      if (path !== '/login' && path !== '/register') {
        localStorage.removeItem('canary_access_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)
