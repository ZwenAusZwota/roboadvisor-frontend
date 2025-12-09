import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const PerformanceChart = ({ data }) => {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="chart-empty">
        <p>Keine Performance-Daten verfügbar</p>
      </div>
    )
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
  }

  // Reduziere Datenpunkte für bessere Performance (alle 3 Tage)
  const chartData = data.data.filter((_, index) => index % 3 === 0 || index === data.data.length - 1)

  return (
    <div className="performance-chart">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            stroke="#718096"
            fontSize={12}
          />
          <YAxis 
            tickFormatter={formatCurrency}
            stroke="#718096"
            fontSize={12}
          />
          <Tooltip 
            formatter={(value) => formatCurrency(value)}
            labelFormatter={(label) => new Date(label).toLocaleDateString('de-DE')}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '10px'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#667eea" 
            strokeWidth={2}
            dot={false}
            name="Portfolio-Wert"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default PerformanceChart



