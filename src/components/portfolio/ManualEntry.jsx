import React, { useState } from 'react'
import api from '../../services/api'

const ManualEntry = ({ showSuccess, showError, onSuccess }) => {
  const [formData, setFormData] = useState({
    isin: '',
    ticker: '',
    name: '',
    purchase_date: '',
    quantity: '',
    purchase_price: '',
  })
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validierung
    if (!formData.name.trim()) {
      showError('Name ist erforderlich')
      return
    }

    if (!formData.isin && !formData.ticker) {
      showError('ISIN oder Ticker muss angegeben werden')
      return
    }

    if (!formData.purchase_date) {
      showError('Kaufdatum ist erforderlich')
      return
    }

    if (!formData.quantity || parseInt(formData.quantity) <= 0) {
      showError('Anzahl muss größer als 0 sein')
      return
    }

    if (!formData.purchase_price) {
      showError('Kaufpreis ist erforderlich')
      return
    }

    setSubmitting(true)

    try {
      await api.createPortfolioHolding({
        isin: formData.isin || null,
        ticker: formData.ticker || null,
        name: formData.name,
        purchase_date: formData.purchase_date,
        quantity: parseInt(formData.quantity),
        purchase_price: formData.purchase_price,
      })
      
      showSuccess('Position erfolgreich hinzugefügt')
      
      // Formular zurücksetzen
      setFormData({
        isin: '',
        ticker: '',
        name: '',
        purchase_date: '',
        quantity: '',
        purchase_price: '',
      })
      
      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Hinzufügen der Position')
    } finally {
      setSubmitting(false)
    }
  }

  // Heute als Standard-Datum setzen
  const today = new Date().toISOString().split('T')[0]

  return (
    <div className="manual-entry">
      <h2>Neue Position hinzufügen</h2>
      
      <form onSubmit={handleSubmit} className="portfolio-form">
        <div className="form-group">
          <label htmlFor="name">
            Name des Wertpapiers <span className="required">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="z.B. Apple Inc."
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="isin">ISIN</label>
            <input
              type="text"
              id="isin"
              name="isin"
              value={formData.isin}
              onChange={handleChange}
              placeholder="US0378331005"
              maxLength={12}
            />
            <small>12 Zeichen alphanumerisch</small>
          </div>

          <div className="form-group">
            <label htmlFor="ticker">Ticker</label>
            <input
              type="text"
              id="ticker"
              name="ticker"
              value={formData.ticker}
              onChange={handleChange}
              placeholder="AAPL"
              maxLength={20}
            />
          </div>
        </div>

        <div className="form-note">
          <small>Hinweis: ISIN oder Ticker muss angegeben werden</small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="purchase_date">
              Kaufdatum <span className="required">*</span>
            </label>
            <input
              type="date"
              id="purchase_date"
              name="purchase_date"
              value={formData.purchase_date}
              onChange={handleChange}
              required
              max={today}
            />
          </div>

          <div className="form-group">
            <label htmlFor="quantity">
              Anzahl <span className="required">*</span>
            </label>
            <input
              type="number"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              required
              min="1"
              step="1"
              placeholder="10"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="purchase_price">
            Kaufpreis pro Stück <span className="required">*</span>
          </label>
          <input
            type="text"
            id="purchase_price"
            name="purchase_price"
            value={formData.purchase_price}
            onChange={handleChange}
            required
            placeholder="150.50"
          />
          <small>Format: 150.50 oder 150,50</small>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? 'Hinzufügen...' : 'Position hinzufügen'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ManualEntry

