import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import './AnalysisHistoryModal.css'

/**
 * Modal zur Anzeige der Bewertungshistorie für ein Asset
 */
const AnalysisHistoryModal = ({ 
  isOpen, 
  onClose, 
  type, // 'portfolio' oder 'watchlist'
  itemId,
  assetName,
  assetIsin,
  assetTicker 
}) => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isOpen && itemId) {
      loadHistory()
    }
  }, [isOpen, itemId, type])

  const loadHistory = async () => {
    try {
      setLoading(true)
      setError(null)

      let data
      if (type === 'portfolio') {
        data = await api.getPortfolioHoldingHistory(itemId)
      } else if (type === 'watchlist') {
        data = await api.getWatchlistItemHistory(itemId)
      } else {
        // Fallback: Nach Asset suchen
        data = await api.getAssetHistory(assetIsin, assetTicker)
      }

      setHistory(data || [])
    } catch (err) {
      setError(err.message || 'Fehler beim Laden der Historie')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content analysis-history-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Bewertungshistorie: {assetName}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="history-loading">Lade Historie...</div>
          )}

          {error && (
            <div className="history-error">
              <strong>Fehler:</strong> {error}
            </div>
          )}

          {!loading && !error && history.length === 0 && (
            <div className="history-empty">
              <p>Noch keine Bewertungen vorhanden.</p>
              <p>Führen Sie eine Analyse durch, um die Historie zu sehen.</p>
            </div>
          )}

          {!loading && !error && history.length > 0 && (
            <div className="history-timeline">
              {history.map((entry, index) => (
                <div key={entry.id} className="history-entry">
                  <div className="history-date">{formatDate(entry.created_at)}</div>
                  
                  {entry.analysis_data?.fundamentalAnalysis && (
                    <div className="history-section">
                      <h4>Fundamentale Analyse</h4>
                      <p>{entry.analysis_data.fundamentalAnalysis.summary}</p>
                      <div className={`valuation-badge valuation-${entry.analysis_data.fundamentalAnalysis.valuation || 'fair'}`}>
                        Bewertung: {entry.analysis_data.fundamentalAnalysis.valuation || 'fair'}
                      </div>
                    </div>
                  )}

                  {entry.analysis_data?.technicalAnalysis && (
                    <div className="history-section">
                      <h4>Technische Analyse</h4>
                      <div className="technical-details">
                        <div className="detail-item">
                          <span className="detail-label">Trend:</span>
                          <span className="detail-value">{entry.analysis_data.technicalAnalysis.trend || 'N/A'}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">RSI:</span>
                          <span className="detail-value">{entry.analysis_data.technicalAnalysis.rsi || 'N/A'}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Signal:</span>
                          <span className={`detail-value signal signal-${entry.analysis_data.technicalAnalysis.signal?.toLowerCase() || 'hold'}`}>
                            {entry.analysis_data.technicalAnalysis.signal || 'hold'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Schließen</button>
        </div>
      </div>
    </div>
  )
}

export default AnalysisHistoryModal

