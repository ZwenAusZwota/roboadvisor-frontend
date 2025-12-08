import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../hooks/useToast'
import ToastContainer from '../components/ToastContainer'
import PortfolioList from '../components/portfolio/PortfolioList'
import ManualEntry from '../components/portfolio/ManualEntry'
import CSVUpload from '../components/portfolio/CSVUpload'
import './Portfolio.css'

const Portfolio = () => {
  const navigate = useNavigate()
  const { toasts, removeToast, showSuccess, showError } = useToast()
  const [activeTab, setActiveTab] = useState('list')
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const tabs = [
    { id: 'list', label: 'Mein Portfolio' },
    { id: 'manual', label: 'Manuell hinzufügen' },
    { id: 'csv', label: 'CSV-Upload' },
  ]

  return (
    <>
      <div className="portfolio-container">
        <div className="portfolio-content">
          <div className="portfolio-header">
            <h1>Portfolio Management</h1>
            <button 
              className="btn-secondary"
              onClick={() => navigate('/')}
            >
              Zurück zur Startseite
            </button>
          </div>

          <div className="portfolio-tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="portfolio-tab-content">
            {activeTab === 'list' && (
              <PortfolioList 
                refreshTrigger={refreshTrigger}
                showSuccess={showSuccess}
                showError={showError}
                onRefresh={handleRefresh}
              />
            )}
            {activeTab === 'manual' && (
              <ManualEntry 
                showSuccess={showSuccess}
                showError={showError}
                onSuccess={() => {
                  setActiveTab('list')
                  handleRefresh()
                }}
              />
            )}
            {activeTab === 'csv' && (
              <CSVUpload 
                showSuccess={showSuccess}
                showError={showError}
                onSuccess={() => {
                  setActiveTab('list')
                  handleRefresh()
                }}
              />
            )}
          </div>
        </div>
      </div>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </>
  )
}

export default Portfolio

