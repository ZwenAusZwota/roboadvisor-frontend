import React from 'react'

const PositionsTable = ({ positions }) => {
  if (!positions || positions.length === 0) {
    return <div className="positions-empty">Keine Positionen verfügbar</div>
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A'
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <div className="positions-table-container">
      <table className="positions-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>ISIN/Ticker</th>
            <th>Anzahl</th>
            <th>Kaufpreis</th>
            <th>Aktueller Preis</th>
            <th>Kaufwert</th>
            <th>Aktueller Wert</th>
            <th>Gewinn/Verlust</th>
            <th>G/V %</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => {
            const gainLossClass = position.gain_loss >= 0 ? 'positive' : 'negative'
            return (
              <tr key={position.id}>
                <td className="position-name">{position.name}</td>
                <td>
                  {position.isin || position.ticker || '-'}
                </td>
                <td>{position.quantity.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</td>
                <td>{position.purchase_price}</td>
                <td>
                  {position.current_price 
                    ? formatCurrency(position.current_price)
                    : 'N/A'}
                </td>
                <td>{formatCurrency(position.purchase_value)}</td>
                <td>
                  {position.current_value 
                    ? formatCurrency(position.current_value)
                    : formatCurrency(position.purchase_value)}
                </td>
                <td className={gainLossClass}>
                  {position.gain_loss !== null && position.gain_loss !== undefined
                    ? formatCurrency(position.gain_loss)
                    : 'N/A'}
                </td>
                <td className={gainLossClass}>
                  {formatPercent(position.gain_loss_percent)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default PositionsTable



