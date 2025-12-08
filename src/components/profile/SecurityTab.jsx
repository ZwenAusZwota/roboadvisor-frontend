import React, { useState, useEffect } from 'react'
import { useUserSettings } from '../../hooks/useUserSettings'
import api from '../../services/api'

const SecurityTab = ({ showSuccess, showError }) => {
  const { settings, refetch } = useUserSettings()
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [twoFactorForm, setTwoFactorForm] = useState({
    password: '',
  })
  const [changingPassword, setChangingPassword] = useState(false)
  const [setting2FA, setSetting2FA] = useState(false)

  const handlePasswordChange = (e) => {
    setPasswordForm({
      ...passwordForm,
      [e.target.name]: e.target.value,
    })
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      showError('Die neuen Passwörter stimmen nicht überein')
      return
    }

    if (passwordForm.newPassword.length < 6) {
      showError('Das neue Passwort muss mindestens 6 Zeichen lang sein')
      return
    }

    setChangingPassword(true)

    try {
      await api.changePassword(passwordForm.currentPassword, passwordForm.newPassword)
      showSuccess('Passwort erfolgreich geändert')
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      })
    } catch (err) {
      showError(err.message || 'Fehler beim Ändern des Passworts')
    } finally {
      setChangingPassword(false)
    }
  }

  const handle2FAChange = (e) => {
    setTwoFactorForm({
      ...twoFactorForm,
      [e.target.name]: e.target.value,
    })
  }

  const handle2FASubmit = async (enable) => {
    if (!twoFactorForm.password) {
      showError('Bitte geben Sie Ihr Passwort ein')
      return
    }

    setSetting2FA(true)

    try {
      const result = await api.setup2FA(enable, twoFactorForm.password)
      showSuccess(result.message || (enable ? '2FA erfolgreich aktiviert' : '2FA erfolgreich deaktiviert'))
      setTwoFactorForm({ password: '' })
      refetch()
    } catch (err) {
      showError(err.message || 'Fehler beim Einrichten der 2FA')
    } finally {
      setSetting2FA(false)
    }
  }

  return (
    <div className="profile-tab">
      <h2>Sicherheit</h2>

      <div className="security-section">
        <h3>Passwort ändern</h3>
        <form onSubmit={handlePasswordSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="currentPassword">Aktuelles Passwort</label>
            <input
              type="password"
              id="currentPassword"
              name="currentPassword"
              value={passwordForm.currentPassword}
              onChange={handlePasswordChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">Neues Passwort</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={passwordForm.newPassword}
              onChange={handlePasswordChange}
              required
              minLength={6}
            />
            <small>Mindestens 6 Zeichen</small>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Neues Passwort bestätigen</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={passwordForm.confirmPassword}
              onChange={handlePasswordChange}
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={changingPassword}>
              {changingPassword ? 'Ändern...' : 'Passwort ändern'}
            </button>
          </div>
        </form>
      </div>

      <div className="security-section">
        <h3>Zwei-Faktor-Authentifizierung (2FA)</h3>
        <p className="security-info">
          {settings?.two_factor_enabled
            ? '2FA ist derzeit aktiviert. Sie können sie hier deaktivieren.'
            : 'Aktivieren Sie die Zwei-Faktor-Authentifizierung für zusätzliche Sicherheit.'}
        </p>

        {!settings?.two_factor_enabled ? (
          <form className="profile-form">
            <div className="form-group">
              <label htmlFor="2fa-password">Passwort bestätigen</label>
              <input
                type="password"
                id="2fa-password"
                name="password"
                value={twoFactorForm.password}
                onChange={handle2FAChange}
                placeholder="Ihr Passwort zur Bestätigung"
              />
            </div>
            <div className="form-actions">
              <button
                type="button"
                className="btn-primary"
                onClick={() => handle2FASubmit(true)}
                disabled={setting2FA || !twoFactorForm.password}
              >
                {setting2FA ? 'Aktivieren...' : '2FA aktivieren'}
              </button>
            </div>
          </form>
        ) : (
          <form className="profile-form">
            <div className="form-group">
              <label htmlFor="2fa-disable-password">Passwort bestätigen</label>
              <input
                type="password"
                id="2fa-disable-password"
                name="password"
                value={twoFactorForm.password}
                onChange={handle2FAChange}
                placeholder="Ihr Passwort zur Bestätigung"
              />
            </div>
            <div className="form-actions">
              <button
                type="button"
                className="btn-danger"
                onClick={() => handle2FASubmit(false)}
                disabled={setting2FA || !twoFactorForm.password}
              >
                {setting2FA ? 'Deaktivieren...' : '2FA deaktivieren'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default SecurityTab

