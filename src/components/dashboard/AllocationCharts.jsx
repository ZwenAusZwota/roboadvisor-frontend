import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const AllocationCharts = ({ allocation }) => {
  if (!allocation) return null

  const COLORS = [
    '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
    '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#a8edea'
  ]

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{data.name}</p>
          <p className="tooltip-value">{formatCurrency(data.value)}</p>
          <p className="tooltip-percent">{data.payload.percentage}%</p>
        </div>
      )
    }
    return null
  }

  const renderChart = (title, data, dataKey = 'value') => {
    if (!data || data.length === 0) {
      return (
        <div className="allocation-empty">
          <p>{title}: Keine Daten verfügbar</p>
        </div>
      )
    }

    return (
      <div className="allocation-chart">
        <h3>{title}</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percentage }) => `${name}: ${percentage}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey={dataKey}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return (
    <div className="allocation-charts">
      <div className="allocation-grid">
        {renderChart('Nach Branchen', allocation.by_sector)}
        {renderChart('Nach Regionen', allocation.by_region)}
        {renderChart('Nach Assetklassen', allocation.by_asset_class)}
      </div>
    </div>
  )
}

export default AllocationCharts

