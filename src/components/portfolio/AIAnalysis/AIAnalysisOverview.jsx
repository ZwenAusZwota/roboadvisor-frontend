import React from 'react'
import './AIAnalysis.css'

/**
 * Übersichtskomponente für AI-Analyse
 * Zeigt eine Zusammenfassung der Portfolio-Analyse an
 */
const AIAnalysisOverview = ({ analysis }) => {
  if (!analysis) {
    return null
  }

  return (
    <div className="ai-analysis-overview">
      <h3>KI-Analyse Übersicht</h3>
      <div className="analysis-summary-grid">
        <div className="summary-item">
          <span className="summary-label">Risiken identifiziert:</span>
          <span className="summary-value">{analysis.risks?.length || 0}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Positionen analysiert:</span>
          <span className="summary-value">{analysis.fundamentalAnalysis?.length || 0}</span>
        </div>
        {analysis.cached && (
          <div className="summary-item cached-badge">
            <span className="summary-label">Status:</span>
            <span className="summary-value">Aus Cache</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default AIAnalysisOverview

