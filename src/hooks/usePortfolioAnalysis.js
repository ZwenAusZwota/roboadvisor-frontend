import { useState, useCallback } from 'react'
import api from '../services/api'

/**
 * Custom Hook für Portfolio-Analysen
 * 
 * Bietet Funktionen zum Abrufen von AI-gestützten Portfolio-Analysen
 * 
 * @returns {Object} { data, error, loading, runAnalysis, clearCache }
 */
export const usePortfolioAnalysis = () => {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  /**
   * Startet eine neue Portfolio-Analyse
   * 
   * @param {boolean} forceRefresh - Wenn true, ignoriert den Cache
   */
  const runAnalysis = useCallback(async (forceRefresh = false) => {
    try {
      setLoading(true)
      setError(null)
      
      const result = await api.analyzePortfolio(forceRefresh)
      setData(result)
      
      return result
    } catch (err) {
      setError(err.message || 'Fehler bei der Portfolio-Analyse')
      setData(null)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Löscht den Analyse-Cache
   */
  const clearCache = useCallback(async () => {
    try {
      await api.clearAnalysisCache()
      setData(null)
    } catch (err) {
      setError(err.message || 'Fehler beim Löschen des Caches')
      throw err
    }
  }, [])

  return {
    data,
    error,
    loading,
    runAnalysis,
    clearCache,
  }
}

