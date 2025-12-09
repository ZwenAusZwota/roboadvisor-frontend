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

  // User Profile Endpoints
  async getUserProfile() {
    return this.request('/api/user/profile')
  }

  async updateUserProfile(profileData) {
    return this.request('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    })
  }

  // User Settings Endpoints
  async getUserSettings() {
    return this.request('/api/user/settings')
  }

  async updateUserSettings(settingsData) {
    return this.request('/api/user/settings', {
      method: 'PUT',
      body: JSON.stringify(settingsData),
    })
  }

  // Security Endpoints
  async changePassword(currentPassword, newPassword) {
    return this.request('/api/user/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    })
  }

  async setup2FA(enable, password) {
    return this.request('/api/user/2fa/setup', {
      method: 'POST',
      body: JSON.stringify({
        enable,
        password,
      }),
    })
  }

  // Privacy Endpoints
  async exportUserData() {
    const response = await fetch(`${this.baseURL}/api/user/data-export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Fehler beim Exportieren der Daten')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `user_data_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  async deleteAccount() {
    return this.request('/api/user', {
      method: 'DELETE',
    })
  }

  // Portfolio Endpoints
  async getPortfolio() {
    return this.request('/api/portfolio')
  }

  async getPortfolioHolding(id) {
    return this.request(`/api/portfolio/${id}`)
  }

  async createPortfolioHolding(holding) {
    return this.request('/api/portfolio', {
      method: 'POST',
      body: JSON.stringify(holding),
    })
  }

  async updatePortfolioHolding(id, holding) {
    return this.request(`/api/portfolio/${id}`, {
      method: 'PUT',
      body: JSON.stringify(holding),
    })
  }

  async deletePortfolioHolding(id) {
    return this.request(`/api/portfolio/${id}`, {
      method: 'DELETE',
    })
  }

  async uploadPortfolioCSV(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${this.baseURL}/api/portfolio/upload-csv`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    })

    const text = await response.text()
    let data
    try {
      data = text ? JSON.parse(text) : null
    } catch (jsonError) {
      const errorMessage = this.getErrorMessage(response.status, null)
      throw new Error(errorMessage)
    }

    if (!response.ok) {
      const errorMessage = this.getErrorMessage(response.status, data.detail || data.error)
      throw new Error(errorMessage)
    }

    return data
  }

  async downloadCSVTemplate() {
    const response = await fetch(`${this.baseURL}/api/portfolio/csv-template`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Fehler beim Herunterladen des Templates')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'portfolio_template.csv'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  // Portfolio Dashboard Endpoints
  async getPortfolioSummary() {
    return this.request('/api/portfolio/dashboard/summary')
  }

  async getPerformanceHistory(days = 30) {
    return this.request(`/api/portfolio/dashboard/performance?days=${days}`)
  }

  async getPortfolioAllocation() {
    return this.request('/api/portfolio/dashboard/allocation')
  }

  async getRiskMetrics() {
    return this.request('/api/portfolio/dashboard/risk')
  }

  // Portfolio Analysis Endpoints
  async analyzePortfolio(forceRefresh = false) {
    return this.request('/api/portfolio/analyze', {
      method: 'POST',
      body: JSON.stringify({ force_refresh: forceRefresh }),
    })
  }

  async clearAnalysisCache() {
    return this.request('/api/portfolio/analyze/cache', {
      method: 'DELETE',
    })
  }

  // Watchlist Endpoints
  async getWatchlist() {
    return this.request('/api/watchlist')
  }

  async getWatchlistItem(id) {
    return this.request(`/api/watchlist/${id}`)
  }

  async createWatchlistItem(item) {
    return this.request('/api/watchlist', {
      method: 'POST',
      body: JSON.stringify(item),
    })
  }

  async updateWatchlistItem(id, item) {
    return this.request(`/api/watchlist/${id}`, {
      method: 'PUT',
      body: JSON.stringify(item),
    })
  }

  async deleteWatchlistItem(id) {
    return this.request(`/api/watchlist/${id}`, {
      method: 'DELETE',
    })
  }

  async analyzeWatchlist(itemId = null, forceRefresh = false) {
    return this.request('/api/watchlist/analyze', {
      method: 'POST',
      body: JSON.stringify({ 
        item_id: itemId,
        force_refresh: forceRefresh 
      }),
    })
  }

  // Analysis History Endpoints
  async getPortfolioHoldingHistory(holdingId) {
    return this.request(`/api/analysis-history/portfolio/${holdingId}`)
  }

  async getWatchlistItemHistory(itemId) {
    return this.request(`/api/analysis-history/watchlist/${itemId}`)
  }

  async getAssetHistory(isin = null, ticker = null) {
    const params = new URLSearchParams()
    if (isin) params.append('isin', isin)
    if (ticker) params.append('ticker', ticker)
    return this.request(`/api/analysis-history/asset?${params.toString()}`)
  }

  async getAnalysisSummary() {
    return this.request('/api/analysis-history/summary')
  }
}

export default new ApiService()



