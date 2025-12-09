"""
Portfolio Analysis Routes
Endpoints für AI-gestützte Portfolio-Analysen
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database import get_db
from models import User, PortfolioHolding, UserSettings, AnalysisHistory, AnalysisHistory
from auth import get_current_user
from services.openai_service import analyze_portfolio
from services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models für Request/Response
class PortfolioAnalysisRequest(BaseModel):
    portfolio_id: Optional[int] = None  # Optional: für zukünftige Multi-Portfolio Unterstützung
    force_refresh: bool = False  # Ignoriere Cache


class FundamentalAnalysisItem(BaseModel):
    ticker: str
    summary: str
    valuation: str  # fair, undervalued, overvalued


class TechnicalAnalysisItem(BaseModel):
    ticker: str
    trend: str
    rsi: str
    signal: str


class DiversificationData(BaseModel):
    regionBreakdown: Dict[str, float]
    sectorBreakdown: Dict[str, float]
    positionWeights: Dict[str, float]


class PortfolioAnalysisResponse(BaseModel):
    fundamentalAnalysis: List[FundamentalAnalysisItem]
    technicalAnalysis: List[TechnicalAnalysisItem]
    risks: List[str]
    diversification: DiversificationData
    cashAssessment: str
    suggestedRebalancing: str
    shortTermAdvice: str
    longTermAdvice: str
    cached: bool = False
    generated_at: str


# Rate Limiting: Einfache In-Memory Implementierung
# In Produktion sollte Redis oder ähnliches verwendet werden
rate_limit_store: Dict[int, List[datetime]] = {}
RATE_LIMIT_REQUESTS = 10  # Maximale Anzahl Requests
RATE_LIMIT_WINDOW_MINUTES = 60  # Zeitfenster in Minuten


def check_rate_limit(user_id: int) -> bool:
    """
    Prüft ob der Benutzer das Rate Limit überschritten hat
    
    Args:
        user_id: Benutzer-ID
        
    Returns:
        True wenn erlaubt, False wenn limitiert
    """
    now = datetime.utcnow()
    
    # Hole bisherige Requests des Users
    user_requests = rate_limit_store.get(user_id, [])
    
    # Entferne alte Requests außerhalb des Zeitfensters
    window_start = now.timestamp() - (RATE_LIMIT_WINDOW_MINUTES * 60)
    user_requests = [
        req for req in user_requests 
        if req.timestamp() > window_start
    ]
    
    # Prüfe Limit
    if len(user_requests) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate Limit erreicht für User {user_id}")
        return False
    
    # Füge aktuellen Request hinzu
    user_requests.append(now)
    rate_limit_store[user_id] = user_requests
    
    return True


@router.post("/api/portfolio/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio_endpoint(
    request: PortfolioAnalysisRequest = PortfolioAnalysisRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analysiert das Portfolio des Benutzers mit AI
    
    - Holt Portfolio-Positionen aus der Datenbank
    - Prüft Cache (12 Stunden TTL)
    - Ruft OpenAI API auf falls nötig
    - Gibt strukturierte Analyse zurück
    
    Rate Limit: 10 Requests pro Stunde pro Benutzer
    """
    try:
        # Rate Limiting prüfen
        if not check_rate_limit(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate Limit erreicht. Maximal {RATE_LIMIT_REQUESTS} Analysen pro Stunde erlaubt."
            )
        
        # Hole Portfolio-Positionen
        holdings_query = db.query(PortfolioHolding).filter(
            PortfolioHolding.userId == current_user.id
        )
        
        # Optional: Filter nach Portfolio-ID (für zukünftige Multi-Portfolio Unterstützung)
        if request.portfolio_id:
            # Hier könnte später nach portfolio_id gefiltert werden
            pass
        
        holdings = holdings_query.all()
        
        if not holdings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio ist leer. Bitte fügen Sie Positionen hinzu."
            )
        
        # Prüfe Cache (außer bei force_refresh)
        cached_analysis = None
        if not request.force_refresh:
            cached_analysis = cache_service.get(current_user.id, request.portfolio_id)
        
        if cached_analysis:
            logger.info(f"Cache Hit für User {current_user.id}")
            # Konvertiere zu Response Model
            return PortfolioAnalysisResponse(
                **cached_analysis,
                cached=True,
                generated_at=datetime.utcnow().isoformat()
            )
        
        # Hole Benutzereinstellungen für Kontext
        user_settings_obj = db.query(UserSettings).filter(
            UserSettings.userId == current_user.id
        ).first()
        
        user_settings = None
        if user_settings_obj:
            user_settings = {
                "riskProfile": user_settings_obj.riskProfile,
                "investmentHorizon": user_settings_obj.investmentHorizon
            }
        
        # Konvertiere Holdings zu Dict-Format für OpenAI Service
        holdings_dict = []
        for holding in holdings:
            holdings_dict.append({
                "id": holding.id,
                "isin": holding.isin,
                "ticker": holding.ticker,
                "name": holding.name,
                "quantity": float(holding.quantity) if holding.quantity else 0,
                "purchase_price": holding.purchase_price,
                "purchase_date": holding.purchase_date.isoformat() if holding.purchase_date else "",
                "sector": holding.sector,
                "region": holding.region,
                "asset_class": holding.asset_class
            })
        
        # Rufe OpenAI Service auf
        logger.info(f"Starte AI-Analyse für User {current_user.id} mit {len(holdings_dict)} Positionen")
        analysis = await analyze_portfolio(holdings_dict, user_settings)
        
        # Speichere Analyse-Historie für jede Portfolio-Position
        for holding in holdings:
            history_entry = AnalysisHistory(
                userId=current_user.id,
                portfolio_holding_id=holding.id,
                watchlist_item_id=None,
                asset_name=holding.name,
                asset_isin=holding.isin,
                asset_ticker=holding.ticker,
                analysis_data={
                    # Extrahiere relevante Analyse für diese Position
                    "fundamentalAnalysis": next(
                        (fa for fa in analysis.get("fundamentalAnalysis", []) 
                         if fa.get("ticker") == (holding.ticker or holding.isin or holding.name)),
                        None
                    ),
                    "technicalAnalysis": next(
                        (ta for ta in analysis.get("technicalAnalysis", [])
                         if ta.get("ticker") == (holding.ticker or holding.isin or holding.name)),
                        None
                    ),
                    "portfolioAnalysis": True,  # Marker für Portfolio-weite Analyse
                    "analysisDate": datetime.utcnow().isoformat()
                }
            )
            db.add(history_entry)
        
        db.commit()
        logger.info(f"Analyse-Historie für {len(holdings)} Positionen gespeichert")
        
        # Speichere im Cache
        cache_service.set(current_user.id, analysis, request.portfolio_id)
        
        # Füge Metadaten hinzu
        analysis["generated_at"] = datetime.utcnow().isoformat()
        analysis["cached"] = False
        
        # Validiere und konvertiere zu Response Model
        try:
            response = PortfolioAnalysisResponse(**analysis)
            return response
        except Exception as e:
            logger.error(f"Fehler beim Validieren der Analyse: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Fehler bei der Analyse-Validierung"
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Fehler bei Portfolio-Analyse: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei Portfolio-Analyse: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein Fehler ist bei der Portfolio-Analyse aufgetreten"
        )


@router.delete("/api/portfolio/analyze/cache")
async def clear_analysis_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Löscht den Cache für die Portfolio-Analyse des aktuellen Benutzers
    """
    cache_service.invalidate(current_user.id)
    return {"message": "Cache erfolgreich gelöscht"}



