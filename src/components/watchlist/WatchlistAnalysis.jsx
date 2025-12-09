import React from 'react'
import { useWatchlistAnalysis } from '../../hooks/useWatchlistAnalysis'
import { useToast } from '../../hooks/useToast'
import AISinglePositionAnalysis from '../portfolio/AIAnalysis/AISinglePositionAnalysis'
import './WatchlistAnalysis.css'

/**
 * Komponente für Watchlist-Analysen
 */
const WatchlistAnalysis = ({ itemId = null }) => {
  const { data, error, loading, runAnalysis } = useWatchlistAnalysis()
  const { showError, showSuccess } = useToast()

  const handleAnalyze = async () => {
    try {
      await runAnalysis(itemId, false)
      showSuccess('Watchlist-Analyse erfolgreich erstellt')
    } catch (err) {
      showError(err.message || 'Fehler bei der Watchlist-Analyse')
    }
  }

  const handleForceRefresh = async () => {
    try {
      await runAnalysis(itemId, true)
      showSuccess('Watchlist-Analyse aktualisiert')
    } catch (err) {
      showError(err.message || 'Fehler bei der Watchlist-Analyse')
    }
  }

  if (!itemId) {
    // Analysiere alle Items
    return (
      <div className="watchlist-analysis-container">
        <div className="watchlist-analysis-header">
          <h3>KI-Analyse für Watchlist</h3>
          <button
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? 'Analysiere...' : 'Alle analysieren'}
          </button>
        </div>

        {error && (
          <div className="watchlist-analysis-error">
            <strong>Fehler:</strong> {error}
          </div>
        )}

        {loading && !data && (
          <div className="watchlist-analysis-loading">
            Analysiere Watchlist-Assets...
          </div>
        )}

        {data && Array.isArray(data) && (
          <div className="watchlist-analysis-results">
            {data.map((item) => (
              <div key={item.item_id} className="watchlist-analysis-item">
                <h4>{item.asset_name}</h4>
                <AISinglePositionAnalysis
                  fundamentalAnalysis={item.fundamentalAnalysis ? [item.fundamentalAnalysis] : []}
                  technicalAnalysis={item.technicalAnalysis ? [item.technicalAnalysis] : []}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  // Analysiere einzelnes Item
  return (
    <div className="watchlist-analysis-container">
      <div className="watchlist-analysis-header">
        <h3>KI-Analyse</h3>
        <div className="header-actions">
          {data && (
            <button
              className="analyze-button"
              onClick={handleForceRefresh}
              disabled={loading}
            >
              Aktualisieren
            </button>
          )}
          <button
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? 'Analysiere...' : data ? 'Neu analysieren' : 'Analyse starten'}
          </button>
        </div>
      </div>

      {error && (
        <div className="watchlist-analysis-error">
          <strong>Fehler:</strong> {error}
        </div>
      )}

      {loading && !data && (
        <div className="watchlist-analysis-loading">
          Analysiere Asset...
        </div>
      )}

      {data && Array.isArray(data) && data.length > 0 && (
        <div className="watchlist-analysis-results">
          <AISinglePositionAnalysis
            fundamentalAnalysis={data[0].fundamentalAnalysis ? [data[0].fundamentalAnalysis] : []}
            technicalAnalysis={data[0].technicalAnalysis ? [data[0].technicalAnalysis] : []}
          />
        </div>
      )}
    </div>
  )
}

export default WatchlistAnalysis



