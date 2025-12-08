from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import random
import os
import json

from database import get_db
from models import User, PortfolioHolding
from auth import get_current_user

# OpenAI-Import
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models für Dashboard
class PositionValue(BaseModel):
    id: int
    name: str
    isin: Optional[str]
    ticker: Optional[str]
    quantity: float
    purchase_price: str
    current_price: Optional[float] = None
    purchase_value: float
    current_value: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percent: Optional[float] = None

class PortfolioSummary(BaseModel):
    total_purchase_value: float
    total_current_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    position_count: int
    positions: List[PositionValue]

class PerformanceDataPoint(BaseModel):
    date: str
    value: float

class PerformanceHistory(BaseModel):
    data: List[PerformanceDataPoint]

class AllocationItem(BaseModel):
    category: str
    value: float
    percentage: float

class AllocationData(BaseModel):
    by_sector: List[AllocationItem]
    by_region: List[AllocationItem]
    by_asset_class: List[AllocationItem]

class RiskMetrics(BaseModel):
    beta: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None

class SectorAssignment(BaseModel):
    position_id: int
    name: str
    isin: Optional[str]
    ticker: Optional[str]
    sector: Optional[str]
    error: Optional[str] = None

class SectorCheckResult(BaseModel):
    all_sectors_assigned: bool
    assignments: List[SectorAssignment]
    unique_sectors: List[str]
    missing_count: int

# Mock-Daten für aktuelle Preise (in Produktion würde man eine API wie Yahoo Finance nutzen)
MOCK_CURRENT_PRICES = {
    "US0378331005": 185.50,  # Apple
    "US5949181045": 420.30,  # Microsoft
    "US02079K3059": 145.20,  # Alphabet
    "US0231351067": 175.80,  # Amazon
    "DE000BASF111": 45.20,   # BASF
    "US09075V1026": 95.50,   # BioNTech
    "CNE100000296": 12.50,   # BYD
    "US1912161007": 60.20,   # Coca-Cola
    "DE0005552004": 42.80,   # Deutsche Post
    "US2546871060": 95.30,   # Disney
    "US28852N1090": 18.50,   # Ellington
    "DE0006231004": 35.80,   # Infineon
    "DE000LS9TQA1": 425.00,  # Lang+Schwarz
    "DE0007100000": 68.50,   # Mercedes-Benz
    "US30303M1027": 485.20,  # Meta
    "US6410694060": 110.50,  # Nestle
    "US67066G1040": 125.80,  # NVIDIA
    "US6974351057": 195.50,  # Palo Alto
    "US79466L3024": 280.30,  # Salesforce
    "DE0007164600": 125.50,  # SAP
    "US86800U3023": 48.20,   # Super Micro
    "US92343V1044": 42.50,   # Verizon
    "US92532F1003": 445.20,  # Vertex
    "GB00BH4HKS39": 2.35,    # Vodafone
}

# Mock-Daten für Branchen-Zuordnung
SECTOR_MAPPING = {
    "US0378331005": "Technologie",
    "US5949181045": "Technologie",
    "US02079K3059": "Technologie",
    "US0231351067": "E-Commerce",
    "DE000BASF111": "Chemie",
    "US09075V1026": "Biotechnologie",
    "CNE100000296": "Automobil",
    "US1912161007": "Getränke",
    "DE0005552004": "Logistik",
    "US2546871060": "Medien",
    "US28852N1090": "Finanzen",
    "DE0006231004": "Halbleiter",
    "DE000LS9TQA1": "Finanzen",
    "DE0007100000": "Automobil",
    "US30303M1027": "Technologie",
    "US6410694060": "Konsumgüter",
    "US67066G1040": "Technologie",
    "US6974351057": "Cybersicherheit",
    "US79466L3024": "Software",
    "DE0007164600": "Software",
    "US86800U3023": "Technologie",
    "US92343V1044": "Telekommunikation",
    "US92532F1003": "Biotechnologie",
    "GB00BH4HKS39": "Telekommunikation",
}

# Mock-Daten für Regionen-Zuordnung
REGION_MAPPING = {
    "US0378331005": "Nordamerika",
    "US5949181045": "Nordamerika",
    "US02079K3059": "Nordamerika",
    "US0231351067": "Nordamerika",
    "DE000BASF111": "Europa",
    "US09075V1026": "Nordamerika",
    "CNE100000296": "Asien",
    "US1912161007": "Nordamerika",
    "DE0005552004": "Europa",
    "US2546871060": "Nordamerika",
    "US28852N1090": "Nordamerika",
    "DE0006231004": "Europa",
    "DE000LS9TQA1": "Europa",
    "DE0007100000": "Europa",
    "US30303M1027": "Nordamerika",
    "US6410694060": "Europa",
    "US67066G1040": "Nordamerika",
    "US6974351057": "Nordamerika",
    "US79466L3024": "Nordamerika",
    "DE0007164600": "Europa",
    "US86800U3023": "Nordamerika",
    "US92343V1044": "Nordamerika",
    "US92532F1003": "Nordamerika",
    "GB00BH4HKS39": "Europa",
}

