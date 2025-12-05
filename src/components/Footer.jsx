import React from 'react'
import { Link } from 'react-router-dom'
import './Footer.css'

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-links">
          <Link to="/" className="footer-link">Home</Link>
          <Link to="/contact" className="footer-link">Kontakt</Link>
        </div>
        <p className="footer-copyright">
          © 2025 RoboAdvisor. Alle Rechte vorbehalten.
        </p>
      </div>
    </footer>
  )
}

export default Footer

