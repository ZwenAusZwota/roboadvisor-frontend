import React, { useState, useEffect } from 'react'
import { useUserSettings } from '../../hooks/useUserSettings'

const NotificationsTab = ({ showSuccess, showError }) => {
  const { settings, updateSettings, loading } = useUserSettings()
  const [notifications, setNotifications] = useState({
    dailyMarket: false,
    weeklySummary: false,
    aiRecommendations: false,
    riskWarnings: true,
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (settings?.notifications) {
      setNotifications({
        dailyMarket: settings.notifications.dailyMarket || false,
        weeklySummary: settings.notifications.weeklySummary || false,
        aiRecommendations: settings.notifications.aiRecommendations || false,
        riskWarnings: settings.notifications.riskWarnings !== false,
      })
    }
  }, [settings])

  const handleToggle = (key) => {
    setNotifications({
      ...notifications,
      [key]: !notifications[key],
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)

    try {
      const result = await updateSettings({ notifications })
      if (result.success) {
        showSuccess('Benachrichtigungseinstellungen erfolgreich aktualisiert')
      } else {
        showError(result.error || 'Fehler beim Aktualisieren der Benachrichtigungen')
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Aktualisieren der Benachrichtigungen')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="profile-tab">Lade Benachrichtigungen...</div>
  }

  return (
    <div className="profile-tab">
      <h2>Benachrichtigungen</h2>
      
      <form onSubmit={handleSubmit} className="profile-form">
        <div className="notification-item">
          <div className="notification-info">
            <h3>Tägliche Marktübersicht</h3>
            <p>Erhalten Sie täglich eine Zusammenfassung der Marktentwicklungen</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notifications.dailyMarket}
              onChange={() => handleToggle('dailyMarket')}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="notification-item">
          <div className="notification-info">
            <h3>Wöchentliche Zusammenfassung</h3>
            <p>Erhalten Sie wöchentlich eine Zusammenfassung Ihres Portfolios</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notifications.weeklySummary}
              onChange={() => handleToggle('weeklySummary')}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="notification-item">
          <div className="notification-info">
            <h3>KI-Empfehlungen</h3>
            <p>Erhalten Sie personalisierte Anlageempfehlungen basierend auf KI-Analysen</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notifications.aiRecommendations}
              onChange={() => handleToggle('aiRecommendations')}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>

        <div className="notification-item">
          <div className="notification-info">
            <h3>Risikowarnungen</h3>
            <p>Erhalten Sie Warnungen bei ungewöhnlichen Marktbewegungen oder Risiken</p>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notifications.riskWarnings}
              onChange={() => handleToggle('riskWarnings')}
            />
            <span className="toggle-slider"></span>
          </label>
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

export default NotificationsTab





