import React, { useState } from 'react'
import { useUserProfile } from '../../hooks/useUserSettings'

const ProfileTab = ({ showSuccess, showError }) => {
  const { profile, updateProfile } = useUserProfile()
  const [formData, setFormData] = useState({
    name: profile?.name || '',
    email: profile?.email || '',
  })
  const [isEditing, setIsEditing] = useState(false)
  const [saving, setSaving] = useState(false)

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
      const result = await updateProfile(formData)
      if (result.success) {
        showSuccess('Profil erfolgreich aktualisiert')
        setIsEditing(false)
      } else {
        showError(result.error || 'Fehler beim Aktualisieren des Profils')
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Aktualisieren des Profils')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: profile?.name || '',
      email: profile?.email || '',
    })
    setIsEditing(false)
  }

  return (
    <div className="profile-tab">
      <h2>Persönliche Informationen</h2>
      
      {!isEditing ? (
        <div className="profile-info">
          <div className="info-row">
            <span className="info-label">Name:</span>
            <span className="info-value">{profile?.name || 'Nicht angegeben'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">E-Mail:</span>
            <span className="info-value">{profile?.email}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Benutzer-ID:</span>
            <span className="info-value">#{profile?.id}</span>
          </div>
          <button className="btn-primary" onClick={() => setIsEditing(true)}>
            Bearbeiten
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Ihr Name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">E-Mail</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="ihre@email.de"
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Speichern...' : 'Speichern'}
            </button>
            <button type="button" className="btn-secondary" onClick={handleCancel}>
              Abbrechen
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

export default ProfileTab



