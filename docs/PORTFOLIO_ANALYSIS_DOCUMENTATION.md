# Portfolio-Analyse System - Dokumentation

## Übersicht

Das Portfolio-Analyse-System nutzt OpenAI GPT-4, um umfassende, strukturierte Analysen von Benutzer-Portfolios zu erstellen. Es bietet fundamentale und technische Analysen, Risikobewertungen, Diversifikations-Insights und Rebalancing-Empfehlungen.

## Architektur

### Backend

#### Komponenten

1. **OpenAI Service** (`backend/services/openai_service.py`)
   - Zuständig für OpenAI API Calls
   - Portfolio-Kontext-Building
   - Response-Validierung und Normalisierung

2. **Cache Service** (`backend/services/cache_service.py`)
   - In-Memory Cache mit 12 Stunden TTL
   - Reduziert Token-Usage durch Caching
   - In Produktion sollte Redis verwendet werden

3. **Portfolio Analysis Routes** (`backend/portfolio_analysis_routes.py`)
   - POST `/api/portfolio/analyze` - Startet Analyse
   - DELETE `/api/portfolio/analyze/cache` - Löscht Cache
   - Rate Limiting: 10 Requests pro Stunde pro Benutzer

#### API Endpoints

##### POST `/api/portfolio/analyze`

Startet eine Portfolio-Analyse.

**Request:**
```json
{
  "portfolio_id": null,  // Optional, für Multi-Portfolio
  "force_refresh": false // Ignoriert Cache wenn true
}
```

**Response:**
Siehe `docs/PORTFOLIO_ANALYSIS_API_EXAMPLE.json` für vollständiges Beispiel.

**Fehler:**
- `400`: Portfolio ist leer
- `429`: Rate Limit erreicht
- `500`: OpenAI API Fehler

##### DELETE `/api/portfolio/analyze/cache`

Löscht den Cache für den aktuellen Benutzer.

**Response:**
```json
{
  "message": "Cache erfolgreich gelöscht"
}
```

### Frontend

#### Komponenten

1. **Hook: `usePortfolioAnalysis`**
   - Verwaltet Analyse-State
   - `runAnalysis(forceRefresh)` - Startet Analyse
   - `clearCache()` - Löscht Cache

2. **Hauptkomponente: `AIAnalysisSection`**
   - Integriert alle Sub-Komponenten
   - Button "Analyse starten"
   - Loading/Error States

3. **Sub-Komponenten:**
   - `AIAnalysisOverview` - Übersicht
   - `AISinglePositionAnalysis` - Einzelne Positionen
   - `AIRiskOverview` - Risiken
   - `AIRebalancingSuggestions` - Rebalancing
   - `AIAdviceShortLong` - Kurz- und langfristige Empfehlungen

## Konfiguration

### Environment Variables

**Backend:**
- `OPENAI_API_KEY` (erforderlich) - OpenAI API Key

**Frontend:**
- Keine zusätzlichen Variablen nötig

### OpenAI Model

Standard: `gpt-4o-mini` (kostenoptimiert)
- Kann in `backend/services/openai_service.py` auf `gpt-4o` geändert werden
- `response_format: "json_object"` erzwingt JSON-Output

## Erweiterung

### Neue Analyse-Typen hinzufügen

1. **Backend:**
   - Erweitern Sie `SYSTEM_PROMPT` in `openai_service.py`
   - Fügen Sie neue Felder zum JSON-Schema hinzu
   - Erweitern Sie `validate_and_normalize_analysis()`

2. **Frontend:**
   - Erstellen Sie neue Komponente in `src/components/portfolio/AIAnalysis/`
   - Integrieren Sie in `AIAnalysisSection.jsx`
   - Erweitern Sie TypeScript-Typen (falls verwendet)

### Beispiel: Neue Analyse-Kategorie "ESG-Score"

```python
# backend/services/openai_service.py
SYSTEM_PROMPT = """
...
{
  ...
  "esgScores": [
    { "ticker": "", "environment": 85, "social": 80, "governance": 90 }
  ]
}
...
"""
```

