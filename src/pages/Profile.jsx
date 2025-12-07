import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import './Profile.css'

const Profile = () => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        navigate('/')
        return
      }

      try {
        const userData = await api.getCurrentUser()
        setUser(userData)
      } catch (err) {
        setError('Fehler beim Laden der Benutzerdaten')
        api.logout()
        navigate('/')
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [navigate])

  if (loading) {
    return (
      <div className="profile-container">
        <div className="profile-content">
          <p>Lade Profil...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="profile-container">
        <div className="profile-content">
          <div className="error-message">{error}</div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="profile-container">
      <div className="profile-content">
        <h1>Mein Profil</h1>
        
        <div className="profile-section">
          <h2>Persönliche Informationen</h2>
          <div className="profile-info">
            <div className="info-row">
              <span className="info-label">Name:</span>
              <span className="info-value">{user.name || 'Nicht angegeben'}</span>
            </div>
            <div className="info-row">
              <span className="info-label">E-Mail:</span>
              <span className="info-value">{user.email}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Benutzer-ID:</span>
              <span className="info-value">#{user.id}</span>
            </div>
          </div>
        </div>

        <div className="profile-actions">
          <button 
            className="btn-secondary"
            onClick={() => navigate('/')}
          >
            Zurück zur Startseite
          </button>
        </div>
      </div>
    </div>
  )
}

export default Profile

