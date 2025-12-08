import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserProfile } from '../hooks/useUserSettings'
import { useToast } from '../hooks/useToast'
import ToastContainer from '../components/ToastContainer'
import ProfileTab from '../components/profile/ProfileTab'
import PreferencesTab from '../components/profile/PreferencesTab'
import NotificationsTab from '../components/profile/NotificationsTab'
import SecurityTab from '../components/profile/SecurityTab'
import PrivacyTab from '../components/profile/PrivacyTab'
import './Profile.css'

const Profile = () => {
  const navigate = useNavigate()
  const { profile, loading: profileLoading } = useUserProfile()
  const { toasts, removeToast, showSuccess, showError } = useToast()
  const [activeTab, setActiveTab] = useState('profile')

  if (profileLoading) {
    return (
      <div className="profile-container">
        <div className="profile-content">
          <p>Lade Profil...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="profile-container">
        <div className="profile-content">
          <div className="error-message">Fehler beim Laden des Profils</div>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'profile', label: 'Profil' },
    { id: 'preferences', label: 'Einstellungen' },
    { id: 'notifications', label: 'Benachrichtigungen' },
    { id: 'security', label: 'Sicherheit' },
    { id: 'privacy', label: 'Datenschutz' },
  ]

  return (
    <>
      <div className="profile-container">
        <div className="profile-content">
          <div className="profile-header">
            <h1>Mein Profil</h1>
            <button 
              className="btn-secondary"
              onClick={() => navigate('/')}
            >
              Zurück zur Startseite
            </button>
          </div>

          <div className="profile-tabs">
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

          <div className="profile-tab-content">
            {activeTab === 'profile' && (
              <ProfileTab showSuccess={showSuccess} showError={showError} />
            )}
            {activeTab === 'preferences' && (
              <PreferencesTab showSuccess={showSuccess} showError={showError} />
            )}
            {activeTab === 'notifications' && (
              <NotificationsTab showSuccess={showSuccess} showError={showError} />
            )}
            {activeTab === 'security' && (
              <SecurityTab showSuccess={showSuccess} showError={showError} />
            )}
            {activeTab === 'privacy' && (
              <PrivacyTab showSuccess={showSuccess} showError={showError} />
            )}
          </div>
        </div>
      </div>
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </>
  )
}

export default Profile