# Mock-Daten für Asset-Klassen
ASSET_CLASS_MAPPING = {
    "US0378331005": "Aktien",
    "US5949181045": "Aktien",
    "US02079K3059": "Aktien",
    "US0231351067": "Aktien",
    "DE000BASF111": "Aktien",
    "US09075V1026": "Aktien",
    "CNE100000296": "Aktien",
    "US1912161007": "Aktien",
    "DE0005552004": "Aktien",
    "US2546871060": "Aktien",
    "US28852N1090": "Aktien",
    "DE0006231004": "Aktien",
    "DE000LS9TQA1": "Aktien",
    "DE0007100000": "Aktien",
    "US30303M1027": "Aktien",
    "US6410694060": "Aktien",
    "US67066G1040": "Aktien",
    "US6974351057": "Aktien",
    "US79466L3024": "Aktien",
    "DE0007164600": "Aktien",
    "US86800U3023": "Aktien",
    "US92343V1044": "Aktien",
    "US92532F1003": "Aktien",
    "GB00BH4HKS39": "Aktien",
}

def get_openai_client() -> Optional[OpenAI]:
    """Erstelle OpenAI-Client mit API-Key aus Umgebungsvariable"""
    if OpenAI is None:
        logger.warning("OpenAI-Paket nicht installiert")
        return None
    
    # Prüfe beide möglichen Variablennamen (Tippfehler-tolerant)
    api_key = os.getenv("OPENAI_SECRET") or os.getenv("OPENAI_SCRET")
    
    if not api_key:
        logger.warning("OPENAI_SECRET oder OPENAI_SCRET nicht in Umgebungsvariablen gefunden")
        return None
    
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des OpenAI-Clients: {e}")
        return None

async def get_sectors_from_openai(positions: List[Dict[str, Any]]) -> Dict[int, str]:
    """
    Fragt die OpenAI-API nach Branchen für alle Portfolio-Positionen auf einmal.
    
    Args:
        positions: Liste von Dictionaries mit position_id, name, isin, ticker
        
    Returns:
        Dictionary mit position_id -> Branche
    """
    if not positions:
        return {}
    
    client = get_openai_client()
    if not client:
        logger.warning("OpenAI-Client nicht verfügbar, verwende Fallback")
        return {}
    
    try:
        # Erstelle Prompt für alle Positionen auf einmal
        positions_info = []
        for pos in positions:
            info_parts = [f"Name: {pos['name']}"]
            if pos.get('isin'):
                info_parts.append(f"ISIN: {pos['isin']}")
            if pos.get('ticker'):
                info_parts.append(f"Ticker: {pos['ticker']}")
            positions_info.append({
                "id": pos['position_id'],
                "info": " | ".join(info_parts)
            })
        
        prompt = (
            "Bestimme für folgende Wertpapiere die Branche (Sector). "
            "Antworte NUR mit einem JSON-Objekt im Format: "
            '{"position_id": "Branche", ...}. '
            "Verwende deutsche Branchenbezeichnungen wie: Technologie, Finanzen, "
            "Gesundheitswesen, Konsumgüter, Energie, Industrie, etc. "
            "Falls die Branche nicht bestimmt werden kann, verwende 'Unbekannt'.\n\n"
            "Wertpapiere:\n"
        )
        
        for pos_info in positions_info:
            prompt += f"- ID {pos_info['id']}: {pos_info['info']}\n"
        
        prompt += "\nAntworte NUR mit dem JSON-Objekt, keine weiteren Erklärungen."
        
        # Rufe OpenAI API auf
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Kostengünstiges Modell
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein Finanzexperte, der Wertpapiere Branchen zuordnet. Antworte nur mit JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Niedrige Temperatur für konsistente Ergebnisse
            response_format={"type": "json_object"}
        )
        
        # Parse Antwort
        content = response.choices[0].message.content.strip()
        
        # Versuche JSON zu parsen
        try:
            sectors_dict = json.loads(content)
            # Konvertiere String-Keys zu Integer
            result = {}
            for key, value in sectors_dict.items():
                try:
                    position_id = int(key)
                    result[position_id] = str(value) if value else "Unbekannt"
                except (ValueError, TypeError):
                    continue
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der OpenAI-Antwort: {e}")
            logger.error(f"Antwort war: {content}")
            return {}
            
    except Exception as e:
        logger.error(f"Fehler bei OpenAI API-Aufruf: {e}")
        return {}

