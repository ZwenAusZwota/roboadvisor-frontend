from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import csv
import io
import logging

from database import get_db
from models import User, PortfolioHolding
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class PortfolioHoldingCreate(BaseModel):
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: str
    purchase_date: str  # ISO format string
    quantity: float  # Unterstützt Dezimalzahlen
    purchase_price: str

class PortfolioHoldingUpdate(BaseModel):
    isin: Optional[str] = None
    ticker: Optional[str] = None
    name: Optional[str] = None
    purchase_date: Optional[str] = None
    quantity: Optional[float] = None
    purchase_price: Optional[str] = None

class PortfolioHoldingResponse(BaseModel):
    id: int
    isin: Optional[str]
    ticker: Optional[str]
    name: str
    purchase_date: str
    quantity: float  # Als float für JSON-Serialisierung
    purchase_price: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class CSVUploadResponse(BaseModel):
    success: int
    errors: List[str]
    created: List[dict]

# Helper function to validate ISIN
def validate_isin(isin: str) -> bool:
    """Validiert ISIN-Format (12 Zeichen, alphanumerisch)"""
    if not isin:
        return False
    if len(isin) != 12:
        return False
    return isin.isalnum()

# Helper function to parse date
def parse_date(date_str: str) -> datetime:
    """Parst verschiedene Datumsformate"""
    if not date_str or not date_str.strip():
        raise ValueError("Datum darf nicht leer sein")
    
    date_str = date_str.strip()
    
    # Erweiterte Liste von Datumsformaten
    formats = [
        "%Y-%m-%d",           # ISO Format: 2024-01-15
        "%d.%m.%Y",           # Deutsch: 15.01.2024
        "%d/%m/%Y",           # US Format: 15/01/2024
        "%Y-%m-%d %H:%M:%S",  # ISO mit Zeit: 2024-01-15 10:30:00
        "%d.%m.%Y %H:%M:%S",  # Deutsch mit Zeit: 15.01.2024 10:30:00
        "%d/%m/%Y %H:%M:%S",  # US mit Zeit: 15/01/2024 10:30:00
        "%Y/%m/%d",           # Alternative: 2024/01/15
        "%d-%m-%Y",           # Alternative: 15-01-2024
        "%Y.%m.%d",           # Alternative: 2024.01.15
        "%d %m %Y",           # Mit Leerzeichen: 15 01 2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Versuche auch ISO-Format mit T-Zeit-Separator
    try:
        # ISO 8601 Format: 2024-01-15T10:30:00 oder 2024-01-15T10:30:00Z
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
            return datetime.strptime(date_part, "%Y-%m-%d")
    except ValueError:
        pass
    
    raise ValueError(f"Ungültiges Datumsformat: '{date_str}'. Unterstützte Formate: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY")

# GET /api/portfolio
@router.get("/api/portfolio", response_model=List[PortfolioHoldingResponse])
async def get_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole alle Portfolio-Positionen des aktuellen Nutzers"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).order_by(PortfolioHolding.purchase_date.desc()).all()
    
    return [
        PortfolioHoldingResponse(
            id=h.id,
            isin=h.isin,
            ticker=h.ticker,
            name=h.name,
            purchase_date=h.purchase_date.isoformat(),
            quantity=float(h.quantity) if h.quantity else 0,
            purchase_price=h.purchase_price,
            created_at=h.created_at.isoformat(),
            updated_at=h.updated_at.isoformat()
        )
        for h in holdings
    ]

# GET /api/portfolio/{id}
@router.get("/api/portfolio/{holding_id}", response_model=PortfolioHoldingResponse)
async def get_portfolio_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole eine spezifische Portfolio-Position"""
    holding = db.query(PortfolioHolding).filter(
        PortfolioHolding.id == holding_id,
        PortfolioHolding.userId == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio-Position nicht gefunden"
        )
    
    return PortfolioHoldingResponse(
        id=holding.id,
        isin=holding.isin,
        ticker=holding.ticker,
        name=holding.name,
        purchase_date=holding.purchase_date.isoformat(),
        quantity=float(holding.quantity) if holding.quantity else 0,
        purchase_price=holding.purchase_price,
        created_at=holding.created_at.isoformat(),
        updated_at=holding.updated_at.isoformat()
    )

# POST /api/portfolio
@router.post("/api/portfolio", response_model=PortfolioHoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio_holding(
    holding: PortfolioHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Erstelle eine neue Portfolio-Position"""
    try:
        logger.info(f"Creating portfolio holding for user {current_user.id}: name={holding.name}, date={holding.purchase_date}")
        
        # Normalisiere leere Strings zu None
        isin = holding.isin.strip() if holding.isin and holding.isin.strip() else None
        ticker = holding.ticker.strip() if holding.ticker and holding.ticker.strip() else None
        name = holding.name.strip() if holding.name else None
        
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
        
        if holding.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anzahl muss größer als 0 sein"
            )
        
        # Konvertiere quantity zu Decimal für Datenbank
        from decimal import Decimal
        quantity_decimal = Decimal(str(holding.quantity))
        
        if not holding.purchase_price or not holding.purchase_price.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kaufpreis ist erforderlich"
            )
        
        # Parse purchase_date
        if not holding.purchase_date or not holding.purchase_date.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kaufdatum ist erforderlich"
            )
        
        try:
            purchase_date = parse_date(holding.purchase_date)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Erstelle neue Position
        new_holding = PortfolioHolding(
            userId=current_user.id,
            isin=isin.upper() if isin else None,
            ticker=ticker.upper() if ticker else None,
            name=name,
            purchase_date=purchase_date,
            quantity=quantity_decimal,
            purchase_price=holding.purchase_price.strip()
        )
        
        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)
        
        logger.info(f"Portfolio holding created for user {current_user.id}: {new_holding.id}")
        
        return PortfolioHoldingResponse(
            id=new_holding.id,
            isin=new_holding.isin,
            ticker=new_holding.ticker,
            name=new_holding.name,
            purchase_date=new_holding.purchase_date.isoformat(),
            quantity=float(new_holding.quantity) if new_holding.quantity else 0,
            purchase_price=new_holding.purchase_price,
            created_at=new_holding.created_at.isoformat(),
            updated_at=new_holding.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error creating portfolio holding for user {current_user.id}: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        logger.error(f"Request data: isin={holding.isin}, ticker={holding.ticker}, name={holding.name}, date={holding.purchase_date}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Erstellen der Portfolio-Position"
        )

# PUT /api/portfolio/{id}
@router.put("/api/portfolio/{holding_id}", response_model=PortfolioHoldingResponse)
async def update_portfolio_holding(
    holding_id: int,
    holding_update: PortfolioHoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualisiere eine Portfolio-Position"""
    try:
        holding = db.query(PortfolioHolding).filter(
            PortfolioHolding.id == holding_id,
            PortfolioHolding.userId == current_user.id
        ).first()
        
        if not holding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio-Position nicht gefunden"
            )
        
        # Validierung
        if holding_update.isin and not validate_isin(holding_update.isin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ungültiges ISIN-Format"
            )
        
        if holding_update.quantity is not None and holding_update.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anzahl muss größer als 0 sein"
            )
        
        # Update Felder
        if holding_update.isin is not None:
            holding.isin = holding_update.isin.upper()
        if holding_update.ticker is not None:
            holding.ticker = holding_update.ticker.upper()
        if holding_update.name is not None:
            holding.name = holding_update.name
        if holding_update.purchase_date is not None:
            try:
                holding.purchase_date = parse_date(holding_update.purchase_date)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        if holding_update.quantity is not None:
            from decimal import Decimal
            holding.quantity = Decimal(str(holding_update.quantity))
        if holding_update.purchase_price is not None:
            holding.purchase_price = holding_update.purchase_price
        
        holding.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(holding)
        
        logger.info(f"Portfolio holding updated: {holding_id}")
        
        return PortfolioHoldingResponse(
            id=holding.id,
            isin=holding.isin,
            ticker=holding.ticker,
            name=holding.name,
            purchase_date=holding.purchase_date.isoformat(),
            quantity=float(holding.quantity) if holding.quantity else 0,
            purchase_price=holding.purchase_price,
            created_at=holding.created_at.isoformat(),
            updated_at=holding.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating portfolio holding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Aktualisieren der Portfolio-Position"
        )

# DELETE /api/portfolio/{id}
@router.delete("/api/portfolio/{holding_id}")
async def delete_portfolio_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lösche eine Portfolio-Position"""
    try:
        holding = db.query(PortfolioHolding).filter(
            PortfolioHolding.id == holding_id,
            PortfolioHolding.userId == current_user.id
        ).first()
        
        if not holding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio-Position nicht gefunden"
            )
        
        db.delete(holding)
        db.commit()
        
        logger.info(f"Portfolio holding deleted: {holding_id}")
        return {"message": "Portfolio-Position erfolgreich gelöscht"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting portfolio holding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Löschen der Portfolio-Position"
        )

# POST /api/portfolio/upload-csv
@router.post("/api/portfolio/upload-csv", response_model=CSVUploadResponse)
async def upload_csv_portfolio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lade Portfolio-Positionen aus CSV-Datei hoch"""
    errors = []
    created = []
    success_count = 0
    
    try:
        # Lese CSV-Datei
        contents = await file.read()
        text = contents.decode('utf-8-sig')  # utf-8-sig entfernt BOM falls vorhanden
        
        # Erkenne Trennzeichen (Semikolon oder Komma)
        # Prüfe erste Zeile auf Semikolon
        first_line = text.split('\n')[0] if '\n' in text else text
        delimiter = ';' if ';' in first_line else ','
        
        csv_reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        
        # Erwartete Spalten
        required_columns = ['name', 'purchase_date', 'quantity', 'purchase_price']
        optional_columns = ['isin', 'ticker']
        
        # Prüfe Header
        if not csv_reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV-Datei ist leer oder hat keinen Header"
            )
        
        # Normalisiere Spaltennamen (trim whitespace)
        normalized_fieldnames = {name.strip(): name for name in csv_reader.fieldnames}
        csv_reader.fieldnames = list(normalized_fieldnames.keys())
        
        # Prüfe ob alle erforderlichen Spalten vorhanden sind
        missing_columns = [col for col in required_columns if col not in csv_reader.fieldnames]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fehlende Spalten in CSV: {', '.join(missing_columns)}. Erforderlich: {', '.join(required_columns)}. Gefundene Spalten: {', '.join(csv_reader.fieldnames)}"
            )
        
        # Verarbeite jede Zeile
        for row_num, row in enumerate(csv_reader, start=2):  # Start bei 2 (Header ist Zeile 1)
            try:
                # Extrahiere Werte
                name = row.get('name', '').strip()
                purchase_date_str = row.get('purchase_date', '').strip()
                quantity_str = row.get('quantity', '').strip()
                purchase_price = row.get('purchase_price', '').strip()
                isin = row.get('isin', '').strip() or None
                ticker = row.get('ticker', '').strip() or None
                
                # Validierung
                if not name:
                    errors.append(f"Zeile {row_num}: Name ist erforderlich")
                    continue
                
                if not purchase_date_str:
                    errors.append(f"Zeile {row_num}: Kaufdatum ist erforderlich")
                    continue
                
                if not quantity_str:
                    errors.append(f"Zeile {row_num}: Anzahl ist erforderlich")
                    continue
                
                if not purchase_price:
                    errors.append(f"Zeile {row_num}: Kaufpreis ist erforderlich")
                    continue
                
                if not isin and not ticker:
                    errors.append(f"Zeile {row_num}: ISIN oder Ticker muss angegeben werden")
                    continue
                
                # Parse und validiere
                try:
                    purchase_date = parse_date(purchase_date_str)
                except ValueError as e:
                    errors.append(f"Zeile {row_num}: {str(e)}")
                    continue
                
                # Parse quantity - unterstützt Komma als Dezimaltrennzeichen
                try:
                    # Ersetze Komma durch Punkt für Python float parsing
                    quantity_str_normalized = quantity_str.replace(',', '.')
                    quantity = float(quantity_str_normalized)
                    if quantity <= 0:
                        errors.append(f"Zeile {row_num}: Anzahl muss größer als 0 sein")
                        continue
                    from decimal import Decimal
                    quantity_decimal = Decimal(str(quantity))
                except ValueError:
                    errors.append(f"Zeile {row_num}: Ungültige Anzahl: {quantity_str}")
                    continue
                
                if isin and not validate_isin(isin):
                    errors.append(f"Zeile {row_num}: Ungültiges ISIN-Format: {isin}")
                    continue
                
                # Normalisiere purchase_price (Komma zu Punkt für Konsistenz, aber speichere Original)
                purchase_price_normalized = purchase_price.replace(',', '.')
                
                # Erstelle Position
                new_holding = PortfolioHolding(
                    userId=current_user.id,
                    isin=isin.upper() if isin else None,
                    ticker=ticker.upper() if ticker else None,
                    name=name,
                    purchase_date=purchase_date,
                    quantity=quantity_decimal,
                    purchase_price=purchase_price_normalized  # Speichere mit Punkt für Konsistenz
                )
                
                db.add(new_holding)
                db.commit()
                db.refresh(new_holding)
                
                success_count += 1
                created.append({
                    "id": new_holding.id,
                    "name": new_holding.name,
                    "isin": new_holding.isin,
                    "ticker": new_holding.ticker
                })
                
            except Exception as e:
                db.rollback()
                errors.append(f"Zeile {row_num}: Fehler beim Verarbeiten - {str(e)}")
                continue
        
        logger.info(f"CSV upload completed for user {current_user.id}: {success_count} created, {len(errors)} errors")
        
        return CSVUploadResponse(
            success=success_count,
            errors=errors,
            created=created
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing CSV upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Verarbeiten der CSV-Datei: {str(e)}"
        )

# GET /api/portfolio/csv-template
@router.get("/api/portfolio/csv-template")
async def get_csv_template():
    """Lade CSV-Template herunter"""
    # Template mit Semikolon als Trennzeichen (deutsches Format)
    template = "name;purchase_date;quantity;purchase_price;isin;ticker\n"
    template += "Apple Inc.;2024-01-15;10;150.50;US0378331005;AAPL\n"
    template += "Microsoft Corporation;2024-02-20;5;380.25;US5949181045;MSFT\n"
    template += "BASF;2024-01-01;11.532;77.0855;DE000BASF111;\n"
    
    from fastapi.responses import Response
    return Response(
        content=template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=portfolio_template.csv"}
    )

