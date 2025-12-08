import React, { useState, useEffect } from 'react'
import api from '../../services/api'

const PortfolioList = ({ refreshTrigger, showSuccess, showError, onRefresh }) => {
  const [holdings, setHoldings] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)

  useEffect(() => {
    loadPortfolio()
  }, [refreshTrigger])

  const loadPortfolio = async () => {
    try {
      setLoading(true)
      const data = await api.getPortfolio()
      setHoldings(data)
    } catch (err) {
      showError(err.message || 'Fehler beim Laden des Portfolios')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Möchten Sie diese Position wirklich löschen?')) {
      return
    }

    try {
      await api.deletePortfolioHolding(id)
      showSuccess('Position erfolgreich gelöscht')
      loadPortfolio()
    } catch (err) {
      showError(err.message || 'Fehler beim Löschen der Position')
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  if (loading) {
    return <div className="portfolio-loading">Lade Portfolio...</div>
  }

  if (holdings.length === 0) {
    return (
      <div className="portfolio-empty">
        <p>Ihr Portfolio ist noch leer.</p>
        <p>Fügen Sie Positionen manuell hinzu oder laden Sie eine CSV-Datei hoch.</p>
      </div>
    )
  }

  return (
    <div className="portfolio-list">
      <div className="portfolio-stats">
        <div className="stat-item">
          <span className="stat-label">Anzahl Positionen:</span>
          <span className="stat-value">{holdings.length}</span>
        </div>
      </div>

      <div className="holdings-table-container">
        <table className="holdings-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>ISIN</th>
              <th>Ticker</th>
              <th>Branche</th>
              <th>Kaufdatum</th>
              <th>Anzahl</th>
              <th>Kaufpreis</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding) => (
              <tr key={holding.id}>
                <td>{holding.name}</td>
                <td>{holding.isin || '-'}</td>
                <td>{holding.ticker || '-'}</td>
                <td>{holding.sector || '-'}</td>
                <td>{formatDate(holding.purchase_date)}</td>
                <td>{holding.quantity}</td>
                <td>{holding.purchase_price}</td>
                <td>
                  <button
                    className="btn-danger-small"
                    onClick={() => handleDelete(holding.id)}
                  >
                    Löschen
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PortfolioList

