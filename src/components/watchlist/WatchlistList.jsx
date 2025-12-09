import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import AnalysisHistoryModal from '../analysis/AnalysisHistoryModal'

const WatchlistList = ({ refreshTrigger, showSuccess, showError, onRefresh }) => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedItem, setSelectedItem] = useState(null)
  const [showHistoryModal, setShowHistoryModal] = useState(false)

  useEffect(() => {
    loadWatchlist()
  }, [refreshTrigger])

  const loadWatchlist = async () => {
    try {
      setLoading(true)
      const data = await api.getWatchlist()
      setItems(data)
    } catch (err) {
      showError(err.message || 'Fehler beim Laden der Watchlist')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Möchten Sie diesen Eintrag wirklich aus der Watchlist entfernen?')) {
      return
    }

    try {
      await api.deleteWatchlistItem(id)
      showSuccess('Eintrag erfolgreich entfernt')
      loadWatchlist()
    } catch (err) {
      showError(err.message || 'Fehler beim Löschen des Eintrags')
    }
  }

  if (loading) {
    return <div className="watchlist-loading">Lade Watchlist...</div>
  }

  if (items.length === 0) {
    return (
      <div className="watchlist-empty">
        <p>Ihre Watchlist ist noch leer.</p>
        <p>Fügen Sie Assets hinzu, die Sie beobachten möchten.</p>
      </div>
    )
  }

  return (
    <div className="watchlist-list">
      <div className="watchlist-stats">
        <div className="stat-item">
          <span className="stat-label">Anzahl Einträge:</span>
          <span className="stat-value">{items.length}</span>
        </div>
      </div>

      <div className="watchlist-table-container">
        <table className="watchlist-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>ISIN</th>
              <th>Ticker</th>
              <th>Branche</th>
              <th>Region</th>
              <th>Assetklasse</th>
              <th>Notizen</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr 
                key={item.id}
                className="watchlist-row-clickable"
                onClick={() => {
                  setSelectedItem(item)
                  setShowHistoryModal(true)
                }}
                style={{ cursor: 'pointer' }}
              >
                <td>{item.name}</td>
                <td>{item.isin || '-'}</td>
                <td>{item.ticker || '-'}</td>
                <td>{item.sector || '-'}</td>
                <td>{item.region || '-'}</td>
                <td>{item.asset_class || '-'}</td>
                <td>{item.notes || '-'}</td>
                <td onClick={(e) => e.stopPropagation()}>
                  <button
                    className="btn-danger-small"
                    onClick={() => handleDelete(item.id)}
                  >
                    Entfernen
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showHistoryModal && selectedItem && (
        <AnalysisHistoryModal
          isOpen={showHistoryModal}
          onClose={() => {
            setShowHistoryModal(false)
            setSelectedItem(null)
          }}
          type="watchlist"
          itemId={selectedItem.id}
          assetName={selectedItem.name}
          assetIsin={selectedItem.isin}
          assetTicker={selectedItem.ticker}
        />
      )}
    </div>
  )
}

export default WatchlistList