def get_current_price(isin: Optional[str], ticker: Optional[str]) -> Optional[float]:
    """Hole aktuellen Preis (Mock-Implementierung)"""
    # In Produktion: API-Aufruf zu Yahoo Finance, Alpha Vantage, etc.
    if isin and isin in MOCK_CURRENT_PRICES:
        return MOCK_CURRENT_PRICES[isin]
    # Fallback: zufällige Variation basierend auf Kaufpreis
    return None

def calculate_position_value(holding: PortfolioHolding) -> PositionValue:
    """Berechne Werte für eine Position"""
    purchase_price = float(holding.purchase_price.replace(',', '.'))
    quantity = float(holding.quantity)
    purchase_value = purchase_price * quantity
    
    current_price = get_current_price(holding.isin, holding.ticker)
    current_value = None
    gain_loss = None
    gain_loss_percent = None
    
    if current_price:
        current_value = current_price * quantity
        gain_loss = current_value - purchase_value
        if purchase_value > 0:
            gain_loss_percent = (gain_loss / purchase_value) * 100
    
    return PositionValue(
        id=holding.id,
        name=holding.name,
        isin=holding.isin,
        ticker=holding.ticker,
        quantity=quantity,
        purchase_price=holding.purchase_price,
        current_price=current_price,
        purchase_value=round(purchase_value, 2),
        current_value=round(current_value, 2) if current_value else None,
        gain_loss=round(gain_loss, 2) if gain_loss is not None else None,
        gain_loss_percent=round(gain_loss_percent, 2) if gain_loss_percent is not None else None
    )

# GET /api/portfolio/dashboard/summary
@router.get("/api/portfolio/dashboard/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole Portfolio-Zusammenfassung mit aktuellen Werten"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).all()
    
    if not holdings:
        return PortfolioSummary(
            total_purchase_value=0,
            total_current_value=0,
            total_gain_loss=0,
            total_gain_loss_percent=0,
            position_count=0,
            positions=[]
        )
    
    positions = [calculate_position_value(h) for h in holdings]
    
    total_purchase_value = sum(p.purchase_value for p in positions)
    total_current_value = sum(p.current_value for p in positions if p.current_value)
    total_gain_loss = total_current_value - total_purchase_value if total_current_value else 0
    total_gain_loss_percent = (total_gain_loss / total_purchase_value * 100) if total_purchase_value > 0 else 0
    
    return PortfolioSummary(
        total_purchase_value=round(total_purchase_value, 2),
        total_current_value=round(total_current_value, 2) if total_current_value else 0,
        total_gain_loss=round(total_gain_loss, 2),
        total_gain_loss_percent=round(total_gain_loss_percent, 2),
        position_count=len(positions),
        positions=positions
    )

# GET /api/portfolio/dashboard/performance
@router.get("/api/portfolio/dashboard/performance", response_model=PerformanceHistory)
async def get_performance_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole Performance-Verlauf"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).all()
    
    if not holdings:
        return PerformanceHistory(data=[])
    
    # Berechne Basis-Wert (Kaufwert)
    base_value = sum(float(h.purchase_price.replace(',', '.')) * float(h.quantity) for h in holdings)
    
    # Generiere Mock-Performance-Daten (in Produktion: echte historische Daten)
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for i in range(days + 1):
        date = start_date + timedelta(days=i)
        # Simuliere Performance mit zufälliger Variation
        import random
        variation = 1 + (random.random() - 0.5) * 0.1  # ±5% Variation
        value = base_value * variation
        data.append(PerformanceDataPoint(
            date=date.strftime("%Y-%m-%d"),
            value=round(value, 2)
        ))
    
    return PerformanceHistory(data=data)

# GET /api/portfolio/dashboard/allocation
@router.get("/api/portfolio/dashboard/allocation", response_model=AllocationData)
async def get_portfolio_allocation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole Portfolio-Aufteilung nach Branchen, Regionen und Assetklassen"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).all()
    
    if not holdings:
        return AllocationData(
            by_sector=[],
            by_region=[],
            by_asset_class=[]
        )
    
    positions = [calculate_position_value(h) for h in holdings]
    total_value = sum(p.current_value for p in positions if p.current_value) or sum(p.purchase_value for p in positions)
    
    # Berechne Aufteilung nach Branchen
    sector_values: Dict[str, float] = {}
    for h, p in zip(holdings, positions):
        isin = h.isin or ""
        sector = SECTOR_MAPPING.get(isin, "Sonstige")
        value = p.current_value if p.current_value else p.purchase_value
        sector_values[sector] = sector_values.get(sector, 0) + value
    
    by_sector = [
        AllocationItem(
            category=sector,
            value=round(value, 2),
            percentage=round((value / total_value * 100), 2) if total_value > 0 else 0
        )
        for sector, value in sorted(sector_values.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Berechne Aufteilung nach Regionen
    region_values: Dict[str, float] = {}
    for h, p in zip(holdings, positions):
        isin = h.isin or ""
        region = REGION_MAPPING.get(isin, "Sonstige")
        value = p.current_value if p.current_value else p.purchase_value
        region_values[region] = region_values.get(region, 0) + value
    
    by_region = [
        AllocationItem(
            category=region,
            value=round(value, 2),
            percentage=round((value / total_value * 100), 2) if total_value > 0 else 0
        )
        for region, value in sorted(region_values.items(), key=lambda x: x[1], reverse=True)
    ]
    
    # Berechne Aufteilung nach Assetklassen
    asset_class_values: Dict[str, float] = {}
    for h, p in zip(holdings, positions):
        isin = h.isin or ""
        asset_class = ASSET_CLASS_MAPPING.get(isin, "Sonstige")
        value = p.current_value if p.current_value else p.purchase_value
        asset_class_values[asset_class] = asset_class_values.get(asset_class, 0) + value
    
    by_asset_class = [
        AllocationItem(
            category=asset_class,
            value=round(value, 2),
            percentage=round((value / total_value * 100), 2) if total_value > 0 else 0
        )
        for asset_class, value in sorted(asset_class_values.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return AllocationData(
        by_sector=by_sector,
        by_region=by_region,
        by_asset_class=by_asset_class
    )

# GET /api/portfolio/dashboard/risk
@router.get("/api/portfolio/dashboard/risk", response_model=RiskMetrics)
async def get_risk_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hole Risikoindikatoren"""
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).all()
    
    if not holdings:
        return RiskMetrics()
    
    # Mock-Berechnungen (in Produktion: echte Berechnungen basierend auf historischen Daten)
    # Beta: Gewichteter Durchschnitt der einzelnen Betas
    # Volatilität: Standardabweichung der Renditen
    # Sharpe Ratio: (Rendite - risikofreier Zins) / Volatilität
    # Max Drawdown: Maximale Verlustphase
    
    # Für Demo: Simulierte Werte
    return RiskMetrics(
        beta=round(1.15 + random.random() * 0.2, 2),  # 1.15 - 1.35
        volatility=round(15 + random.random() * 10, 2),  # 15% - 25%
        sharpe_ratio=round(1.2 + random.random() * 0.8, 2),  # 1.2 - 2.0
        max_drawdown=round(-5 - random.random() * 10, 2)  # -5% bis -15%
    )

# GET /api/portfolio/dashboard/check-sectors
@router.get("/api/portfolio/dashboard/check-sectors", response_model=SectorCheckResult)
async def check_portfolio_sectors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Prüft, ob alle Portfoliowerte einer Branche zugeordnet sind.
    Nutzt die OpenAI-API, um fehlende Branchenzuordnungen zu bestimmen.
    """
    holdings = db.query(PortfolioHolding).filter(
        PortfolioHolding.userId == current_user.id
    ).all()
    
    if not holdings:
        return SectorCheckResult(
            all_sectors_assigned=True,
            assignments=[],
            unique_sectors=[],
            missing_count=0
        )
    
    # Bereite Positionsdaten für OpenAI vor
    positions_data = []
    for holding in holdings:
        positions_data.append({
            'position_id': holding.id,
            'name': holding.name,
            'isin': holding.isin,
            'ticker': holding.ticker
        })
    
    # Rufe OpenAI-API auf, um Branchen zu bestimmen
    sectors_from_openai = await get_sectors_from_openai(positions_data)
    
    # Erstelle Assignments
    assignments = []
    unique_sectors_set = set()
    missing_count = 0
    
    for holding in holdings:
        # Versuche zuerst OpenAI-Ergebnis, dann Mock-Daten, dann "Unbekannt"
        sector = None
        error = None
        
        if holding.id in sectors_from_openai:
            sector = sectors_from_openai[holding.id]
        elif holding.isin and holding.isin in SECTOR_MAPPING:
            sector = SECTOR_MAPPING[holding.isin]
        else:
            sector = "Unbekannt"
            missing_count += 1
        
        if sector and sector != "Unbekannt":
            unique_sectors_set.add(sector)
        
        assignments.append(SectorAssignment(
            position_id=holding.id,
            name=holding.name,
            isin=holding.isin,
            ticker=holding.ticker,
            sector=sector,
            error=error
        ))
    
    all_sectors_assigned = missing_count == 0
    
    return SectorCheckResult(
        all_sectors_assigned=all_sectors_assigned,
        assignments=assignments,
        unique_sectors=sorted(list(unique_sectors_set)),
        missing_count=missing_count
    )

