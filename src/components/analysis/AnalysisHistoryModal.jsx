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
              {history.map((entry, index) => {
                const fa = entry.analysis_data?.fundamentalAnalysis
                const ta = entry.analysis_data?.technicalAnalysis
                const hasData = fa || ta || entry.analysis_data?.recommendation || entry.analysis_data?.risks?.length > 0
                
                return (
                  <div key={entry.id || index} className="history-entry">
                    <div className="history-date">{formatDate(entry.created_at)}</div>
                    
                    {!hasData && (
                      <div className="history-section">
                        <p className="history-no-data">Keine detaillierten Analysedaten verfügbar für diesen Eintrag.</p>
                      </div>
                    )}
                    
                    {fa && typeof fa === 'object' && (
                      <div className="history-section">
                        <h4>Fundamentale Analyse</h4>
                        {fa.summary && <p>{fa.summary}</p>}
                        {fa.valuation && (
                          <div className={`valuation-badge valuation-${fa.valuation || 'fair'}`}>
                            Bewertung: {fa.valuation}
                          </div>
                        )}
                        {fa.strengths && Array.isArray(fa.strengths) && fa.strengths.length > 0 && (
                          <div className="history-list">
                            <strong>Stärken:</strong>
                            <ul>
                              {fa.strengths.map((strength, i) => (
                                <li key={i}>{strength}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {fa.weaknesses && Array.isArray(fa.weaknesses) && fa.weaknesses.length > 0 && (
                          <div className="history-list">
                            <strong>Schwächen:</strong>
                            <ul>
                              {fa.weaknesses.map((weakness, i) => (
                                <li key={i}>{weakness}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {ta && typeof ta === 'object' && (
                      <div className="history-section">
                        <h4>Technische Analyse</h4>
                        <div className="technical-details">
                          {ta.trend && (
                            <div className="detail-item">
                              <span className="detail-label">Trend:</span>
                              <span className="detail-value">{ta.trend}</span>
                            </div>
                          )}
                          {ta.rsi && (
                            <div className="detail-item">
                              <span className="detail-label">RSI:</span>
                              <span className="detail-value">{ta.rsi}</span>
                            </div>
                          )}
                          {ta.signal && (
                            <div className="detail-item">
                              <span className="detail-label">Signal:</span>
                              <span className={`detail-value signal signal-${ta.signal.toLowerCase() || 'hold'}`}>
                                {ta.signal}
                              </span>
                            </div>
                          )}
                          {ta.supportLevel && (
                            <div className="detail-item">
                              <span className="detail-label">Support:</span>
                              <span className="detail-value">{ta.supportLevel}</span>
                            </div>
                          )}
                          {ta.resistanceLevel && (
                            <div className="detail-item">
                              <span className="detail-label">Resistance:</span>
                              <span className="detail-value">{ta.resistanceLevel}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {entry.analysis_data?.risks && Array.isArray(entry.analysis_data.risks) && entry.analysis_data.risks.length > 0 && (
                      <div className="history-section">
                        <h4>Risiken</h4>
                        <ul className="history-risk-list">
                          {entry.analysis_data.risks.map((risk, i) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {entry.analysis_data?.recommendation && (
                      <div className="history-section">
                        <h4>Empfehlung</h4>
                        <p>{entry.analysis_data.recommendation}</p>
                      </div>
                    )}

                    {entry.analysis_data?.priceTarget && (
                      <div className="history-section">
                        <h4>Preisziel</h4>
                        <p>{entry.analysis_data.priceTarget}</p>
                      </div>
                    )}
                  </div>
                )
              })}
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



