"""
Analysis History Routes
Endpoints für Bewertungshistorie
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import User, AnalysisHistory, PortfolioHolding, WatchlistItem
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class AnalysisHistoryResponse(BaseModel):
    id: int
    portfolio_holding_id: Optional[int]
    watchlist_item_id: Optional[int]
    asset_name: str
    asset_isin: Optional[str]
    asset_ticker: Optional[str]
    analysis_data: Dict[str, Any]
    created_at: str
    
    class Config:
        from_attributes = True

class AnalysisHistorySummary(BaseModel):
    asset_name: str
    asset_isin: Optional[str]
    asset_ticker: Optional[str]
    total_analyses: int
    latest_analysis_date: str
    latest_analysis: Optional[Dict[str, Any]]

# GET /api/analysis-history/portfolio/{holding_id}
@router.get("/api/analysis-history/portfolio/{holding_id}", response_model=List[AnalysisHistoryResponse])
async def get_portfolio_holding_history(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hole Bewertungshistorie für eine Portfolio-Position
    """
    # Prüfe ob Portfolio-Holding existiert und dem User gehört
    holding = db.query(PortfolioHolding).filter(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.userId == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio-Position nicht gefunden"
        )
    
    # Hole Historie
    history = db.query(AnalysisHistory).filter(
        AnalysisHistory.userId == current_user.id,
        AnalysisHistory.portfolio_holding_id == holding_id
    ).order_by(AnalysisHistory.created_at.desc()).all()
    
    return [
        AnalysisHistoryResponse(
            id=h.id,
            portfolio_holding_id=h.portfolio_holding_id,
            watchlist_item_id=h.watchlist_item_id,
            asset_name=h.asset_name,
            asset_isin=h.asset_isin,
            asset_ticker=h.asset_ticker,
            analysis_data=h.analysis_data,
            created_at=h.created_at.isoformat()
        )
        for h in history
    ]

# GET /api/analysis-history/watchlist/{item_id}
@router.get("/api/analysis-history/watchlist/{item_id}", response_model=List[AnalysisHistoryResponse])
async def get_watchlist_item_history(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hole Bewertungshistorie für einen Watchlist-Eintrag
    """
    # Prüfe ob Watchlist-Item existiert und dem User gehört
    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.userId == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist-Eintrag nicht gefunden"
        )
    
    # Hole Historie
    history = db.query(AnalysisHistory).filter(
        AnalysisHistory.userId == current_user.id,
        AnalysisHistory.watchlist_item_id == item_id
    ).order_by(AnalysisHistory.created_at.desc()).all()
    
    return [
        AnalysisHistoryResponse(
            id=h.id,
            portfolio_holding_id=h.portfolio_holding_id,
            watchlist_item_id=h.watchlist_item_id,
            asset_name=h.asset_name,
            asset_isin=h.asset_isin,
            asset_ticker=h.asset_ticker,
            analysis_data=h.analysis_data,
            created_at=h.created_at.isoformat()
        )
        for h in history
    ]

# GET /api/analysis-history/asset
@router.get("/api/analysis-history/asset", response_model=List[AnalysisHistoryResponse])
async def get_asset_history(
    isin: Optional[str] = None,
    ticker: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hole Bewertungshistorie für ein Asset (nach ISIN oder Ticker)
    Funktioniert sowohl für Portfolio als auch Watchlist
    """
    if not isin and not ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISIN oder Ticker muss angegeben werden"
        )
    
    query = db.query(AnalysisHistory).filter(
        AnalysisHistory.userId == current_user.id
    )
    
    if isin:
        query = query.filter(AnalysisHistory.asset_isin == isin.upper())
    if ticker:
        query = query.filter(AnalysisHistory.asset_ticker == ticker.upper())
    
    history = query.order_by(AnalysisHistory.created_at.desc()).all()
    
    return [
        AnalysisHistoryResponse(
            id=h.id,
            portfolio_holding_id=h.portfolio_holding_id,
            watchlist_item_id=h.watchlist_item_id,
            asset_name=h.asset_name,
            asset_isin=h.asset_isin,
            asset_ticker=h.asset_ticker,
            analysis_data=h.analysis_data,
            created_at=h.created_at.isoformat()
        )
        for h in history
    ]

# GET /api/analysis-history/summary
@router.get("/api/analysis-history/summary", response_model=List[AnalysisHistorySummary])
async def get_analysis_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hole Zusammenfassung aller analysierten Assets
    """
    # Hole alle eindeutigen Assets mit ihrer letzten Analyse
    from sqlalchemy import func
    
    # Gruppiere nach Asset (ISIN oder Ticker)
    subquery = db.query(
        AnalysisHistory.asset_name,
        AnalysisHistory.asset_isin,
        AnalysisHistory.asset_ticker,
        func.max(AnalysisHistory.created_at).label('latest_date'),
        func.count(AnalysisHistory.id).label('count')
    ).filter(
        AnalysisHistory.userId == current_user.id
    ).group_by(
        AnalysisHistory.asset_name,
        AnalysisHistory.asset_isin,
        AnalysisHistory.asset_ticker
    ).subquery()
    
    # Hole Details der letzten Analyse
    results = []
    for row in db.query(subquery).all():
        latest = db.query(AnalysisHistory).filter(
            AnalysisHistory.userId == current_user.id,
            AnalysisHistory.asset_isin == row.asset_isin,
            AnalysisHistory.asset_ticker == row.asset_ticker,
            AnalysisHistory.created_at == row.latest_date
        ).first()
        
        results.append(AnalysisHistorySummary(
            asset_name=row.asset_name,
            asset_isin=row.asset_isin,
            asset_ticker=row.asset_ticker,
            total_analyses=row.count,
            latest_analysis_date=row.latest_date.isoformat(),
            latest_analysis=latest.analysis_data if latest else None
        ))
    
    return results

