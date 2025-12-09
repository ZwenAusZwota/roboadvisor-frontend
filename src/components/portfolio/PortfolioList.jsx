import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import AnalysisHistoryModal from '../analysis/AnalysisHistoryModal'

const PortfolioList = ({ refreshTrigger, showSuccess, showError, onRefresh }) => {
  const [holdings, setHoldings] = useState([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [selectedHolding, setSelectedHolding] = useState(null)
  const [showHistoryModal, setShowHistoryModal] = useState(false)

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
              <th>Region</th>
              <th>Assetklasse</th>
              <th>Kaufdatum</th>
              <th>Anzahl</th>
              <th>Kaufpreis</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding) => (
              <tr 
                key={holding.id}
                className="portfolio-row-clickable"
                onClick={() => {
                  setSelectedHolding(holding)
                  setShowHistoryModal(true)
                }}
                style={{ cursor: 'pointer' }}
              >
                <td>{holding.name}</td>
                <td>{holding.isin || '-'}</td>
                <td>{holding.ticker || '-'}</td>
                <td>{holding.sector || '-'}</td>
                <td>{holding.region || '-'}</td>
                <td>{holding.asset_class || '-'}</td>
                <td>{formatDate(holding.purchase_date)}</td>
                <td>{holding.quantity}</td>
                <td>{holding.purchase_price}</td>
                <td onClick={(e) => e.stopPropagation()}>
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

      {showHistoryModal && selectedHolding && (
        <AnalysisHistoryModal
          isOpen={showHistoryModal}
          onClose={() => {
            setShowHistoryModal(false)
            setSelectedHolding(null)
          }}
          type="portfolio"
          itemId={selectedHolding.id}
          assetName={selectedHolding.name}
          assetIsin={selectedHolding.isin}
          assetTicker={selectedHolding.ticker}
        />
      )}
    </div>
  )
}

export default PortfolioList

