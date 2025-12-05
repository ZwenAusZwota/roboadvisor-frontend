import React from 'react'
import './Contact.css'

const Contact = () => {
  return (
    <div className="contact">
      <div className="contact-container">
        <h1 className="contact-title">Kontakt</h1>
        <p className="contact-description">
          Haben Sie Fragen? Wir helfen Ihnen gerne weiter.
        </p>
        <form className="contact-form">
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input type="text" id="name" name="name" required />
          </div>
          <div className="form-group">
            <label htmlFor="email">E-Mail</label>
            <input type="email" id="email" name="email" required />
          </div>
          <div className="form-group">
            <label htmlFor="message">Nachricht</label>
            <textarea id="message" name="message" rows="5" required></textarea>
          </div>
          <button type="submit" className="submit-button">Absenden</button>
        </form>
      </div>
    </div>
  )
}

export default Contact