```jsx
// Frontend: Neue Komponente
const AIESGAnalysis = ({ esgScores }) => {
  // Rendering-Logik
}
```

### Integration echter Marktdaten

Aktuell verwendet das System Platzhalter-Preise. Für echte Integration:

1. Implementieren Sie `get_current_market_price()` in `openai_service.py`
2. Integrieren Sie Marktdaten-API (z.B. Alpha Vantage, Yahoo Finance)
3. Aktualisieren Sie `build_portfolio_context()` für echte Preise

## Tests

### Backend Tests

```bash
cd backend
pytest tests/test_portfolio_analysis.py -v
```

### Frontend Tests

```bash
# Unit Tests für Hook
npm test usePortfolioAnalysis

# Component Tests
npm test AIAnalysisSection
```

## Rate Limiting

- **Limit:** 10 Requests pro Stunde pro Benutzer
- **Implementierung:** In-Memory in `portfolio_analysis_routes.py`
- **Produktion:** Sollte auf Redis-basiertes Rate Limiting migriert werden

## Caching

- **TTL:** 12 Stunden
- **Strategie:** In-Memory Cache
- **Produktion:** Redis empfohlen für:
  - Persistenz
  - Shared Cache über Instanzen
  - Erweiterte Features (TTL, Invalidation)

### Cache-Invalidierung

Der Cache wird automatisch invalidiert nach:
- 12 Stunden (TTL)
- Explizite Löschung über DELETE Endpoint
- Force Refresh Request

## Fehlerbehandlung

### Backend

- OpenAI API Fehler werden abgefangen und als 500 zurückgegeben
- Rate Limit Fehler: 429 Status Code
- Validierungsfehler: 400 Status Code mit detaillierter Meldung

### Frontend

- Fehler werden über Toast-Notifications angezeigt
- Retry-Logic kann in `usePortfolioAnalysis` hinzugefügt werden
- Fallback-UI bei fehlenden Daten

## Performance

### Optimierungen

1. **Caching:** Reduziert API Calls erheblich
2. **Model:** `gpt-4o-mini` ist schneller und günstiger als `gpt-4o`
3. **Rate Limiting:** Verhindert Missbrauch und Kosten-Explosion

### Monitoring

Empfohlene Metriken:
- Anzahl API Calls pro Tag
- Cache Hit Rate
- Durchschnittliche Response-Zeit
- OpenAI Token Usage

## Sicherheit

- Authentifizierung erforderlich (JWT Token)
- Rate Limiting verhindert Missbrauch
- Keine sensiblen Daten im Cache (nur Analyse-Ergebnisse)
- OpenAI API Key nur im Backend (nie im Frontend)

## Kosten

- **OpenAI gpt-4o-mini:** ~$0.15 pro 1M Input Tokens, ~$0.60 pro 1M Output Tokens
- **Durchschnittliche Analyse:** ~2000 Input Tokens, ~1000 Output Tokens
- **Kosten pro Analyse:** ~$0.001-0.002
- **Mit Caching:** Kosten reduzieren sich erheblich bei wiederholten Analysen

## Bekannte Einschränkungen

1. **Platzhalter-Preise:** Aktuelle Marktpreise müssen extern integriert werden
2. **In-Memory Cache:** Nicht persistent, geht bei Neustart verloren
3. **Rate Limiting:** Einfache Implementierung, nicht für Multi-Instance geeignet
4. **Keine historischen Analysen:** Analysen werden nicht in Datenbank gespeichert

## Zukünftige Verbesserungen

- [ ] Integration echter Marktdaten-APIs
- [ ] Redis-basiertes Caching
- [ ] Speicherung historischer Analysen in Datenbank
- [ ] Vergleich mehrerer Analysen über Zeit
- [ ] PDF-Export der Analysen
- [ ] E-Mail-Versand bei neuen Analysen
- [ ] Backtesting von Empfehlungen

