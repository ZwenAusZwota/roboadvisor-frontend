import React, { useState } from 'react'
import api from '../services/api'
import './LoginModal.css'

const LoginModal = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  })

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        // Login
        await api.login(formData.email, formData.password)
        onClose()
        // Optional: Reload oder State-Update für eingeloggten User
        window.location.reload()
      } else {
        // Registrierung
        if (formData.password !== formData.confirmPassword) {
          setError('Passwörter stimmen nicht überein')
          setLoading(false)
          return
        }
        if (formData.password.length < 6) {
          setError('Passwort muss mindestens 6 Zeichen lang sein')
          setLoading(false)
          return
        }
        // Prüfe Passwort-Länge (maximal 128 Zeichen)
        if (formData.password.length > 128) {
          setError('Passwort ist zu lang. Bitte verwenden Sie maximal 128 Zeichen.')
          setLoading(false)
          return
        }
        await api.register(formData.name, formData.email, formData.password)
        // Nach Registrierung automatisch einloggen
        await api.login(formData.email, formData.password)
        onClose()
        window.location.reload()
      }
    } catch (err) {
      setError(err.message || 'Ein Fehler ist aufgetreten')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <h2>{isLogin ? 'Anmelden' : 'Registrieren'}</h2>
          <p className="modal-subtitle">
            {isLogin 
              ? 'Willkommen zurück bei RoboAdvisor' 
              : 'Erstelle dein Konto für digitale Finanzberatung'}
          </p>
        </div>

        <div className="modal-tabs">
          <button 
            className={`tab-button ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Anmelden
          </button>
          <button 
            className={`tab-button ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Registrieren
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required={!isLogin}
                placeholder="Dein Name"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">E-Mail</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="deine@email.de"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Passwort</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="••••••••"
              minLength="6"
            />
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Passwort bestätigen</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required={!isLogin}
                placeholder="••••••••"
                minLength="6"
              />
            </div>
          )}

          {isLogin && (
            <div className="form-options">
              <label className="checkbox-label">
                <input type="checkbox" />
                <span>Angemeldet bleiben</span>
              </label>
              <a href="#" className="forgot-password">Passwort vergessen?</a>
            </div>
          )}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Wird verarbeitet...' : (isLogin ? 'Anmelden' : 'Konto erstellen')}
          </button>
        </form>

        <div className="modal-footer">
          <p>
            {isLogin ? (
              <>
                Noch kein Konto?{' '}
                <button 
                  className="link-button" 
                  onClick={() => setIsLogin(false)}
                >
                  Jetzt registrieren
                </button>
              </>
            ) : (
              <>
                Bereits ein Konto?{' '}
                <button 
                  className="link-button" 
                  onClick={() => setIsLogin(true)}
                >
                  Jetzt anmelden
                </button>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginModal

