import React from 'react'
import './AIAnalysis.css'

/**
 * Komponente für die Analyse einer einzelnen Position
 * Zeigt fundamentale und technische Analyse für jede Position
 */
const AISinglePositionAnalysis = ({ fundamentalAnalysis, technicalAnalysis }) => {
  if (!fundamentalAnalysis && !technicalAnalysis) {
    return null
  }

  // Kombiniere fundamentale und technische Analyse nach Ticker
  const positions = new Map()

  // Füge fundamentale Analyse hinzu
  if (fundamentalAnalysis && Array.isArray(fundamentalAnalysis)) {
    fundamentalAnalysis.forEach((item) => {
      const ticker = item.ticker || 'N/A'
      positions.set(ticker, {
        ticker,
        fundamental: item,
        technical: null,
      })
    })
  }

  // Füge technische Analyse hinzu
  if (technicalAnalysis && Array.isArray(technicalAnalysis)) {
    technicalAnalysis.forEach((item) => {
      const ticker = item.ticker || 'N/A'
      if (positions.has(ticker)) {
        positions.get(ticker).technical = item
      } else {
        positions.set(ticker, {
          ticker,
          fundamental: null,
          technical: item,
        })
      }
    })
  }

  const getValuationColor = (valuation) => {
    switch (valuation?.toLowerCase()) {
      case 'undervalued':
        return 'valuation-undervalued'
      case 'overvalued':
        return 'valuation-overvalued'
      default:
        return 'valuation-fair'
    }
  }

  const getSignalColor = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'buy':
        return 'signal-buy'
      case 'sell':
        return 'signal-sell'
      default:
        return 'signal-hold'
    }
  }

  return (
    <div className="ai-position-analysis">
      <h3>Positionen-Analyse</h3>
      <div className="positions-list">
        {Array.from(positions.values()).map((position) => (
          <div key={position.ticker} className="position-analysis-card">
            <div className="position-header">
              <h4>{position.ticker}</h4>
            </div>
            
            {position.fundamental && (
              <div className="analysis-section fundamental">
                <h5>Fundamentale Analyse</h5>
                <p className="position-analysis-summary">{position.fundamental.summary}</p>
                <div className={`valuation-badge ${getValuationColor(position.fundamental.valuation)}`}>
                  Bewertung: {position.fundamental.valuation || 'fair'}
                </div>
              </div>
            )}

            {position.technical && (
              <div className="analysis-section technical">
                <h5>Technische Analyse</h5>
                <div className="technical-details">
                  <div className="detail-item">
                    <span className="detail-label">Trend:</span>
                    <span className="detail-value">{position.technical.trend || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">RSI:</span>
                    <span className="detail-value">{position.technical.rsi || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Signal:</span>
                    <span className={`detail-value signal ${getSignalColor(position.technical.signal)}`}>
                      {position.technical.signal || 'hold'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default AISinglePositionAnalysis

