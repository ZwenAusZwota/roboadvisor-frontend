import React, { useState } from 'react'
import api from '../../services/api'

const CSVUpload = ({ showSuccess, showError, onSuccess }) => {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.endsWith('.csv')) {
        showError('Bitte wählen Sie eine CSV-Datei aus')
        return
      }
      setFile(selectedFile)
      setUploadResult(null)
    }
  }

  const handleDownloadTemplate = async () => {
    try {
      await api.downloadCSVTemplate()
      showSuccess('Template erfolgreich heruntergeladen')
    } catch (err) {
      showError(err.message || 'Fehler beim Herunterladen des Templates')
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    
    if (!file) {
      showError('Bitte wählen Sie eine CSV-Datei aus')
      return
    }

    setUploading(true)
    setUploadResult(null)

    try {
      const result = await api.uploadPortfolioCSV(file)
      
      setUploadResult(result)
      
      if (result.success > 0) {
        showSuccess(`${result.success} Position(en) erfolgreich hinzugefügt`)
        if (result.errors.length > 0) {
          showError(`${result.errors.length} Fehler beim Import`)
        }
        if (onSuccess) {
          setTimeout(() => onSuccess(), 1000)
        }
      } else {
        showError('Keine Positionen konnten hinzugefügt werden')
      }
    } catch (err) {
      showError(err.message || 'Fehler beim Hochladen der CSV-Datei')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="csv-upload">
      <h2>Portfolio per CSV importieren</h2>
      
      <div className="csv-info">
        <p>
          Laden Sie Ihre Portfolio-Positionen aus einer CSV-Datei hoch. 
          Die Datei muss folgende Spalten enthalten:
        </p>
        <ul>
          <li><strong>name</strong> (erforderlich) - Name des Wertpapiers</li>
          <li><strong>purchase_date</strong> (erforderlich) - Kaufdatum (Format: YYYY-MM-DD, DD.MM.YYYY oder DD/MM/YYYY)</li>
          <li><strong>quantity</strong> (erforderlich) - Anzahl (unterstützt Dezimalzahlen, z.B. 11.532 oder 11,532)</li>
          <li><strong>purchase_price</strong> (erforderlich) - Kaufpreis pro Stück (z.B. 215.35 oder 215,35)</li>
          <li><strong>isin</strong> (optional) - ISIN (12 Zeichen)</li>
          <li><strong>ticker</strong> (optional) - Ticker-Symbol</li>
        </ul>
        <p className="csv-note">
          <strong>Hinweis:</strong> ISIN oder Ticker muss mindestens angegeben werden.
        </p>
        <p className="csv-note">
          <strong>Trennzeichen:</strong> Die CSV-Datei kann Komma (,) oder Semikolon (;) als Trennzeichen verwenden.
          Dezimalzahlen können sowohl mit Punkt (.) als auch mit Komma (,) eingegeben werden.
        </p>
      </div>

      <div className="csv-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={handleDownloadTemplate}
        >
          Template herunterladen
        </button>
      </div>

      <form onSubmit={handleUpload} className="csv-upload-form">
        <div className="form-group">
          <label htmlFor="csv-file">CSV-Datei auswählen</label>
          <input
            type="file"
            id="csv-file"
            accept=".csv,text/csv"
            onChange={handleFileChange}
            required
          />
          {file && (
            <div className="file-info">
              <span>Ausgewählte Datei: {file.name}</span>
              <span className="file-size">
                ({(file.size / 1024).toFixed(2)} KB)
              </span>
            </div>
          )}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn-primary"
            disabled={uploading || !file}
          >
            {uploading ? 'Hochladen...' : 'CSV hochladen'}
          </button>
        </div>
      </form>

      {uploadResult && (
        <div className="upload-result">
          <h3>Upload-Ergebnis</h3>
          <div className="result-success">
            <strong>Erfolgreich:</strong> {uploadResult.success} Position(en) hinzugefügt
          </div>
          {uploadResult.errors.length > 0 && (
            <div className="result-errors">
              <strong>Fehler ({uploadResult.errors.length}):</strong>
              <ul>
                {uploadResult.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
          {uploadResult.created.length > 0 && (
            <div className="result-created">
              <strong>Erstellt:</strong>
              <ul>
                {uploadResult.created.map((item) => (
                  <li key={item.id}>
                    {item.name} {item.isin ? `(ISIN: ${item.isin})` : `(Ticker: ${item.ticker})`}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default CSVUpload

