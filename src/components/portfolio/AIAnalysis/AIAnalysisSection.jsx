import React from 'react'
import { usePortfolioAnalysis } from '../../../hooks/usePortfolioAnalysis'
import { useToast } from '../../../hooks/useToast'
import AIAnalysisOverview from './AIAnalysisOverview'
import AISinglePositionAnalysis from './AISinglePositionAnalysis'
import AIRiskOverview from './AIRiskOverview'
import AIRebalancingSuggestions from './AIRebalancingSuggestions'
import AIAdviceShortLong from './AIAdviceShortLong'
import './AIAnalysis.css'

/**
 * Hauptkomponente für AI-Analyse
 * Integriert alle Analyse-Komponenten und stellt die Benutzeroberfläche bereit
 */
const AIAnalysisSection = () => {
  const { data, error, loading, runAnalysis } = usePortfolioAnalysis()
  const { showError, showSuccess } = useToast()

  const handleAnalyze = async () => {
    try {
      await runAnalysis(false)
      showSuccess('Portfolio-Analyse erfolgreich erstellt')
    } catch (err) {
      showError(err.message || 'Fehler bei der Portfolio-Analyse')
    }
  }

  const handleForceRefresh = async () => {
    try {
      await runAnalysis(true)
      showSuccess('Portfolio-Analyse aktualisiert')
    } catch (err) {
      showError(err.message || 'Fehler bei der Portfolio-Analyse')
    }
  }

  return (
    <div className="ai-analysis-container">
      <div className="ai-analysis-header">
        <h2>KI-Analyse</h2>
        <div className="header-actions">
          {data && (
            <button
              className="analyze-button"
              onClick={handleForceRefresh}
              disabled={loading}
            >
              Aktualisieren
            </button>
          )}
          <button
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? 'Analysiere...' : data ? 'Neu analysieren' : 'Analyse starten'}
          </button>
        </div>
      </div>

      {error && (
        <div className="ai-analysis-error">
          <strong>Fehler:</strong> {error}
        </div>
      )}

      {loading && !data && (
        <div className="ai-analysis-loading">
          Analysiere Ihr Portfolio...
        </div>
      )}

      {!loading && !data && !error && (
        <div className="ai-analysis-empty">
          <p>Klicken Sie auf "Analyse starten", um eine KI-gestützte Analyse Ihres Portfolios zu erhalten.</p>
        </div>
      )}

      {data && !loading && (
        <div className="ai-analysis-content">
          <AIAnalysisOverview analysis={data} />
          
          <AISinglePositionAnalysis
            fundamentalAnalysis={data.fundamentalAnalysis}
            technicalAnalysis={data.technicalAnalysis}
          />
          
          <AIRiskOverview
            risks={data.risks}
            cashAssessment={data.cashAssessment}
          />
          
          <AIRebalancingSuggestions
            diversification={data.diversification}
            suggestedRebalancing={data.suggestedRebalancing}
          />
          
          <AIAdviceShortLong
            shortTermAdvice={data.shortTermAdvice}
            longTermAdvice={data.longTermAdvice}
          />
        </div>
      )}
    </div>
  )
}

export default AIAnalysisSection

