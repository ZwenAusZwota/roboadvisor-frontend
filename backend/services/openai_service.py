"""
OpenAI Service für Portfolio-Analysen
Stellt Funktionen zum Aufrufen von OpenAI GPT-4 für Portfolio-Analysen bereit
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

# OpenAI Client initialisieren
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY nicht gesetzt. OpenAI-Funktionen werden nicht verfügbar sein.")

client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# Standard System Prompt für Portfolio-Analysen
SYSTEM_PROMPT = """Du bist ein Finanzanalyse-Assistent für ein Portfolio-Management-Tool. 
Analysiere das Portfolio des Benutzers und gib strukturiertes JSON im folgenden Schema zurück:

{
  "fundamentalAnalysis": [
    { "ticker": "", "summary": "", "valuation": "fair/undervalued/overvalued" }
  ],
  "technicalAnalysis": [
    { "ticker": "", "trend": "", "rsi": "", "signal": "" }
  ],
  "risks": [
    "Klumpenrisiko: ...",
    "Branchenübergewicht: ...",
    "Cash-Anteil: ..."
  ],
  "diversification": {
    "regionBreakdown": {},
    "sectorBreakdown": {},
    "positionWeights": {}
  },
  "cashAssessment": "",
  "suggestedRebalancing": "",
  "shortTermAdvice": "",
  "longTermAdvice": ""
}

Passe alle Empfehlungen an den Anlagehorizont und das Risikoprofil des Benutzers an.
Verwende klare, nicht-technische Sprache. Keine Disclaimer oder Finanzberatungswarnungen."""


def get_current_market_price(ticker: Optional[str], isin: Optional[str]) -> float:
    """
    Platzhalter-Funktion für aktuelle Marktpreise.
    In Produktion sollte hier eine echte Marktdaten-API integriert werden.
    
    Args:
        ticker: Ticker-Symbol
        isin: ISIN-Code
        
    Returns:
        Platzhalter-Preis (z.B. 10% über Kaufpreis)
    """
    # TODO: Integration mit echter Marktdaten-API (z.B. Alpha Vantage, Yahoo Finance, etc.)
    # Für jetzt: Platzhalter-Preis
    return 0.0


def build_portfolio_context(
    holdings: List[Dict],
    user_settings: Optional[Dict] = None
) -> str:
    """
    Erstellt einen Kontext-String aus Portfolio-Holdings für OpenAI
    
    Args:
        holdings: Liste von Portfolio-Positionen
        user_settings: Benutzereinstellungen (riskProfile, investmentHorizon)
        
    Returns:
        Formatierter Kontext-String
    """
    context_parts = ["Portfolio-Übersicht:\n"]
    
    total_value = 0.0
    positions = []
    
    for holding in holdings:
        ticker = holding.get('ticker', holding.get('isin', 'N/A'))
        name = holding.get('name', 'Unbekannt')
        quantity = float(holding.get('quantity', 0))
        purchase_price = float(holding.get('purchase_price', 0).replace(',', '.'))
        purchase_date = holding.get('purchase_date', '')
        sector = holding.get('sector', 'Unbekannt')
        region = holding.get('region', 'Unbekannt')
        asset_class = holding.get('asset_class', 'Unbekannt')
        
        # Platzhalter für aktuellen Preis (10% über Kaufpreis)
        current_price = purchase_price * 1.1
        position_value = quantity * current_price
        total_value += position_value
        
        positions.append({
            'ticker': ticker,
            'name': name,
            'quantity': quantity,
            'purchase_price': purchase_price,
            'current_price': current_price,
            'purchase_date': purchase_date,
            'sector': sector,
            'region': region,
            'asset_class': asset_class,
            'value': position_value
        })
    
    # Portfolio-Positionen auflisten
    for pos in positions:
        weight_pct = (pos['value'] / total_value * 100) if total_value > 0 else 0
        context_parts.append(
            f"- {pos['name']} ({pos['ticker']}): "
            f"{pos['quantity']} Stück @ {pos['purchase_price']:.2f} EUR "
            f"(aktuell ca. {pos['current_price']:.2f} EUR, {weight_pct:.1f}% des Portfolios), "
            f"Branche: {pos['sector']}, Region: {pos['region']}, "
            f"Assetklasse: {pos['asset_class']}, Kaufdatum: {pos['purchase_date']}"
        )
    
    context_parts.append(f"\nGesamtwert Portfolio: {total_value:.2f} EUR")
    
    # Diversifikation-Statistiken
    sectors = {}
    regions = {}
    asset_classes = {}
    
    for pos in positions:
        sector = pos['sector']
        region = pos['region']
        asset_class = pos['asset_class']
        
        sectors[sector] = sectors.get(sector, 0) + pos['value']
        regions[region] = regions.get(region, 0) + pos['value']
        asset_classes[asset_class] = asset_classes.get(asset_class, 0) + pos['value']
    
    context_parts.append("\nDiversifikation:")
    context_parts.append("Branchen: " + ", ".join([f"{k}: {v/total_value*100:.1f}%" for k, v in sectors.items()]))
    context_parts.append("Regionen: " + ", ".join([f"{k}: {v/total_value*100:.1f}%" for k, v in regions.items()]))
    context_parts.append("Assetklassen: " + ", ".join([f"{k}: {v/total_value*100:.1f}%" for k, v in asset_classes.items()]))
    
    # Benutzereinstellungen
    if user_settings:
        risk_profile = user_settings.get('riskProfile', 'Nicht angegeben')
        investment_horizon = user_settings.get('investmentHorizon', 'Nicht angegeben')
        context_parts.append(f"\nBenutzereinstellungen:")
        context_parts.append(f"Risikoprofil: {risk_profile}")
        context_parts.append(f"Anlagehorizont: {investment_horizon}")
    
    return "\n".join(context_parts)


async def analyze_portfolio(
    holdings: List[Dict],
    user_settings: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analysiert ein Portfolio mit OpenAI GPT-4
    
    Args:
        holdings: Liste von Portfolio-Positionen
        user_settings: Benutzereinstellungen (riskProfile, investmentHorizon)
        
    Returns:
        Strukturierte Analyse als Dictionary
        
    Raises:
        ValueError: Wenn OpenAI API Key nicht gesetzt ist
        Exception: Bei OpenAI API Fehlern
    """
    if not client:
        raise ValueError("OPENAI_API_KEY ist nicht gesetzt. Bitte konfigurieren Sie die OpenAI API.")
    
    if not holdings:
        raise ValueError("Portfolio ist leer. Bitte fügen Sie Positionen hinzu.")
    
    try:
        # Baue Kontext
        portfolio_context = build_portfolio_context(holdings, user_settings)
        
        # User Prompt
        user_prompt = f"""Analysiere das folgende Portfolio:

{portfolio_context}

Gib eine detaillierte Analyse im vorgegebenen JSON-Format zurück. 
Berücksichtige dabei:
- Fundamentale Bewertung jeder Position
- Technische Analyse (Trend, RSI, Signale)
- Risiken (Klumpenrisiko, Branchenkonzentration, Cash-Anteil)
- Diversifikation nach Regionen, Branchen und Gewichtungen
- Cash-Bewertung
- Vorschläge für Rebalancing
- Kurzfristige und langfristige Empfehlungen"""
        
        logger.info(f"Rufe OpenAI API auf für Portfolio mit {len(holdings)} Positionen")
        
        # OpenAI API Call
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Verwende gpt-4o-mini für Kostenoptimierung, kann auf gpt-4o geändert werden
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  # Erzwingt JSON-Output
        )
        
        # Parse Response
        content = response.choices[0].message.content
        logger.info(f"OpenAI Response erhalten: {len(content)} Zeichen")
        
        # Parse JSON
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der OpenAI Response: {e}")
            logger.error(f"Response Content: {content[:500]}")
            raise ValueError(f"OpenAI Response konnte nicht als JSON geparst werden: {e}")
        
        # Validierung und Normalisierung
        analysis = validate_and_normalize_analysis(analysis, holdings)
        
        logger.info("Portfolio-Analyse erfolgreich erstellt")
        return analysis
        
    except Exception as e:
        logger.error(f"Fehler bei OpenAI API Call: {e}")
        raise


def validate_and_normalize_analysis(analysis: Dict, holdings: List[Dict]) -> Dict:
    """
    Validiert und normalisiert die OpenAI-Analyse
    
    Args:
        analysis: Rohe Analyse von OpenAI
        holdings: Liste von Portfolio-Positionen
        
    Returns:
        Validierte und normalisierte Analyse
    """
    # Standard-Struktur
    normalized = {
        "fundamentalAnalysis": [],
        "technicalAnalysis": [],
        "risks": [],
        "diversification": {
            "regionBreakdown": {},
            "sectorBreakdown": {},
            "positionWeights": {}
        },
        "cashAssessment": "",
        "suggestedRebalancing": "",
        "shortTermAdvice": "",
        "longTermAdvice": ""
    }
    
    # Extrahiere verfügbare Ticker/ISINs
    tickers = []
    for holding in holdings:
        ticker = holding.get('ticker') or holding.get('isin') or holding.get('name', 'N/A')
        tickers.append(ticker)
    
    # Fundamental Analysis
    if "fundamentalAnalysis" in analysis and isinstance(analysis["fundamentalAnalysis"], list):
        normalized["fundamentalAnalysis"] = analysis["fundamentalAnalysis"]
    else:
        # Fallback: Erstelle für jede Position
        for ticker in tickers:
            normalized["fundamentalAnalysis"].append({
                "ticker": ticker,
                "summary": "Keine fundamentale Analyse verfügbar",
                "valuation": "fair"
            })
    
    # Technical Analysis
    if "technicalAnalysis" in analysis and isinstance(analysis["technicalAnalysis"], list):
        normalized["technicalAnalysis"] = analysis["technicalAnalysis"]
    else:
        # Fallback
        for ticker in tickers:
            normalized["technicalAnalysis"].append({
                "ticker": ticker,
                "trend": "neutral",
                "rsi": "N/A",
                "signal": "hold"
            })
    
    # Risks
    if "risks" in analysis and isinstance(analysis["risks"], list):
        normalized["risks"] = analysis["risks"]
    
    # Diversification
    if "diversification" in analysis and isinstance(analysis["diversification"], dict):
        div = analysis["diversification"]
        if "regionBreakdown" in div:
            normalized["diversification"]["regionBreakdown"] = div["regionBreakdown"]
        if "sectorBreakdown" in div:
            normalized["diversification"]["sectorBreakdown"] = div["sectorBreakdown"]
        if "positionWeights" in div:
            normalized["diversification"]["positionWeights"] = div["positionWeights"]
    
    # Textfelder
    normalized["cashAssessment"] = analysis.get("cashAssessment", "")
    normalized["suggestedRebalancing"] = analysis.get("suggestedRebalancing", "")
    normalized["shortTermAdvice"] = analysis.get("shortTermAdvice", "")
    normalized["longTermAdvice"] = analysis.get("longTermAdvice", "")
    
    return normalized

