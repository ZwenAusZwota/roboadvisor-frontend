import React from 'react'
import './AIAnalysis.css'

/**
 * Komponente für Rebalancing-Vorschläge
 * Zeigt Vorschläge zur Portfolio-Umstrukturierung
 */
const AIRebalancingSuggestions = ({ diversification, suggestedRebalancing }) => {
  if (!diversification && !suggestedRebalancing) {
    return null
  }

  return (
    <div className="ai-rebalancing">
      <h3>Rebalancing & Diversifikation</h3>

      {diversification && (
        <div className="diversification-breakdown">
          {diversification.sectorBreakdown && Object.keys(diversification.sectorBreakdown).length > 0 && (
            <div className="breakdown-section">
              <h4>Branchenverteilung</h4>
              <div className="breakdown-list">
                {Object.entries(diversification.sectorBreakdown).map(([sector, weight]) => (
                  <div key={sector} className="breakdown-item">
                    <div className="breakdown-label">{sector}</div>
                    <div className="breakdown-bar">
                      <div 
                        className="breakdown-fill" 
                        style={{ width: `${Math.min(weight, 100)}%` }}
                      />
                    </div>
                    <div className="breakdown-value">{weight.toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {diversification.regionBreakdown && Object.keys(diversification.regionBreakdown).length > 0 && (
            <div className="breakdown-section">
              <h4>Regionsverteilung</h4>
              <div className="breakdown-list">
                {Object.entries(diversification.regionBreakdown).map(([region, weight]) => (
                  <div key={region} className="breakdown-item">
                    <div className="breakdown-label">{region}</div>
                    <div className="breakdown-bar">
                      <div 
                        className="breakdown-fill" 
                        style={{ width: `${Math.min(weight, 100)}%` }}
                      />
                    </div>
                    <div className="breakdown-value">{weight.toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {diversification.positionWeights && Object.keys(diversification.positionWeights).length > 0 && (
            <div className="breakdown-section">
              <h4>Position-Gewichtungen</h4>
              <div className="breakdown-list">
                {Object.entries(diversification.positionWeights)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 10) // Top 10 Positionen
                  .map(([position, weight]) => (
                    <div key={position} className="breakdown-item">
                      <div className="breakdown-label">{position}</div>
                      <div className="breakdown-bar">
                        <div 
                          className="breakdown-fill" 
                          style={{ width: `${Math.min(weight, 100)}%` }}
                        />
                      </div>
                      <div className="breakdown-value">{weight.toFixed(1)}%</div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}

      {suggestedRebalancing && (
        <div className="rebalancing-suggestions">
          <h4>Rebalancing-Empfehlungen</h4>
          <p>{suggestedRebalancing}</p>
        </div>
      )}
    </div>
  )
}

export default AIRebalancingSuggestions

