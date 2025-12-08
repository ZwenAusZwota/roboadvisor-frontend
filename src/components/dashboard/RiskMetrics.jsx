import React from 'react'

const RiskMetrics = ({ metrics }) => {
  if (!metrics) return null

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A'
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const getBetaColor = (beta) => {
    if (!beta) return 'neutral'
    if (beta < 0.8) return 'low'
    if (beta > 1.2) return 'high'
    return 'medium'
  }

  const getVolatilityColor = (vol) => {
    if (!vol) return 'neutral'
    if (vol < 10) return 'low'
    if (vol > 20) return 'high'
    return 'medium'
  }

  const getSharpeColor = (sharpe) => {
    if (!sharpe) return 'neutral'
    if (sharpe > 1.5) return 'good'
    if (sharpe > 1.0) return 'medium'
    return 'low'
  }

  return (
    <div className="risk-metrics">
      <div className="risk-grid">
        <div className="risk-metric">
          <div className="risk-label">Beta</div>
          <div className={`risk-value ${getBetaColor(metrics.beta)}`}>
            {metrics.beta !== null && metrics.beta !== undefined ? metrics.beta.toFixed(2) : 'N/A'}
          </div>
          <div className="risk-description">
            {metrics.beta && (
              <>
                {metrics.beta < 0.8 && 'Niedriges Risiko'}
                {metrics.beta >= 0.8 && metrics.beta <= 1.2 && 'Marktdurchschnitt'}
                {metrics.beta > 1.2 && 'Höheres Risiko'}
              </>
            )}
          </div>
        </div>

        <div className="risk-metric">
          <div className="risk-label">Volatilität</div>
          <div className={`risk-value ${getVolatilityColor(metrics.volatility)}`}>
            {formatPercent(metrics.volatility)}
          </div>
          <div className="risk-description">
            {metrics.volatility && (
              <>
                {metrics.volatility < 10 && 'Niedrig'}
                {metrics.volatility >= 10 && metrics.volatility <= 20 && 'Moderat'}
                {metrics.volatility > 20 && 'Hoch'}
              </>
            )}
          </div>
        </div>

        <div className="risk-metric">
          <div className="risk-label">Sharpe Ratio</div>
          <div className={`risk-value ${getSharpeColor(metrics.sharpe_ratio)}`}>
            {metrics.sharpe_ratio !== null && metrics.sharpe_ratio !== undefined 
              ? metrics.sharpe_ratio.toFixed(2) 
              : 'N/A'}
          </div>
          <div className="risk-description">
            {metrics.sharpe_ratio && (
              <>
                {metrics.sharpe_ratio > 1.5 && 'Ausgezeichnet'}
                {metrics.sharpe_ratio > 1.0 && metrics.sharpe_ratio <= 1.5 && 'Gut'}
                {metrics.sharpe_ratio <= 1.0 && 'Verbesserungswürdig'}
              </>
            )}
          </div>
        </div>

        <div className="risk-metric">
          <div className="risk-label">Max. Drawdown</div>
          <div className={`risk-value ${metrics.max_drawdown && metrics.max_drawdown < -10 ? 'high' : 'medium'}`}>
            {formatPercent(metrics.max_drawdown)}
          </div>
          <div className="risk-description">
            Maximale Verlustphase
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskMetrics

