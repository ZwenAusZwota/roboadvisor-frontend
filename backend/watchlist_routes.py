"""
Watchlist Routes
Endpoints für Watchlist-Verwaltung
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import get_db
from models import User, WatchlistItem
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class WatchlistItemCreate(BaseModel):
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: str
    sector: Optional[str] = None
    region: Optional[str] = None
    asset_class: Optional[str] = None
    notes: Optional[str] = None

class WatchlistItemUpdate(BaseModel):
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    region: Optional[str] = None
    asset_class: Optional[str] = None
    notes: Optional[str] = None

class WatchlistItemResponse(BaseModel):
    id: int
    isin: Optional[str]
    ticker: Optional[str]
    name: str
    sector: Optional[str]
    region: Optional[str]
    asset_class: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

# Helper function to validate ISIN
def validate_isin(isin: str) -> bool:
    """Validiert ISIN-Format (12 Zeichen, alphanumerisch)"""
    if not isin:
        return False
    if len(isin) != 12:
        return False
    return isin.isalnum()

# GET /api/watchlist
@router.get("/api/watchlist", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole alle Watchlist-Einträge des aktuellen Nutzers"""
    items = db.query(WatchlistItem).filter(
        WatchlistItem.userId == current_user.id
    ).order_by(WatchlistItem.created_at.desc()).all()
    
    return [
        WatchlistItemResponse(
            id=item.id,
            isin=item.isin,
            ticker=item.ticker,
            name=item.name,
            sector=item.sector,
            region=item.region,
            asset_class=item.asset_class,
            notes=item.notes,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat()
        )
        for item in items
    ]

# GET /api/watchlist/{id}
@router.get("/api/watchlist/{item_id}", response_model=WatchlistItemResponse)
async def get_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole einen spezifischen Watchlist-Eintrag"""
    item = db.query(WatchlistItem).filter(
        WatchlistItem.id == item_id,
        WatchlistItem.userId == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist-Eintrag nicht gefunden"
        )
    
    return WatchlistItemResponse(
        id=item.id,
        isin=item.isin,
        ticker=item.ticker,
        name=item.name,
        sector=item.sector,
        region=item.region,
        asset_class=item.asset_class,
        notes=item.notes,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat()
    )

# POST /api/watchlist
@router.post("/api/watchlist", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist_item(
    item: WatchlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Erstelle einen neuen Watchlist-Eintrag"""
    try:
        # Normalisiere leere Strings zu None
        isin = item.isin.strip().upper() if item.isin and item.isin.strip() else None
        ticker = item.ticker.strip().upper() if item.ticker and item.ticker.strip() else None
        name = item.name.strip() if item.name else None
        
        # Validierung
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name ist erforderlich"
            )
        
        if not isin and not ticker:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISIN oder Ticker muss angegeben werden"
            )
        
        if isin and not validate_isin(isin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ungültiges ISIN-Format: '{isin}'. ISIN muss genau 12 Zeichen alphanumerisch sein"
            )
        
        # Erstelle neuen Eintrag
        new_item = WatchlistItem(
            userId=current_user.id,
            isin=isin,
            ticker=ticker,
            name=name,
            sector=item.sector,
            region=item.region,
            asset_class=item.asset_class,
            notes=item.notes
        )
        
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        logger.info(f"Watchlist item created for user {current_user.id}: {new_item.id}")
        
        return WatchlistItemResponse(
            id=new_item.id,
            isin=new_item.isin,
            ticker=new_item.ticker,
            name=new_item.name,
            sector=new_item.sector,
            region=new_item.region,
            asset_class=new_item.asset_class,
            notes=new_item.notes,
            created_at=new_item.created_at.isoformat(),
            updated_at=new_item.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating watchlist item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Erstellen des Watchlist-Eintrags"
        )

# PUT /api/watchlist/{id}
@router.put("/api/watchlist/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: int,
    item_update: WatchlistItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualisiere einen Watchlist-Eintrag"""
    try:
        item = db.query(WatchlistItem).filter(
            WatchlistItem.id == item_id,
            WatchlistItem.userId == current_user.id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist-Eintrag nicht gefunden"
            )
        
        # Validierung
        if item_update.isin and not validate_isin(item_update.isin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges ISIN-Format"
            )
        
        # Update Felder
        if item_update.isin is not None:
            item.isin = item_update.isin.upper()
        if item_update.ticker is not None:
            item.ticker = item_update.ticker.upper()
        if item_update.name is not None:
            item.name = item_update.name
        if item_update.sector is not None:
            item.sector = item_update.sector
        if item_update.region is not None:
            item.region = item_update.region
        if item_update.asset_class is not None:
            item.asset_class = item_update.asset_class
        if item_update.notes is not None:
            item.notes = item_update.notes
        
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        
        logger.info(f"Watchlist item updated: {item_id}")
        
        return WatchlistItemResponse(
            id=item.id,
            isin=item.isin,
            ticker=item.ticker,
            name=item.name,
            sector=item.sector,
            region=item.region,
            asset_class=item.asset_class,
            notes=item.notes,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating watchlist item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Aktualisieren des Watchlist-Eintrags"
        )

# DELETE /api/watchlist/{id}
@router.delete("/api/watchlist/{item_id}")
async def delete_watchlist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lösche einen Watchlist-Eintrag"""
    try:
        item = db.query(WatchlistItem).filter(
            WatchlistItem.id == item_id,
            WatchlistItem.userId == current_user.id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist-Eintrag nicht gefunden"
            )
        
        db.delete(item)
        db.commit()
        
        logger.info(f"Watchlist item deleted: {item_id}")
        return {"message": "Watchlist-Eintrag erfolgreich gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting watchlist item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Löschen des Watchlist-Eintrags"
        )
