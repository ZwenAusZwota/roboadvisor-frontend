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

  // Konvertiert HTTP-Status-Codes in benutzerfreundliche Fehlermeldungen
  getErrorMessage(statusCode, backendMessage) {
    // Filtere technische Fehlermeldungen heraus
    const technicalKeywords = [
      'Internal server error',
      'Registration failed',
      'Traceback',
      'password cannot be longer than 72 bytes',
      'truncate manually',
      'cannot be longer',
      'bytes',
      'Exception',
      'Error:',
      'at ',
      'File "',
      'line '
    ]
    
    // Wenn Backend bereits eine benutzerfreundliche Nachricht sendet, verwende diese
    if (backendMessage && !technicalKeywords.some(keyword => backendMessage.includes(keyword))) {
      return backendMessage
    }
    
    // Ansonsten generische Nachrichten basierend auf Status-Code
    switch (statusCode) {
      case 400:
        return 'Ungültige Eingabedaten. Bitte überprüfen Sie Ihre Eingaben.'
      case 401:
        return 'E-Mail oder Passwort falsch'
      case 403:
        return 'Zugriff verweigert'
      case 404:
        return 'Ressource nicht gefunden'
      case 409:
        return 'Diese E-Mail-Adresse ist bereits registriert'
      case 500:
        return 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'
      case 503:
        return 'Service vorübergehend nicht verfügbar. Bitte versuchen Sie es später erneut.'
      default:
        return 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.'
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
        // Wenn kein JSON, dann generische Fehlermeldung
        const errorMessage = this.getErrorMessage(response.status, null)
        throw new Error(errorMessage)
      }

      if (!response.ok) {
        // Verwende benutzerfreundliche Fehlermeldung
        const errorMessage = this.getErrorMessage(response.status, data.detail || data.error)
        throw new Error(errorMessage)
      }

      return data
    } catch (error) {
      // Logge detaillierte Fehler nur in der Konsole, nicht für den Benutzer
      console.error('API Error:', error)
      // Wirf nur die benutzerfreundliche Nachricht
      if (error.message && !error.message.includes('API Error')) {
        throw error
      }
      // Fallback für unerwartete Fehler
      throw new Error('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.')
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



