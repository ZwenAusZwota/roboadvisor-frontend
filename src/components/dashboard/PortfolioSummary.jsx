import React from 'react'

const PortfolioSummary = ({ summary }) => {
  if (!summary) return null

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const gainLossClass = summary.total_gain_loss >= 0 ? 'positive' : 'negative'

  return (
    <div className="portfolio-summary">
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-label">Aktueller Depotwert</div>
          <div className="card-value primary">
            {summary.total_current_value > 0 
              ? formatCurrency(summary.total_current_value)
              : formatCurrency(summary.total_purchase_value)}
          </div>
          <div className="card-subtitle">
            {summary.position_count} Position{summary.position_count !== 1 ? 'en' : ''}
          </div>
        </div>

        <div className="summary-card">
          <div className="card-label">Kaufwert</div>
          <div className="card-value">
            {formatCurrency(summary.total_purchase_value)}
          </div>
        </div>

        <div className={`summary-card ${gainLossClass}`}>
          <div className="card-label">Gewinn/Verlust</div>
          <div className="card-value">
            {formatCurrency(summary.total_gain_loss)}
          </div>
          <div className="card-subtitle">
            {formatPercent(summary.total_gain_loss_percent)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PortfolioSummary

