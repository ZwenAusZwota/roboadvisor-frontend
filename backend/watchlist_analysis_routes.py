"""
Watchlist Analysis Routes
Endpoints für AI-gestützte Watchlist-Analysen
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database import get_db
from models import User, WatchlistItem, UserSettings, AnalysisHistory
from auth import get_current_user
# analyze_single_asset wird unten definiert
from services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class WatchlistAnalysisRequest(BaseModel):
    item_id: Optional[int] = None  # Wenn None: analysiere alle Watchlist-Items
    force_refresh: bool = False

class WatchlistAnalysisResponse(BaseModel):
    item_id: int
    asset_name: str
    asset_isin: Optional[str]
    asset_ticker: Optional[str]
    fundamentalAnalysis: Optional[Dict[str, Any]]
    technicalAnalysis: Optional[Dict[str, Any]]
    analysis_date: str
    cached: bool = False


async def analyze_single_asset(asset: Dict, user_settings: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Analysiert ein einzelnes Asset (für Watchlist)
    
    Args:
        asset: Asset-Daten (name, isin, ticker, etc.)
        user_settings: Benutzereinstellungen
        
    Returns:
        Analyse für das einzelne Asset
    """
    import json
    from services.openai_service import get_openai_client, SYSTEM_PROMPT
    
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI Client konnte nicht initialisiert werden.")
    
    # Baue Kontext für einzelnes Asset
    asset_context = f"""Asset-Informationen:
- Name: {asset.get('name', 'Unbekannt')}
- ISIN: {asset.get('isin', 'N/A')}
- Ticker: {asset.get('ticker', 'N/A')}
- Branche: {asset.get('sector', 'Nicht angegeben')}
- Region: {asset.get('region', 'Nicht angegeben')}
- Assetklasse: {asset.get('asset_class', 'Nicht angegeben')}
"""
    
    user_prompt = f"""Analysiere das folgende Asset:

{asset_context}

Gib eine detaillierte Analyse zurück mit:
- Fundamentaler Bewertung (summary, valuation: fair/undervalued/overvalued)
- Technischer Analyse (trend, rsi, signal: buy/hold/sell)
- Kurzer Einschätzung der Investitionsattraktivität

Format (JSON):
{{
  "fundamentalAnalysis": {{
    "ticker": "{asset.get('ticker') or asset.get('isin') or asset.get('name')}",
    "summary": "...",
    "valuation": "fair"
  }},
  "technicalAnalysis": {{
    "ticker": "{asset.get('ticker') or asset.get('isin') or asset.get('name')}",
    "trend": "...",
    "rsi": "...",
    "signal": "buy/hold/sell"
  }}
}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        analysis = json.loads(content)
        
        return analysis
    except Exception as e:
        logger.error(f"Fehler bei OpenAI API Call für Asset-Analyse: {e}")
        raise


# POST /api/watchlist/analyze
@router.post("/api/watchlist/analyze", response_model=List[WatchlistAnalysisResponse])
async def analyze_watchlist(
    request: WatchlistAnalysisRequest = WatchlistAnalysisRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analysiert Watchlist-Einträge mit AI
    
    - Wenn item_id angegeben: Analysiere nur dieses Item
    - Wenn item_id None: Analysiere alle Watchlist-Items
    - Speichert Analyse in Historie
    """
    try:
        import json
        
        # Hole Watchlist-Items
        if request.item_id:
            items = db.query(WatchlistItem).filter(
                WatchlistItem.id == request.item_id,
                WatchlistItem.userId == current_user.id
            ).all()
        else:
            items = db.query(WatchlistItem).filter(
                WatchlistItem.userId == current_user.id
            ).all()
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keine Watchlist-Einträge gefunden."
            )
        
        # Hole Benutzereinstellungen
        user_settings_obj = db.query(UserSettings).filter(
            UserSettings.userId == current_user.id
        ).first()
        
        user_settings = None
        if user_settings_obj:
            user_settings = {
                "riskProfile": user_settings_obj.riskProfile,
                "investmentHorizon": user_settings_obj.investmentHorizon
            }
        
        results = []
        
        for item in items:
            # Prüfe Cache (für einzelnes Item)
            cached_analysis = None
            if not request.force_refresh:
                # Verwende item.id als portfolio_id-Parameter für eindeutigen Cache-Key
                cached_analysis = cache_service.get(current_user.id, portfolio_id=item.id, cache_type="watchlist")
            
            if cached_analysis:
                logger.info(f"Cache Hit für Watchlist-Item {item.id}")
                results.append(WatchlistAnalysisResponse(
                    item_id=item.id,
                    asset_name=item.name,
                    asset_isin=item.isin,
                    asset_ticker=item.ticker,
                    fundamentalAnalysis=cached_analysis.get("fundamentalAnalysis"),
                    technicalAnalysis=cached_analysis.get("technicalAnalysis"),
                    analysis_date=cached_analysis.get("analysisDate", datetime.utcnow().isoformat()),
                    cached=True
                ))
                continue
            
            # Konvertiere Item zu Dict
            asset_dict = {
                "name": item.name,
                "isin": item.isin,
                "ticker": item.ticker,
                "sector": item.sector,
                "region": item.region,
                "asset_class": item.asset_class
            }
            
            # Rufe OpenAI Service auf
            logger.info(f"Starte AI-Analyse für Watchlist-Item {item.id}: {item.name}")
            try:
                analysis = await analyze_single_asset(asset_dict, user_settings)
            except Exception as e:
                logger.error(f"Fehler bei OpenAI-Analyse für Item {item.id}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Fehler bei der KI-Analyse für {item.name}: {str(e)}"
                )
            
            # Speichere in Historie
            history_entry = AnalysisHistory(
                userId=current_user.id,
                portfolio_holding_id=None,
                watchlist_item_id=item.id,
                asset_name=item.name,
                asset_isin=item.isin,
                asset_ticker=item.ticker,
                analysis_data={
                    "fundamentalAnalysis": analysis.get("fundamentalAnalysis"),
                    "technicalAnalysis": analysis.get("technicalAnalysis"),
                    "watchlistAnalysis": True,
                    "analysisDate": datetime.utcnow().isoformat()
                }
            )
            db.add(history_entry)
            
            # Cache setzen für dieses Item
            cache_data = {
                "fundamentalAnalysis": analysis.get("fundamentalAnalysis"),
                "technicalAnalysis": analysis.get("technicalAnalysis"),
                "analysisDate": datetime.utcnow().isoformat()
            }
            cache_service.set(current_user.id, cache_data, portfolio_id=item.id, cache_type="watchlist")
            logger.info(f"Cache gespeichert für Watchlist-Item {item.id}")
            
            results.append(WatchlistAnalysisResponse(
                item_id=item.id,
                asset_name=item.name,
                asset_isin=item.isin,
                asset_ticker=item.ticker,
                fundamentalAnalysis=analysis.get("fundamentalAnalysis"),
                technicalAnalysis=analysis.get("technicalAnalysis"),
                analysis_date=datetime.utcnow().isoformat(),
                cached=False
            ))
        
        db.commit()
        logger.info(f"Analyse-Historie für {len(items)} Watchlist-Items gespeichert")
        
        return results
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Fehler bei Watchlist-Analyse: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei Watchlist-Analyse: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein Fehler ist bei der Watchlist-Analyse aufgetreten"
        )

