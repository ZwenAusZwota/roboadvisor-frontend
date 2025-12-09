import React from 'react'
import './AIAnalysis.css'

/**
 * Komponente für Risiko-Übersicht
 * Zeigt identifizierte Risiken des Portfolios
 */
const AIRiskOverview = ({ risks, cashAssessment }) => {
  if ((!risks || risks.length === 0) && !cashAssessment) {
    return null
  }

  return (
    <div className="ai-risk-overview">
      <h3>Risiko-Analyse</h3>
      
      {risks && risks.length > 0 && (
        <div className="risks-list">
          {risks.map((risk, index) => (
            <div key={index} className="risk-item">
              <div className="risk-icon">⚠️</div>
              <div className="risk-text">{risk}</div>
            </div>
          ))}
        </div>
      )}

      {cashAssessment && (
        <div className="cash-assessment">
          <h4>Cash-Bewertung</h4>
          <p>{cashAssessment}</p>
        </div>
      )}
    </div>
  )
}

export default AIRiskOverview



