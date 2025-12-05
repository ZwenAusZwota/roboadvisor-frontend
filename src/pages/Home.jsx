import React from 'react'
import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">Dein digitaler Finanzberater</h1>
          <p className="hero-description">
            Optimierte Portfolios, intelligente Anlagestrategien – alles an einem Ort.
          </p>
          <button className="hero-button">Mehr erfahren</button>
        </div>
      </section>

      <section className="features">
        <div className="features-container">
          <Link to="/risk_profile" className="feature-card">
            <div className="feature-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <h3 className="feature-title">Risikoprofil</h3>
            <p className="feature-description">
              Erstelle dein individuelles Risikoprofil in wenigen Schritten.
            </p>
          </Link>

          <Link to="/portfolio" className="feature-card">
            <div className="feature-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
              </svg>
            </div>
            <h3 className="feature-title">Portfolio Management</h3>
            <p className="feature-description">
              Verwalte deine Wertpapiere und optimiere dein Portfolio.
            </p>
          </Link>
        </div>
      </section>
    </div>
  )
}

export default Home

