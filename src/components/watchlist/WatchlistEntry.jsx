import React, { useState } from 'react'
import api from '../../services/api'

const WatchlistEntry = ({ showSuccess, showError, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    isin: '',
    ticker: '',
    sector: '',
    region: '',
    asset_class: '',
    notes: '',
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
    
    if (!formData.name.trim()) {
      showError('Name ist erforderlich')
      return
    }

    if (!formData.isin && !formData.ticker) {
      showError('ISIN oder Ticker muss angegeben werden')
      return
    }

    setSubmitting(true)

    try {
      await api.createWatchlistItem({
        name: formData.name.trim(),
        isin: formData.isin.trim() || null,
        ticker: formData.ticker.trim() || null,
        sector: formData.sector.trim() || null,
        region: formData.region.trim() || null,
        asset_class: formData.asset_class.trim() || null,
        notes: formData.notes.trim() || null,
      })
      showSuccess('Asset erfolgreich zur Watchlist hinzugefügt')
      setFormData({
        name: '',
        isin: '',
        ticker: '',
        sector: '',
        region: '',
        asset_class: '',
        notes: '',
      })
      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Hinzufügen zur Watchlist')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="watchlist-entry">
      <h3>Neues Asset zur Watchlist hinzufügen</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Name *</label>
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
              placeholder="z.B. US0378331005"
              maxLength={12}
            />
          </div>

          <div className="form-group">
            <label htmlFor="ticker">Ticker</label>
            <input
              type="text"
              id="ticker"
              name="ticker"
              value={formData.ticker}
              onChange={handleChange}
              placeholder="z.B. AAPL"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="sector">Branche</label>
            <input
              type="text"
              id="sector"
              name="sector"
              value={formData.sector}
              onChange={handleChange}
              placeholder="z.B. Technologie"
            />
          </div>

          <div className="form-group">
            <label htmlFor="region">Region</label>
            <input
              type="text"
              id="region"
              name="region"
              value={formData.region}
              onChange={handleChange}
              placeholder="z.B. Nordamerika"
            />
          </div>

          <div className="form-group">
            <label htmlFor="asset_class">Assetklasse</label>
            <input
              type="text"
              id="asset_class"
              name="asset_class"
              value={formData.asset_class}
              onChange={handleChange}
              placeholder="z.B. Aktien"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notizen</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={3}
            placeholder="Optionale Notizen zum Asset"
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={submitting}
        >
          {submitting ? 'Hinzufügen...' : 'Zur Watchlist hinzufügen'}
        </button>
      </form>
    </div>
  )
}

export default WatchlistEntry
