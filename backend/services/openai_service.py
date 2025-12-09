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

# OpenAI Client - Lazy Initialization (wird erst beim ersten Aufruf erstellt)
_client = None
_openai_api_key = None


def get_openai_client():
    """
    Erstellt oder gibt den OpenAI Client zurück (Lazy Loading)
    """
    global _client, _openai_api_key
    
    if _client is not None:
        return _client
    
    # Unterstützt sowohl OPENAI_API_KEY als auch OPENAI_SECRET (für Flexibilität)
    _openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_SECRET")
    
    if not _openai_api_key:
        logger.warning("OPENAI_API_KEY oder OPENAI_SECRET nicht gesetzt. OpenAI-Funktionen werden nicht verfügbar sein.")
        return None
    
    try:
        # Initialisiere Client nur mit api_key, keine anderen Parameter
        # um Kompatibilitätsprobleme zu vermeiden
        _client = OpenAI(api_key=_openai_api_key)
        logger.info("OpenAI API Key gefunden, Client initialisiert")
        return _client
    except TypeError as e:
        # Spezielle Behandlung für TypeError - könnte auf Versionsinkompatibilität hindeuten
        logger.error(f"TypeError bei OpenAI Client-Initialisierung: {e}")
        logger.error("Dies könnte auf ein Problem mit der OpenAI-Bibliotheksversion hinweisen")
        try:
            import openai
            openai_version = getattr(openai, '__version__', 'Unknown')
            logger.error(f"OpenAI Bibliothek Version: {openai_version}")
            logger.error("Bitte prüfen Sie die OpenAI-Bibliotheksversion in requirements.txt")
        except:
            pass
        return None
    except Exception as e:
        logger.error(f"Fehler bei OpenAI Client-Initialisierung: {e}")
        logger.error(f"Fehlertyp: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Standard System Prompt für Portfolio-Analysen
PORTFOLIO_SYSTEM_PROMPT = """Du bist ein Finanzanalyse-Assistent für ein Portfolio-Management-Tool. 
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

# System Prompt für einzelne Asset-Analysen
SINGLE_ASSET_SYSTEM_PROMPT = """Du bist ein Finanzanalyse-Assistent für ein Portfolio-Management-Tool. 
Analysiere ein einzelnes Wertpapier/Asset und gib strukturiertes JSON im folgenden Schema zurück:

{
  "fundamentalAnalysis": {
    "summary": "",
    "valuation": "fair/undervalued/overvalued",
    "strengths": [],
    "weaknesses": [],
    "keyMetrics": {}
  },
  "technicalAnalysis": {
    "trend": "",
    "rsi": "",
    "signal": "buy/hold/sell",
    "supportLevel": "",
    "resistanceLevel": ""
  },
  "risks": [],
  "recommendation": "",
  "priceTarget": ""
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
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY oder OPENAI_SECRET ist nicht gesetzt. Bitte konfigurieren Sie die OpenAI API in den Environment Variables.")
    
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
        
        # OpenAI API Call (client wurde bereits oben initialisiert)
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Verwende gpt-4o-mini für Kostenoptimierung, kann auf gpt-4o geändert werden
            messages=[
                {"role": "system", "content": PORTFOLIO_SYSTEM_PROMPT},
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


async def analyze_single_asset(
    asset: Dict,
    user_settings: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analysiert ein einzelnes Asset (Wertpapier) mit OpenAI GPT-4
    
    Args:
        asset: Asset-Dictionary mit name, isin, ticker, etc.
        user_settings: Benutzereinstellungen (riskProfile, investmentHorizon)
        
    Returns:
        Strukturierte Analyse als Dictionary
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY oder OPENAI_SECRET ist nicht gesetzt. Bitte konfigurieren Sie die OpenAI API in den Environment Variables.")
    
    try:
        # Baue Asset-Kontext
        asset_context_parts = [
            f"Asset-Analyse für: {asset.get('name', 'Unbekannt')}",
            f"ISIN: {asset.get('isin', 'N/A')}",
            f"Ticker: {asset.get('ticker', 'N/A')}",
            f"Branche: {asset.get('sector', 'Unbekannt')}",
            f"Region: {asset.get('region', 'Unbekannt')}",
            f"Assetklasse: {asset.get('asset_class', 'Unbekannt')}"
        ]
        
        # Zusätzliche Infos für Portfolio-Holdings
        if 'purchase_price' in asset:
            asset_context_parts.append(f"Kaufpreis: {asset.get('purchase_price')} EUR")
            asset_context_parts.append(f"Anzahl: {asset.get('quantity', 0)}")
            asset_context_parts.append(f"Kaufdatum: {asset.get('purchase_date', 'N/A')}")
        
        asset_context = "\n".join(asset_context_parts)
        
        # Benutzereinstellungen
        if user_settings:
            risk_profile = user_settings.get('riskProfile', 'Nicht angegeben')
            investment_horizon = user_settings.get('investmentHorizon', 'Nicht angegeben')
            asset_context += f"\n\nBenutzereinstellungen:\nRisikoprofil: {risk_profile}\nAnlagehorizont: {investment_horizon}"
        
        # User Prompt
        user_prompt = f"""Analysiere das folgende Wertpapier:

{asset_context}

Gib eine detaillierte Analyse im vorgegebenen JSON-Format zurück.
Berücksichtige dabei:
- Fundamentale Bewertung (Stärken, Schwächen, Bewertung)
- Technische Analyse (Trend, RSI, Signale, Support/Resistance)
- Risiken
- Klare Kauf-/Verkauf-/Halte-Empfehlung
- Preisziel (falls möglich)"""
        
        logger.info(f"Rufe OpenAI API auf für Asset-Analyse: {asset.get('name')}")
        
        # OpenAI API Call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SINGLE_ASSET_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Parse Response
        content = response.choices[0].message.content
        logger.info(f"OpenAI Response erhalten für Asset-Analyse: {len(content)} Zeichen")
        
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der OpenAI Response: {e}")
            logger.error(f"Response Content: {content[:500]}")
            raise ValueError(f"OpenAI Response konnte nicht als JSON geparst werden: {e}")
        
        # Validierung und Normalisierung
        analysis = validate_and_normalize_single_asset_analysis(analysis, asset)
        
        logger.info("Asset-Analyse erfolgreich erstellt")
        return analysis
        
    except Exception as e:
        logger.error(f"Fehler bei OpenAI API Call für Asset-Analyse: {e}")
        raise


def validate_and_normalize_single_asset_analysis(analysis: Dict, asset: Dict) -> Dict:
    """
    Validiert und normalisiert die OpenAI-Analyse für ein einzelnes Asset
    
    Args:
        analysis: Rohe Analyse von OpenAI
        asset: Asset-Dictionary
        
    Returns:
        Validierte und normalisierte Analyse
    """
    normalized = {
        "fundamentalAnalysis": {
            "summary": "",
            "valuation": "fair",
            "strengths": [],
            "weaknesses": [],
            "keyMetrics": {}
        },
        "technicalAnalysis": {
            "trend": "neutral",
            "rsi": "N/A",
            "signal": "hold",
            "supportLevel": "",
            "resistanceLevel": ""
        },
        "risks": [],
        "recommendation": "",
        "priceTarget": None
    }
    
    # Fundamental Analysis
    if "fundamentalAnalysis" in analysis and isinstance(analysis["fundamentalAnalysis"], dict):
        fa = analysis["fundamentalAnalysis"]
        normalized["fundamentalAnalysis"] = {
            "summary": fa.get("summary", ""),
            "valuation": fa.get("valuation", "fair"),
            "strengths": fa.get("strengths", []) if isinstance(fa.get("strengths"), list) else [],
            "weaknesses": fa.get("weaknesses", []) if isinstance(fa.get("weaknesses"), list) else [],
            "keyMetrics": fa.get("keyMetrics", {}) if isinstance(fa.get("keyMetrics"), dict) else {}
        }
    
    # Technical Analysis
    if "technicalAnalysis" in analysis and isinstance(analysis["technicalAnalysis"], dict):
        ta = analysis["technicalAnalysis"]
        normalized["technicalAnalysis"] = {
            "trend": ta.get("trend", "neutral"),
            "rsi": str(ta.get("rsi", "N/A")),
            "signal": ta.get("signal", "hold"),
            "supportLevel": ta.get("supportLevel", ""),
            "resistanceLevel": ta.get("resistanceLevel", "")
        }
    
    # Risks
    if "risks" in analysis and isinstance(analysis["risks"], list):
        normalized["risks"] = analysis["risks"]
    
    # Recommendation & Price Target
    normalized["recommendation"] = analysis.get("recommendation", "")
    normalized["priceTarget"] = analysis.get("priceTarget")
    
    return normalized


def parse_percentage_string(value) -> float:
    """
    Konvertiert einen Prozent-String (z.B. "70%" oder "14.9%") zu einem float (z.B. 70.0 oder 14.9)
    
    Args:
        value: String mit Prozentzeichen oder bereits ein float/int
        
    Returns:
        Float-Wert (ohne Prozentzeichen)
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Entferne Prozentzeichen und Leerzeichen
        cleaned = value.replace("%", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            # Fallback: versuche nur Zahlen zu extrahieren
            import re
            numbers = re.findall(r'\d+\.?\d*', cleaned)
            if numbers:
                return float(numbers[0])
            return 0.0
    
    return 0.0


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
    
    # Diversification - konvertiere Prozent-Strings zu floats
    if "diversification" in analysis and isinstance(analysis["diversification"], dict):
        div = analysis["diversification"]
        
        # Region Breakdown - konvertiere Strings zu floats
        if "regionBreakdown" in div and isinstance(div["regionBreakdown"], dict):
            normalized["diversification"]["regionBreakdown"] = {
                key: parse_percentage_string(value)
                for key, value in div["regionBreakdown"].items()
            }
        
        # Sector Breakdown - konvertiere Strings zu floats
        if "sectorBreakdown" in div and isinstance(div["sectorBreakdown"], dict):
            normalized["diversification"]["sectorBreakdown"] = {
                key: parse_percentage_string(value)
                for key, value in div["sectorBreakdown"].items()
            }
        
        # Position Weights - konvertiere Strings zu floats
        if "positionWeights" in div and isinstance(div["positionWeights"], dict):
            normalized["diversification"]["positionWeights"] = {
                key: parse_percentage_string(value)
                for key, value in div["positionWeights"].items()
            }
    
    # Textfelder
    normalized["cashAssessment"] = analysis.get("cashAssessment", "")
    normalized["suggestedRebalancing"] = analysis.get("suggestedRebalancing", "")
    normalized["shortTermAdvice"] = analysis.get("shortTermAdvice", "")
    normalized["longTermAdvice"] = analysis.get("longTermAdvice", "")
    
    return normalized

