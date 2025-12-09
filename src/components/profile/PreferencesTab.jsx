import React, { useState, useEffect } from 'react'
import { useUserSettings } from '../../hooks/useUserSettings'

const PreferencesTab = ({ showSuccess, showError }) => {
  const { settings, updateSettings, loading } = useUserSettings()
  const [formData, setFormData] = useState({
    timezone: '',
    language: 'de',
    currency: 'EUR',
    riskProfile: '',
    investmentHorizon: '',
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (settings) {
      setFormData({
        timezone: settings.timezone || 'Europe/Berlin',
        language: settings.language || 'de',
        currency: settings.currency || 'EUR',
        riskProfile: settings.riskProfile || '',
        investmentHorizon: settings.investmentHorizon || '',
      })
    }
  }, [settings])

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)

    try {
      const result = await updateSettings(formData)
      if (result.success) {
        showSuccess('Einstellungen erfolgreich aktualisiert')
      } else {
        showError(result.error || 'Fehler beim Aktualisieren der Einstellungen')
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Aktualisieren der Einstellungen')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="profile-tab">Lade Einstellungen...</div>
  }

  return (
    <div className="profile-tab">
      <h2>Einstellungen</h2>
      
      <form onSubmit={handleSubmit} className="profile-form">
        <div className="form-group">
          <label htmlFor="timezone">Zeitzone</label>
          <input
            type="text"
            id="timezone"
            name="timezone"
            value={formData.timezone}
            onChange={handleChange}
            placeholder="Europe/Berlin"
          />
          <small>Beispiel: Europe/Berlin, America/New_York, Asia/Tokyo</small>
        </div>

        <div className="form-group">
          <label htmlFor="language">Sprache</label>
          <select
            id="language"
            name="language"
            value={formData.language}
            onChange={handleChange}
          >
            <option value="de">Deutsch</option>
            <option value="en">English</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="currency">Währung</label>
          <select
            id="currency"
            name="currency"
            value={formData.currency}
            onChange={handleChange}
          >
            <option value="EUR">EUR (Euro)</option>
            <option value="USD">USD (US Dollar)</option>
            <option value="CHF">CHF (Schweizer Franken)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="riskProfile">Risikoprofil</label>
          <select
            id="riskProfile"
            name="riskProfile"
            value={formData.riskProfile}
            onChange={handleChange}
          >
            <option value="">Bitte wählen</option>
            <option value="conservative">Konservativ</option>
            <option value="balanced">Ausgewogen</option>
            <option value="growth">Wachstum</option>
            <option value="aggressive">Aggressiv</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="investmentHorizon">Anlagehorizont</label>
          <select
            id="investmentHorizon"
            name="investmentHorizon"
            value={formData.investmentHorizon}
            onChange={handleChange}
          >
            <option value="">Bitte wählen</option>
            <option value="short">Kurzfristig (&lt; 1 Jahr)</option>
            <option value="medium">Mittelfristig (1-5 Jahre)</option>
            <option value="long">Langfristig (&gt; 5 Jahre)</option>
          </select>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Speichern...' : 'Speichern'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default PreferencesTab





