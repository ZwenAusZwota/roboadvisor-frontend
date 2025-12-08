import { useState, useEffect } from 'react'
import api from '../services/api'

export const useUserSettings = () => {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getUserSettings()
      setSettings(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const updateSettings = async (updates) => {
    try {
      setError(null)
      // Optimistic update
      const previousSettings = { ...settings }
      if (settings) {
        setSettings({ ...settings, ...updates })
      }
      
      const updated = await api.updateUserSettings(updates)
      setSettings(updated)
      return { success: true }
    } catch (err) {
      // Revert on error
      if (previousSettings) {
        setSettings(previousSettings)
      }
      setError(err.message)
      return { success: false, error: err.message }
    }
  }

  return {
    settings,
    loading,
    error,
    updateSettings,
    refetch: fetchSettings,
  }
}

export const useUserProfile = () => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getUserProfile()
      setProfile(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  const updateProfile = async (updates) => {
    try {
      setError(null)
      // Optimistic update
      const previousProfile = { ...profile }
      if (profile) {
        setProfile({ ...profile, ...updates })
      }
      
      const updated = await api.updateUserProfile(updates)
      setProfile(updated)
      return { success: true }
    } catch (err) {
      // Revert on error
      if (previousProfile) {
        setProfile(previousProfile)
      }
      setError(err.message)
      return { success: false, error: err.message }
    }
  }

  return {
    profile,
    loading,
    error,
    updateProfile,
    refetch: fetchProfile,
  }
}

