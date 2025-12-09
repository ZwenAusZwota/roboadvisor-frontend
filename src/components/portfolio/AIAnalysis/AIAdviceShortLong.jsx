import React from 'react'
import './AIAnalysis.css'

/**
 * Komponente für kurzfristige und langfristige Empfehlungen
 */
const AIAdviceShortLong = ({ shortTermAdvice, longTermAdvice }) => {
  if (!shortTermAdvice && !longTermAdvice) {
    return null
  }

  return (
    <div className="ai-advice">
      <h3>Empfehlungen</h3>
      
      {shortTermAdvice && (
        <div className="advice-section short-term">
          <h4>🔄 Kurzfristige Empfehlungen</h4>
          <p>{shortTermAdvice}</p>
        </div>
      )}

      {longTermAdvice && (
        <div className="advice-section long-term">
          <h4>🎯 Langfristige Empfehlungen</h4>
          <p>{longTermAdvice}</p>
        </div>
      )}
    </div>
  )
}

export default AIAdviceShortLong





