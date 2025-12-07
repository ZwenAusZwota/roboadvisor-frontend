import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import LoginModal from './LoginModal'
import BackendStatus from './BackendStatus'
import api from '../services/api'
import './Header.css'

const Header = () => {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [isHovered, setIsHovered] = useState(false)
  const [loading, setLoading] = useState(true)
  const [hoverTimeout, setHoverTimeout] = useState(null)
  const navigate = useNavigate()

  // Prüfe Login-Status beim Laden
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        try {
          const userData = await api.getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token ist ungültig, entferne es
          api.logout()
          setUser(null)
        }
      }
      setLoading(false)
    }
    checkAuth()
  }, [])

  // Event Listener für Token-Änderungen (z.B. nach Login)
  useEffect(() => {
    const handleStorageChange = async () => {
      const token = localStorage.getItem('auth_token')
      if (token && !user) {
        try {
          const userData = await api.getCurrentUser()
          setUser(userData)
        } catch (error) {
          api.logout()
          setUser(null)
        }
      } else if (!token) {
        setUser(null)
      }
    }

    // Prüfe beim Storage-Event (z.B. nach Login in anderem Tab)
    window.addEventListener('storage', handleStorageChange)
    
    // Prüfe auch bei Focus (falls Login in anderem Tab)
    window.addEventListener('focus', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleStorageChange)
    }
  }, [user])

  // Cleanup für Timeout beim Unmount
  useEffect(() => {
    return () => {
      if (hoverTimeout) {
        clearTimeout(hoverTimeout)
      }
    }
  }, [hoverTimeout])

  const handleLogout = () => {
    api.logout()
    setUser(null)
    setIsHovered(false)
    navigate('/')
    // Optional: Seite neu laden
    window.location.reload()
  }

  const handleProfileClick = () => {
    setIsHovered(false)
    navigate('/profile')
  }

  return (
    <>
      <header className="header">
        <div className="header-container">
          <div className="header-brand">
            <h1 className="logo">RoboAdvisor</h1>
            <p className="tagline">Ihr smarter Partner für digitale Finanzberatung</p>
          </div>
          <div className="header-right">
            <nav className="nav">
              <ul className="nav-list">
                <li><Link to="/" className="nav-link">Home</Link></li>
                <li><Link to="/contact" className="nav-link">Kontakt</Link></li>
                <li>
                  {loading ? (
                    <span className="nav-link">...</span>
                  ) : user ? (
                    <div 
                      className="user-menu-container"
                      onMouseEnter={() => {
                        // Lösche Timeout, falls vorhanden
                        if (hoverTimeout) {
                          clearTimeout(hoverTimeout)
                          setHoverTimeout(null)
                        }
                        setIsHovered(true)
                      }}
                      onMouseLeave={() => {
                        // Kleiner Delay bevor Menü geschlossen wird
                        const timeout = setTimeout(() => {
                          setIsHovered(false)
                        }, 200) // 200ms Delay
                        setHoverTimeout(timeout)
                      }}
                    >
                      <button className="nav-link user-name-button">
                        {user.name || user.email}
                      </button>
                      {isHovered && (
                        <div 
                          className="user-menu-dropdown"
                          onMouseEnter={() => {
                            // Lösche Timeout, falls vorhanden
                            if (hoverTimeout) {
                              clearTimeout(hoverTimeout)
                              setHoverTimeout(null)
                            }
                            setIsHovered(true)
                          }}
                          onMouseLeave={() => {
                            // Kleiner Delay bevor Menü geschlossen wird
                            const timeout = setTimeout(() => {
                              setIsHovered(false)
                            }, 200) // 200ms Delay
                            setHoverTimeout(timeout)
                          }}
                        >
                          <button 
                            className="user-menu-item"
                            onClick={handleProfileClick}
                          >
                            Profil
                          </button>
                          <button 
                            className="user-menu-item"
                            onClick={handleLogout}
                          >
                            Logout
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <button 
                      className="nav-link login-button" 
                      onClick={() => setIsLoginModalOpen(true)}
                    >
                      Login
                    </button>
                  )}
                </li>
              </ul>
            </nav>
            <BackendStatus />
          </div>
        </div>
      </header>
      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => {
          setIsLoginModalOpen(false)
          // Nach erfolgreichem Login User-Daten laden
          const token = localStorage.getItem('auth_token')
          if (token) {
            api.getCurrentUser()
              .then(userData => setUser(userData))
              .catch(() => setUser(null))
          }
        }} 
      />
    </>
  )
}

export default Header

