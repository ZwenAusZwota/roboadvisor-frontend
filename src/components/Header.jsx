import React from 'react'
import { Link } from 'react-router-dom'
import './Header.css'

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="header-brand">
          <h1 className="logo">RoboAdvisor</h1>
          <p className="tagline">Ihr smarter Partner für digitale Finanzberatung</p>
        </div>
        <nav className="nav">
          <ul className="nav-list">
            <li><Link to="/" className="nav-link">Home</Link></li>
            <li><Link to="/contact" className="nav-link">Kontakt</Link></li>
            <li><a href="#" className="nav-link">Login</a></li>
          </ul>
        </nav>
      </div>
    </header>
  )
}

export default Header

