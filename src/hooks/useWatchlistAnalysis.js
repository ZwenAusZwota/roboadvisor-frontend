import { useState, useCallback } from 'react'
import api from '../services/api'

/**
 * Custom Hook für Watchlist-Analysen
 */
export const useWatchlistAnalysis = () => {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const runAnalysis = useCallback(async (itemId = null, forceRefresh = false) => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await api.analyzeWatchlist(itemId, forceRefresh)
      setData(result)
      
      return result
    } catch (err) {
      setError(err.message || 'Fehler bei der Watchlist-Analyse')
      setData(null)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    data,
    error,
    loading,
    runAnalysis,
  }
}

