import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import LoginModal from './LoginModal'
import BackendStatus from './BackendStatus'
import './Header.css'

const Header = () => {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)

  return (
    <>
      <header className="header">
        <div className="header-container">
          <div className="header-brand">
            <h1 className="logo">RoboAdvisor</h1>
            <p className="tagline">Ihr smarter Partner für digitale Finanzberatung</p>
          </div>
          <div className="header-right">
            <BackendStatus />
            <nav className="nav">
              <ul className="nav-list">
                <li><Link to="/" className="nav-link">Home</Link></li>
                <li><Link to="/contact" className="nav-link">Kontakt</Link></li>
                <li>
                  <button 
                    className="nav-link login-button" 
                    onClick={() => setIsLoginModalOpen(true)}
                  >
                    Login
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </header>
      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => setIsLoginModalOpen(false)} 
      />
    </>
  )
}

export default Header

