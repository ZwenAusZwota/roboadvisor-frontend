import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'

const PrivacyTab = ({ showSuccess, showError }) => {
  const navigate = useNavigate()
  const [exporting, setExporting] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState('')

  const handleExport = async () => {
    setExporting(true)
    try {
      await api.exportUserData()
      showSuccess('Datenexport erfolgreich gestartet')
    } catch (err) {
      showError(err.message || 'Fehler beim Exportieren der Daten')
    } finally {
      setExporting(false)
    }
  }

  const handleDelete = async () => {
    if (confirmDelete !== 'LÖSCHEN') {
      showError('Bitte geben Sie "LÖSCHEN" ein, um zu bestätigen')
      return
    }

    if (!window.confirm('Sind Sie sicher? Diese Aktion kann nicht rückgängig gemacht werden!')) {
      return
    }

    setDeleting(true)
    try {
      await api.deleteAccount()
      showSuccess('Konto erfolgreich gelöscht')
      api.logout()
      setTimeout(() => {
        navigate('/')
        window.location.reload()
      }, 2000)
    } catch (err) {
      showError(err.message || 'Fehler beim Löschen des Kontos')
      setDeleting(false)
    }
  }

  return (
    <div className="profile-tab">
      <h2>Datenschutz</h2>

      <div className="privacy-section">
        <h3>Datenexport</h3>
        <p className="privacy-info">
          Laden Sie alle Ihre gespeicherten Daten als JSON-Datei herunter.
        </p>
        <button
          className="btn-primary"
          onClick={handleExport}
          disabled={exporting}
        >
          {exporting ? 'Exportiere...' : 'Daten exportieren'}
        </button>
      </div>

      <div className="privacy-section danger-zone">
        <h3>Konto löschen</h3>
        <p className="privacy-info warning">
          <strong>Warnung:</strong> Das Löschen Ihres Kontos ist permanent und kann nicht rückgängig gemacht werden.
          Alle Ihre Daten, Einstellungen und Portfolios werden unwiderruflich gelöscht.
        </p>
        
        <form onSubmit={(e) => { e.preventDefault(); handleDelete(); }} className="profile-form">
          <div className="form-group">
            <label htmlFor="confirmDelete">
              Geben Sie "LÖSCHEN" ein, um zu bestätigen:
            </label>
            <input
              type="text"
              id="confirmDelete"
              value={confirmDelete}
              onChange={(e) => setConfirmDelete(e.target.value)}
              placeholder="LÖSCHEN"
              className={confirmDelete && confirmDelete !== 'LÖSCHEN' ? 'error' : ''}
            />
          </div>
          <div className="form-actions">
            <button
              type="submit"
              className="btn-danger"
              disabled={deleting || confirmDelete !== 'LÖSCHEN'}
            >
              {deleting ? 'Lösche...' : 'Konto endgültig löschen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PrivacyTab





