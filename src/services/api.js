// In Produktion: verwende den tatsächlichen Backend-Pfad von DigitalOcean
// In Entwicklung: localhost:8000
const getApiBaseUrl = () => {
  // Wenn VITE_API_URL explizit gesetzt ist, verwende das
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // In Entwicklung (localhost) verwende localhost:8000
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000'
  }
  
  // In Produktion: verwende den tatsächlichen Backend-Pfad
  // DigitalOcean generiert automatisch: /roboadvisor-frontend-backend
  return '/roboadvisor-frontend-backend'
}

const API_BASE_URL = getApiBaseUrl()

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = localStorage.getItem('auth_token')
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('auth_token', token)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, config)
      
      // Response-Body als Text lesen (kann nur einmal gelesen werden)
      const text = await response.text()
      
      // Versuche, Text als JSON zu parsen
      let data
      try {
        data = text ? JSON.parse(text) : null
      } catch (jsonError) {
        // Wenn kein JSON, dann Text-Response verwenden
        throw new Error(`Server returned: ${response.status} ${response.statusText}. ${text.substring(0, 100)}`)
      }

      if (!response.ok) {
        throw new Error(data.detail || data.error || `HTTP ${response.status}: ${response.statusText}`)
      }

      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  // Auth Endpoints
  async register(name, email, password) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    })
  }

  async login(email, password) {
    const response = await this.request('/api/auth/login-json', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    
    if (response.access_token) {
      this.setToken(response.access_token)
    }
    
    return response
  }

  async getCurrentUser() {
    return this.request('/api/auth/me')
  }

  async logout() {
    this.setToken(null)
  }

  // Health Check
  async healthCheck() {
    return this.request('/api/health')
  }
}

export default new ApiService()



