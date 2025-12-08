import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../hooks/useToast'
import ToastContainer from '../components/ToastContainer'
import PortfolioSummary from '../components/dashboard/PortfolioSummary'
import PerformanceChart from '../components/dashboard/PerformanceChart'
import AllocationCharts from '../components/dashboard/AllocationCharts'
import RiskMetrics from '../components/dashboard/RiskMetrics'
import PositionsTable from '../components/dashboard/PositionsTable'
import api from '../services/api'
import './Dashboard.css'

const Dashboard = () => {
  const navigate = useNavigate()
  const { toasts, removeToast, showError } = useToast()
  const [summary, setSummary] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [allocation, setAllocation] = useState(null)
  const [riskMetrics, setRiskMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [summaryData, performanceData, allocationData, riskData] = await Promise.all([
        api.getPortfolioSummary(),
        api.getPerformanceHistory(30),
        api.getPortfolioAllocation(),
        api.getRiskMetrics(),
      ])
      
      setSummary(summaryData)
      setPerformance(performanceData)
      setAllocation(allocationData)
      setRiskMetrics(riskData)
    } catch (err) {
      showError(err.message || 'Fehler beim Laden der Dashboard-Daten')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-content">
          <p>Lade Dashboard...</p>
        </div>
      </div>
    )
  }

  if (!summary || summary.position_count === 0) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>Mein Portfolio</h1>
            <button 
              className="btn-secondary"
              onClick={() => navigate('/portfolio')}
            >
              Portfolio verwalten
            </button>
          </div>
          <div className="dashboard-empty">
            <p>Ihr Portfolio ist noch leer.</p>
            <p>Fügen Sie Positionen hinzu, um das Dashboard zu sehen.</p>
            <button 
              className="btn-primary"
              onClick={() => navigate('/portfolio')}
            >
              Erste Position hinzufügen
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="dashboard-container">
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>Mein Portfolio</h1>
            <button 
              className="btn-secondary"
              onClick={() => navigate('/portfolio')}
            >
              Portfolio verwalten
            </button>
          </div>

          <PortfolioSummary summary={summary} />

          <div className="dashboard-grid">
            <div className="dashboard-widget performance-widget">
              <h2>Performance-Verlauf</h2>
              <PerformanceChart data={performance} />
            </div>

            <div className="dashboard-widget allocation-widget">
              <h2>Portfolio-Aufteilung</h2>
              <AllocationCharts allocation={allocation} />
            </div>

            <div className="dashboard-widget risk-widget">
              <h2>Risikoindikatoren</h2>
              <RiskMetrics metrics={riskMetrics} />
            </div>

            <div className="dashboard-widget positions-widget">
              <h2>Positionen im Detail</h2>
              <PositionsTable positions={summary.positions} />
            </div>
          </div>
        </div>
      </div>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </>
  )
}

export default Dashboard

