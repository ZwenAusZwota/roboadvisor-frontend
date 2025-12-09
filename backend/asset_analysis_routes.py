"""
Asset Analysis Routes
Endpoints für AI-Analysen einzelner Assets (Portfolio-Holdings oder Watchlist-Items)
mit Historie-Speicherung
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database import get_db
from models import User, PortfolioHolding, WatchlistItem, AnalysisHistory
from auth import get_current_user
from services.openai_service import analyze_single_asset
from services.cache_service import cache_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class SingleAssetAnalysisRequest(BaseModel):
    asset_type: str  # "portfolio" oder "watchlist"
    asset_id: int
    force_refresh: bool = False


class SingleAssetAnalysisResponse(BaseModel):
    fundamentalAnalysis: Dict[str, Any]
    technicalAnalysis: Dict[str, Any]
    risks: List[str]
    recommendation: str
    priceTarget: Optional[str] = None
    cached: bool = False
    generated_at: str


class AnalysisHistoryItem(BaseModel):
    id: int
    asset_name: str
    asset_isin: Optional[str]
    asset_ticker: Optional[str]
    analysis_data: Dict[str, Any]
    created_at: str
    
    class Config:
        from_attributes = True


# Rate Limiting für Asset-Analysen
rate_limit_store_asset: Dict[int, List[datetime]] = {}
RATE_LIMIT_ASSET_REQUESTS = 20  # Mehr als Portfolio-Analyse, da einzelne Assets
RATE_LIMIT_ASSET_WINDOW_MINUTES = 60


def check_asset_rate_limit(user_id: int) -> bool:
    """Prüft Rate Limit für Asset-Analysen"""
    now = datetime.utcnow()
    user_requests = rate_limit_store_asset.get(user_id, [])
    window_start = now.timestamp() - (RATE_LIMIT_ASSET_WINDOW_MINUTES * 60)
    user_requests = [
        req for req in user_requests 
        if req.timestamp() > window_start
    ]
    
    if len(user_requests) >= RATE_LIMIT_ASSET_REQUESTS:
        logger.warning(f"Asset Rate Limit erreicht für User {user_id}")
        return False
    
    user_requests.append(now)
    rate_limit_store_asset[user_id] = user_requests
    return True


@router.post("/api/asset/analyze", response_model=SingleAssetAnalysisResponse)
async def analyze_single_asset_endpoint(
    request: SingleAssetAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analysiert ein einzelnes Asset (Portfolio-Holding oder Watchlist-Item) mit AI
    und speichert die Analyse in der Historie
    """
    try:
        # Rate Limiting prüfen
        if not check_asset_rate_limit(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate Limit erreicht. Maximal {RATE_LIMIT_ASSET_REQUESTS} Asset-Analysen pro Stunde erlaubt."
            )
        
        # Hole Asset je nach Typ
        asset = None
        asset_type_str = ""
        
        if request.asset_type == "portfolio":
            asset = db.query(PortfolioHolding).filter(
                PortfolioHolding.id == request.asset_id,
                PortfolioHolding.userId == current_user.id
            ).first()
            asset_type_str = "Portfolio-Holding"
        elif request.asset_type == "watchlist":
            asset = db.query(WatchlistItem).filter(
                WatchlistItem.id == request.asset_id,
                WatchlistItem.userId == current_user.id
            ).first()
            asset_type_str = "Watchlist-Item"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="asset_type muss 'portfolio' oder 'watchlist' sein"
            )
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{asset_type_str} nicht gefunden"
            )
        
        # Prüfe Cache (vereinfacht - für Asset-Analysen verwenden wir kurzen Cache)
        # TODO: Erweitere Cache-Service für Asset-spezifische Keys
        cached_analysis = None
        if not request.force_refresh:
            # Für jetzt: Kein Cache für einzelne Assets (kann später erweitert werden)
            pass
        
        # Hole Benutzereinstellungen für Kontext
        from models import UserSettings
        user_settings_obj = db.query(UserSettings).filter(
            UserSettings.userId == current_user.id
        ).first()
        
        user_settings = None
        if user_settings_obj:
            user_settings = {
                "riskProfile": user_settings_obj.riskProfile,
                "investmentHorizon": user_settings_obj.investmentHorizon
            }
        
        # Baue Asset-Dict für OpenAI Service
        asset_dict = {
            "name": asset.name,
            "isin": asset.isin,
            "ticker": asset.ticker,
            "sector": asset.sector,
            "region": asset.region,
            "asset_class": asset.asset_class
        }
        
        # Für Portfolio-Holdings: zusätzliche Infos
        if isinstance(asset, PortfolioHolding):
            asset_dict.update({
                "quantity": float(asset.quantity) if asset.quantity else 0,
                "purchase_price": asset.purchase_price,
                "purchase_date": asset.purchase_date.isoformat() if asset.purchase_date else ""
            })
        
        # Rufe OpenAI Service auf
        logger.info(f"Starte AI-Analyse für {asset_type_str} {request.asset_id}")
        analysis = await analyze_single_asset(asset_dict, user_settings)
        
        # Speichere in Historie
        history_entry = AnalysisHistory(
            userId=current_user.id,
            portfolio_holding_id=request.asset_id if request.asset_type == "portfolio" else None,
            watchlist_item_id=request.asset_id if request.asset_type == "watchlist" else None,
            asset_name=asset.name,
            asset_isin=asset.isin,
            asset_ticker=asset.ticker,
            analysis_data=analysis
        )
        db.add(history_entry)
        db.commit()
        
        # Cache wird für einzelne Assets nicht verwendet (jede Analyse wird gespeichert)
        
        analysis["generated_at"] = datetime.utcnow().isoformat()
        
        return SingleAssetAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Fehler bei Asset-Analyse: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei Asset-Analyse: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ein Fehler ist bei der Asset-Analyse aufgetreten"
        )


@router.get("/api/asset/analysis-history/{asset_type}/{asset_id}", response_model=List[AnalysisHistoryItem])
async def get_analysis_history(
    asset_type: str,
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hole die Analyse-Historie für ein Asset (Portfolio-Holding oder Watchlist-Item)
    """
    try:
        # Validiere Asset-Type
        if asset_type not in ["portfolio", "watchlist"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="asset_type muss 'portfolio' oder 'watchlist' sein"
            )
        
        # Prüfe ob Asset existiert und dem User gehört
        asset = None
        if asset_type == "portfolio":
            asset = db.query(PortfolioHolding).filter(
                PortfolioHolding.id == asset_id,
                PortfolioHolding.userId == current_user.id
            ).first()
        else:
            asset = db.query(WatchlistItem).filter(
                WatchlistItem.id == asset_id,
                WatchlistItem.userId == current_user.id
            ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset nicht gefunden"
            )
        
        # Hole Historie
        query = db.query(AnalysisHistory).filter(
            AnalysisHistory.userId == current_user.id
        )
        
        if asset_type == "portfolio":
            query = query.filter(AnalysisHistory.portfolio_holding_id == asset_id)
        else:
            query = query.filter(AnalysisHistory.watchlist_item_id == asset_id)
        
        history = query.order_by(AnalysisHistory.created_at.desc()).limit(50).all()
        
        return [
            AnalysisHistoryItem(
                id=entry.id,
                asset_name=entry.asset_name,
                asset_isin=entry.asset_isin,
                asset_ticker=entry.asset_ticker,
                analysis_data=entry.analysis_data,
                created_at=entry.created_at.isoformat()
            )
            for entry in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Analyse-Historie: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Abrufen der Analyse-Historie"
        )

