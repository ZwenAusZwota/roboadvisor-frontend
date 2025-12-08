import React, { useState } from 'react'
import api from '../../services/api'

const ManualEntry = ({ showSuccess, showError, onSuccess }) => {
  const [formData, setFormData] = useState({
    isin: '',
    ticker: '',
    name: '',
    purchase_date: '',
    purchase_date_text: '',
    quantity: '',
    purchase_price: '',
  })
  const [dateInputType, setDateInputType] = useState('date') // 'date' oder 'text'
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    const value = e.target.value
    setFormData({
      ...formData,
      [e.target.name]: value,
    })
    
    // Synchronisiere Date-Picker und Text-Eingabe
    if (e.target.name === 'purchase_date') {
      setFormData(prev => ({
        ...prev,
        purchase_date_text: value ? new Date(value).toLocaleDateString('de-DE') : ''
      }))
    } else if (e.target.name === 'purchase_date_text') {
      // Versuche Text-Datum zu parsen
      try {
        const date = parseDateText(value)
        if (date) {
          setFormData(prev => ({
            ...prev,
            purchase_date: date.toISOString().split('T')[0]
          }))
        }
      } catch (e) {
        // Ignoriere Parsing-Fehler während der Eingabe
      }
    }
  }

  const parseDateText = (dateText) => {
    if (!dateText || !dateText.trim()) return null
    
    // Unterstützte Formate
    const formats = [
      /^(\d{4})-(\d{2})-(\d{2})$/,           // YYYY-MM-DD
      /^(\d{2})\.(\d{2})\.(\d{4})$/,         // DD.MM.YYYY
      /^(\d{2})\/(\d{2})\/(\d{4})$/,         // DD/MM/YYYY
      /^(\d{1,2})\.(\d{1,2})\.(\d{4})$/,     // D.M.YYYY
      /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/,     // D/M/YYYY
    ]
    
    for (const format of formats) {
      const match = dateText.trim().match(format)
      if (match) {
        let year, month, day
        if (format.source.includes('YYYY')) {
          // Format mit Jahr am Ende
          day = parseInt(match[1], 10)
          month = parseInt(match[2], 10)
          year = parseInt(match[3], 10)
        } else {
          // Format mit Jahr am Anfang
          year = parseInt(match[1], 10)
          month = parseInt(match[2], 10)
          day = parseInt(match[3], 10)
        }
        
        if (year >= 1900 && year <= 2100 && month >= 1 && month <= 12 && day >= 1 && day <= 31) {
          return new Date(year, month - 1, day)
        }
      }
    }
    
    return null
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

    if (!formData.purchase_date && !formData.purchase_date_text) {
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

    // Bestimme das zu sendende Datum
    let purchaseDate = formData.purchase_date
    if (!purchaseDate && formData.purchase_date_text) {
      const parsedDate = parseDateText(formData.purchase_date_text)
      if (parsedDate) {
        purchaseDate = parsedDate.toISOString().split('T')[0]
      } else {
        // Sende Text-Datum direkt, Backend kann es parsen
        purchaseDate = formData.purchase_date_text.trim()
      }
    }

    if (!purchaseDate) {
      showError('Kaufdatum ist erforderlich')
      return
    }

    // Bereite Daten für API vor
    const holdingData = {
      name: formData.name.trim(),
      purchase_date: purchaseDate,
      quantity: parseInt(formData.quantity),
      purchase_price: formData.purchase_price.trim(),
    }

    // Füge ISIN/Ticker nur hinzu, wenn sie nicht leer sind
    const isin = formData.isin.trim()
    const ticker = formData.ticker.trim()
    
    if (isin) {
      holdingData.isin = isin
    }
    if (ticker) {
      holdingData.ticker = ticker
    }

    try {
      await api.createPortfolioHolding(holdingData)
      
      showSuccess('Position erfolgreich hinzugefügt')
      
      // Formular zurücksetzen
      setFormData({
        isin: '',
        ticker: '',
        name: '',
        purchase_date: '',
        purchase_date_text: '',
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
            <div className="date-input-container">
              <div className="date-input-toggle">
                <button
                  type="button"
                  className={`date-toggle-btn ${dateInputType === 'date' ? 'active' : ''}`}
                  onClick={() => setDateInputType('date')}
                >
                  Kalender
                </button>
                <button
                  type="button"
                  className={`date-toggle-btn ${dateInputType === 'text' ? 'active' : ''}`}
                  onClick={() => setDateInputType('text')}
                >
                  Text
                </button>
              </div>
              {dateInputType === 'date' ? (
                <input
                  type="date"
                  id="purchase_date"
                  name="purchase_date"
                  value={formData.purchase_date}
                  onChange={handleChange}
                  required
                  max={today}
                />
              ) : (
                <input
                  type="text"
                  id="purchase_date_text"
                  name="purchase_date_text"
                  value={formData.purchase_date_text}
                  onChange={handleChange}
                  required
                  placeholder="DD.MM.YYYY oder YYYY-MM-DD"
                />
              )}
            </div>
            <small>
              Unterstützte Formate: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY
            </small>
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

