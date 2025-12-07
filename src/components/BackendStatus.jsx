import React, { useState, useEffect } from 'react'
import api from '../services/api'
import './BackendStatus.css'

const BackendStatus = () => {
  const [status, setStatus] = useState(null) // null = loading, true = healthy, false = unhealthy
  const [statusInfo, setStatusInfo] = useState(null)
  const [isHovered, setIsHovered] = useState(false)

  const checkHealth = async () => {
    try {
      const response = await api.healthCheck()
      setStatus(response.status === 'healthy')
      setStatusInfo(response)
    } catch (error) {
      setStatus(false)
      setStatusInfo({
        status: 'unhealthy',
        error: error.message || 'Backend nicht erreichbar',
        timestamp: new Date().toISOString()
      })
    }
  }

  useEffect(() => {
    // Sofort beim Mount prüfen
    checkHealth()

    // Dann alle 30 Sekunden prüfen
    const interval = setInterval(checkHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  const getStatusText = () => {
    if (status === null) return 'Prüfe Backend-Status...'
    if (status) {
      const dbStatus = statusInfo?.database || 'unbekannt'
      const timestamp = statusInfo?.timestamp 
        ? new Date(statusInfo.timestamp).toLocaleString('de-DE')
        : 'unbekannt'
      return `Backend ist erreichbar und gesund\n\nDatenbank: ${dbStatus}\nZeitstempel: ${timestamp}`
    }
    const errorMsg = statusInfo?.error || 'Unbekannter Fehler'
    const timestamp = statusInfo?.timestamp 
      ? new Date(statusInfo.timestamp).toLocaleString('de-DE')
      : new Date().toLocaleString('de-DE')
    return `Backend ist nicht erreichbar oder ungesund\n\nFehler: ${errorMsg}\nZeitstempel: ${timestamp}`
  }

  return (
    <div 
      className="backend-status-container"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={`backend-status-dot ${status === null ? 'loading' : status ? 'healthy' : 'unhealthy'}`}>
        {status === null && <span className="status-spinner"></span>}
      </div>
      {isHovered && (
        <div className="backend-status-tooltip">
          <pre>{getStatusText()}</pre>
        </div>
      )}
    </div>
  )
}

export default BackendStatus

