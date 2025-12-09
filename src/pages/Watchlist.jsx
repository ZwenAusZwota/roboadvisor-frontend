import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../hooks/useToast'
import ToastContainer from '../components/ToastContainer'
import WatchlistList from '../components/watchlist/WatchlistList'
import WatchlistEntry from '../components/watchlist/WatchlistEntry'
import WatchlistAnalysis from '../components/watchlist/WatchlistAnalysis'
import './Watchlist.css'

const Watchlist = () => {
  const navigate = useNavigate()
  const { toasts, removeToast, showSuccess, showError } = useToast()
  const [activeTab, setActiveTab] = useState('list')
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  const tabs = [
    { id: 'list', label: 'Meine Watchlist' },
    { id: 'add', label: 'Asset hinzufügen' },
    { id: 'analyze', label: 'KI-Analyse' },
  ]

  return (
    <>
      <div className="watchlist-container">
        <div className="watchlist-content">
          <div className="watchlist-header">
            <h1>Watchlist</h1>
            <div className="header-actions">
              <button 
                className="btn-secondary"
                onClick={() => navigate('/portfolio')}
              >
                Portfolio anzeigen
              </button>
              <button 
                className="btn-secondary"
                onClick={() => navigate('/')}
              >
                Zurück zur Startseite
              </button>
            </div>
          </div>

          <div className="watchlist-tabs">
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

          <div className="watchlist-tab-content">
            {activeTab === 'list' && (
              <WatchlistList 
                refreshTrigger={refreshTrigger}
                showSuccess={showSuccess}
                showError={showError}
                onRefresh={handleRefresh}
              />
            )}
            {activeTab === 'add' && (
              <WatchlistEntry 
                showSuccess={showSuccess}
                showError={showError}
                onSuccess={() => {
                  setActiveTab('list')
                  handleRefresh()
                }}
              />
            )}
            {activeTab === 'analyze' && (
              <WatchlistAnalysis />
            )}
          </div>
        </div>
      </div>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </>
  )
}

export default Watchlist
