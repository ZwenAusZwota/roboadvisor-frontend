"""
Tägliche Portfolio- und Watchlist-Analyse
Führt einmal täglich automatisch Analysen für alle Portfolios und Watchlists durch.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import time
import asyncio

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from database import SessionLocal, engine
from models import User, PortfolioHolding, WatchlistItem, UserSettings, AnalysisHistory
from services.openai_service import analyze_portfolio, analyze_single_asset
from services.cache_service import cache_service

# Logging konfigurieren
log_file_path = os.path.join(os.path.dirname(__file__), 'daily_analysis_job.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file_path)
    ]
)
logger = logging.getLogger(__name__)

# Konfiguration
BATCH_SIZE = 10  # Anzahl der Analysen pro Batch
DELAY_BETWEEN_BATCHES = 60  # Sekunden Pause zwischen Batches (Rate Limiting)
DELAY_BETWEEN_ANALYSES = 5  # Sekunden Pause zwischen einzelnen Analysen
MAX_ANALYSES_PER_DAY = 500  # Maximale Anzahl Analysen pro Tag (Safety Limit)
SKIP_RECENT_ANALYSES_HOURS = 12  # Überspringe Analysen, die in den letzten X Stunden erstellt wurden


def get_users_with_portfolios(db):
    """Hole alle Benutzer, die Portfolio-Positionen haben"""
    users = db.query(User).join(PortfolioHolding).distinct().all()
    return users


def get_users_with_watchlists(db):
    """Hole alle Benutzer, die Watchlist-Einträge haben"""
    users = db.query(User).join(WatchlistItem).distinct().all()
    return users


def has_recent_analysis(db, user_id: int, portfolio_holding_id: int = None, watchlist_item_id: int = None) -> bool:
    """
    Prüft, ob bereits eine Analyse in den letzten X Stunden existiert
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=SKIP_RECENT_ANALYSES_HOURS)
    
    query = db.query(AnalysisHistory).filter(
        AnalysisHistory.userId == user_id,
        AnalysisHistory.created_at >= cutoff_time
    )
    
    if portfolio_holding_id:
        query = query.filter(AnalysisHistory.portfolio_holding_id == portfolio_holding_id)
    if watchlist_item_id:
        query = query.filter(AnalysisHistory.watchlist_item_id == watchlist_item_id)
    
    return query.first() is not None


async def analyze_user_portfolio(db, user: User, user_settings: Dict, total_analyses_counter: Dict = None) -> Dict:
    """
    Analysiert das Portfolio eines Benutzers
    """
    try:
        # Hole alle Portfolio-Positionen des Benutzers
        holdings = db.query(PortfolioHolding).filter(
            PortfolioHolding.userId == user.id
        ).all()
        
        if not holdings:
            logger.info(f"User {user.id} ({user.email}) hat kein Portfolio")
            return {"success": False, "reason": "no_holdings"}
        
        # Prüfe Safety Limit (wenn Counter übergeben wurde)
        if total_analyses_counter and total_analyses_counter["count"] >= MAX_ANALYSES_PER_DAY:
            logger.warning(f"Maximales Analysen-Limit erreicht. Überspringe Portfolio-Analyse für User {user.id}.")
            return {"success": False, "reason": "limit_reached"}
        
        # Prüfe, ob bereits eine Analyse in den letzten Stunden existiert
        # (Prüfe für die erste Position als Indikator)
        if has_recent_analysis(db, user.id, portfolio_holding_id=holdings[0].id):
            logger.info(f"User {user.id} hat bereits eine kürzliche Portfolio-Analyse (innerhalb der letzten {SKIP_RECENT_ANALYSES_HOURS} Stunden), überspringe")
            return {"success": False, "reason": "recent_analysis_exists"}
        
        # Konvertiere Holdings zu Dict-Format
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
        
        logger.info(f"Starte Portfolio-Analyse für User {user.id} ({user.email}) mit {len(holdings_dict)} Positionen")
        
        # Führe Analyse durch
        analysis = await analyze_portfolio(holdings_dict, user_settings)
        
        # Speichere Analyse-Historie für jede Position
        for holding in holdings:
            ticker_match = holding.ticker or holding.isin or holding.name
            fundamental = next(
                (fa for fa in analysis.get("fundamentalAnalysis", []) 
                 if fa.get("ticker") == ticker_match),
                None
            )
            technical = next(
                (ta for ta in analysis.get("technicalAnalysis", [])
                 if ta.get("ticker") == ticker_match),
                None
            )
            
            analysis_data = {
                "portfolioAnalysis": True,
                "analysisDate": datetime.utcnow().isoformat()
            }
            
            if fundamental:
                analysis_data["fundamentalAnalysis"] = fundamental
            else:
                analysis_data["fundamentalAnalysis"] = {
                    "ticker": ticker_match,
                    "summary": "Keine detaillierte fundamentale Analyse verfügbar für diese Position.",
                    "valuation": "fair"
                }
            
            if technical:
                analysis_data["technicalAnalysis"] = technical
            else:
                analysis_data["technicalAnalysis"] = {
                    "ticker": ticker_match,
                    "trend": "neutral",
                    "rsi": "N/A",
                    "signal": "hold"
                }
            
            if analysis.get("risks"):
                analysis_data["risks"] = analysis.get("risks")
            if analysis.get("shortTermAdvice"):
                analysis_data["shortTermAdvice"] = analysis.get("shortTermAdvice")
            if analysis.get("longTermAdvice"):
                analysis_data["longTermAdvice"] = analysis.get("longTermAdvice")
            
            history_entry = AnalysisHistory(
                userId=user.id,
                portfolio_holding_id=holding.id,
                watchlist_item_id=None,
                asset_name=holding.name,
                asset_isin=holding.isin,
                asset_ticker=holding.ticker,
                analysis_data=analysis_data
            )
            db.add(history_entry)
        
        db.commit()
        logger.info(f"Portfolio-Analyse erfolgreich für User {user.id}")
        
        return {"success": True, "holdings_count": len(holdings)}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler bei Portfolio-Analyse für User {user.id}: {e}", exc_info=True)
        return {"success": False, "reason": "error", "error": str(e)}


async def analyze_user_watchlist(db, user: User, user_settings: Dict, total_analyses_counter: Dict) -> Dict:
    """
    Analysiert die Watchlist eines Benutzers
    """
    try:
        # Hole alle Watchlist-Einträge des Benutzers
        items = db.query(WatchlistItem).filter(
            WatchlistItem.userId == user.id
        ).all()
        
        if not items:
            logger.info(f"User {user.id} ({user.email}) hat keine Watchlist-Einträge")
            return {"success": False, "reason": "no_items", "analyzed": 0}
        
        analyzed_count = 0
        skipped_count = 0
        
        for item in items:
            # Prüfe Safety Limit vor jeder Analyse
            if total_analyses_counter["count"] >= MAX_ANALYSES_PER_DAY:
                logger.warning(f"Maximales Analysen-Limit erreicht. Überspringe verbleibende Items.")
                break
            
            # Prüfe, ob bereits eine Analyse in den letzten Stunden existiert
            if has_recent_analysis(db, user.id, watchlist_item_id=item.id):
                logger.debug(f"Watchlist-Item {item.id} hat bereits eine kürzliche Analyse, überspringe")
                skipped_count += 1
                continue
            
            try:
                # Konvertiere Item zu Dict
                asset_dict = {
                    "name": item.name,
                    "isin": item.isin,
                    "ticker": item.ticker,
                    "sector": item.sector,
                    "region": item.region,
                    "asset_class": item.asset_class
                }
                
                logger.info(f"Starte Watchlist-Analyse für Item {item.id} ({item.name}) von User {user.id}")
                
                # Führe Analyse durch
                analysis = await analyze_single_asset(asset_dict, user_settings)
                
                # Inkrementiere Counter
                total_analyses_counter["count"] += 1
                
                # Speichere in Historie
                history_entry = AnalysisHistory(
                    userId=user.id,
                    portfolio_holding_id=None,
                    watchlist_item_id=item.id,
                    asset_name=item.name,
                    asset_isin=item.isin,
                    asset_ticker=item.ticker,
                    analysis_data={
                        "fundamentalAnalysis": analysis.get("fundamentalAnalysis", {}),
                        "technicalAnalysis": analysis.get("technicalAnalysis", {}),
                        "risks": analysis.get("risks", []),
                        "recommendation": analysis.get("recommendation", ""),
                        "priceTarget": analysis.get("priceTarget"),
                        "watchlistAnalysis": True,
                        "analysisDate": datetime.utcnow().isoformat()
                    }
                )
                db.add(history_entry)
                db.commit()
                
                analyzed_count += 1
                logger.info(f"Watchlist-Item {item.id} erfolgreich analysiert")
                
                # Rate Limiting: Warte zwischen einzelnen Analysen
                # (Nur wenn nicht das letzte Item und Limit nicht erreicht)
                if analyzed_count < len(items) - skipped_count:
                    await asyncio.sleep(DELAY_BETWEEN_ANALYSES)
                    
            except Exception as e:
                db.rollback()
                logger.error(f"Fehler bei Watchlist-Item {item.id} Analyse: {e}", exc_info=True)
                continue
        
        logger.info(f"Watchlist-Analyse für User {user.id} abgeschlossen: {analyzed_count} analysiert, {skipped_count} übersprungen")
        return {"success": True, "analyzed": analyzed_count, "skipped": skipped_count}
        
    except Exception as e:
        logger.error(f"Fehler bei Watchlist-Analyse für User {user.id}: {e}", exc_info=True)
        return {"success": False, "reason": "error", "error": str(e)}


async def process_batch_portfolios(db, users: List[User], user_settings_map: Dict[int, Dict], total_analyses_counter: Dict) -> Dict:
    """
    Verarbeitet einen Batch von Portfolio-Analysen
    """
    results = {
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "errors": []
    }
    
    for user in users:
        try:
            # Prüfe Safety Limit vor jeder Analyse
            if total_analyses_counter["count"] >= MAX_ANALYSES_PER_DAY:
                logger.warning(f"Maximales Analysen-Limit erreicht. Überspringe verbleibende Portfolio-Analysen.")
                break
            
            user_settings = user_settings_map.get(user.id)
            result = await analyze_user_portfolio(db, user, user_settings, total_analyses_counter)
            
            if result["success"]:
                results["successful"] += 1
                total_analyses_counter["count"] += 1
            elif result.get("reason") == "recent_analysis_exists" or result.get("reason") == "no_holdings":
                results["skipped"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"User {user.id}: {result.get('reason', 'unknown')}")
            
            # Rate Limiting
            await asyncio.sleep(DELAY_BETWEEN_ANALYSES)
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"User {user.id}: {str(e)}")
            logger.error(f"Unerwarteter Fehler bei Portfolio-Analyse für User {user.id}: {e}", exc_info=True)
    
    return results


async def process_batch_watchlists(db, users: List[User], user_settings_map: Dict[int, Dict], total_analyses_counter: Dict) -> Dict:
    """
    Verarbeitet einen Batch von Watchlist-Analysen
    """
    results = {
        "successful": 0,
        "failed": 0,
        "total_analyzed": 0,
        "total_skipped": 0,
        "errors": []
    }
    
    for user in users:
        try:
            user_settings = user_settings_map.get(user.id)
            result = await analyze_user_watchlist(db, user, user_settings, total_analyses_counter)
            
            if result["success"]:
                results["successful"] += 1
                results["total_analyzed"] += result.get("analyzed", 0)
                results["total_skipped"] += result.get("skipped", 0)
            else:
                results["failed"] += 1
                results["errors"].append(f"User {user.id}: {result.get('reason', 'unknown')}")
            
            # Rate Limiting
            await asyncio.sleep(DELAY_BETWEEN_ANALYSES)
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"User {user.id}: {str(e)}")
            logger.error(f"Unerwarteter Fehler bei Watchlist-Analyse für User {user.id}: {e}", exc_info=True)
    
    return results


async def main():
    """
    Hauptfunktion für tägliche Analysen
    """
    start_time = datetime.utcnow()
    logger.info("=" * 80)
    logger.info("Starte tägliche Portfolio- und Watchlist-Analysen")
    logger.info(f"Zeitpunkt: {start_time.isoformat()}")
    logger.info("=" * 80)
    
    db = SessionLocal()
    total_analyses_counter = {"count": 0}  # Verwende Dict für Referenz-Passing
    
    try:
        # Hole alle Benutzer mit Portfolios
        users_with_portfolios = get_users_with_portfolios(db)
        logger.info(f"Gefunden: {len(users_with_portfolios)} Benutzer mit Portfolios")
        
        # Hole alle Benutzer mit Watchlists
        users_with_watchlists = get_users_with_watchlists(db)
        logger.info(f"Gefunden: {len(users_with_watchlists)} Benutzer mit Watchlists")
        
        # Hole Benutzereinstellungen für alle relevanten Benutzer
        all_user_ids = set([u.id for u in users_with_portfolios] + [u.id for u in users_with_watchlists])
        user_settings_map = {}
        
        for user_id in all_user_ids:
            settings = db.query(UserSettings).filter(UserSettings.userId == user_id).first()
            if settings:
                user_settings_map[user_id] = {
                    "riskProfile": settings.riskProfile,
                    "investmentHorizon": settings.investmentHorizon
                }
            else:
                user_settings_map[user_id] = None
        
        # Prüfe Safety Limit
        estimated_portfolio_analyses = len(users_with_portfolios)
        estimated_watchlist_items = db.query(WatchlistItem).count()
        estimated_analyses = estimated_portfolio_analyses + estimated_watchlist_items
        
        logger.info(f"Geschätzte Analysen: {estimated_analyses} ({estimated_portfolio_analyses} Portfolios, {estimated_watchlist_items} Watchlist-Items)")
        
        if estimated_analyses > MAX_ANALYSES_PER_DAY:
            logger.warning(f"Geschätzte Analysen ({estimated_analyses}) überschreiten Limit ({MAX_ANALYSES_PER_DAY})")
            logger.warning(f"Verarbeitung wird auf {MAX_ANALYSES_PER_DAY} Analysen begrenzt")
            logger.warning(f"Einige Analysen werden übersprungen")
        
        # Portfolio-Analysen in Batches verarbeiten
        portfolio_results = {
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        if users_with_portfolios:
            logger.info(f"Starte Portfolio-Analysen für {len(users_with_portfolios)} Benutzer")
            
            for i in range(0, len(users_with_portfolios), BATCH_SIZE):
                batch = users_with_portfolios[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                total_batches = (len(users_with_portfolios) + BATCH_SIZE - 1) // BATCH_SIZE
                
                logger.info(f"Verarbeite Portfolio-Batch {batch_num}/{total_batches} ({len(batch)} Benutzer)")
                
                batch_results = await process_batch_portfolios(db, batch, user_settings_map, total_analyses_counter)
                
                portfolio_results["successful"] += batch_results["successful"]
                portfolio_results["failed"] += batch_results["failed"]
                portfolio_results["skipped"] += batch_results["skipped"]
                portfolio_results["errors"].extend(batch_results["errors"])
                total_analyses_counter["count"] += batch_results["successful"]
                
                # Prüfe Limit nach jedem Batch
                if total_analyses_counter["count"] >= MAX_ANALYSES_PER_DAY:
                    logger.warning(f"Maximales Analysen-Limit ({MAX_ANALYSES_PER_DAY}) erreicht. Stoppe Portfolio-Verarbeitung.")
                    break
                
                # Warte zwischen Batches (außer beim letzten)
                if i + BATCH_SIZE < len(users_with_portfolios) and total_analyses_counter["count"] < MAX_ANALYSES_PER_DAY:
                    logger.info(f"Warte {DELAY_BETWEEN_BATCHES} Sekunden vor nächstem Batch...")
                    await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        
        # Watchlist-Analysen in Batches verarbeiten
        watchlist_results = {
            "successful": 0,
            "failed": 0,
            "total_analyzed": 0,
            "total_skipped": 0,
            "errors": []
        }
        
        if users_with_watchlists:
            logger.info(f"Starte Watchlist-Analysen für {len(users_with_watchlists)} Benutzer")
            
            for i in range(0, len(users_with_watchlists), BATCH_SIZE):
                batch = users_with_watchlists[i:i + BATCH_SIZE]
                batch_num = (i // BATCH_SIZE) + 1
                total_batches = (len(users_with_watchlists) + BATCH_SIZE - 1) // BATCH_SIZE
                
                logger.info(f"Verarbeite Watchlist-Batch {batch_num}/{total_batches} ({len(batch)} Benutzer)")
                
                batch_results = await process_batch_watchlists(db, batch, user_settings_map, total_analyses_counter)
                
                watchlist_results["successful"] += batch_results["successful"]
                watchlist_results["failed"] += batch_results["failed"]
                watchlist_results["total_analyzed"] += batch_results["total_analyzed"]
                watchlist_results["total_skipped"] += batch_results["total_skipped"]
                watchlist_results["errors"].extend(batch_results["errors"])
                total_analyses_counter["count"] += batch_results["total_analyzed"]
                
                # Prüfe Safety Limit nach jedem Batch
                if total_analyses_counter["count"] >= MAX_ANALYSES_PER_DAY:
                    logger.warning(f"Maximales Analysen-Limit ({MAX_ANALYSES_PER_DAY}) erreicht. Stoppe Watchlist-Verarbeitung.")
                    break
                
                # Warte zwischen Batches (außer beim letzten)
                if i + BATCH_SIZE < len(users_with_watchlists) and total_analyses_counter["count"] < MAX_ANALYSES_PER_DAY:
                    logger.info(f"Warte {DELAY_BETWEEN_BATCHES} Sekunden vor nächstem Batch...")
                    await asyncio.sleep(DELAY_BETWEEN_BATCHES)
        
        # Zusammenfassung
        end_time = datetime.utcnow()
        duration = end_time - start_time
        
        logger.info("=" * 80)
        logger.info("TÄGLICHE ANALYSEN ABGESCHLOSSEN")
        logger.info("=" * 80)
        logger.info(f"Startzeit: {start_time.isoformat()}")
        logger.info(f"Endzeit: {end_time.isoformat()}")
        logger.info(f"Dauer: {duration}")
        logger.info(f"Gesamt-Analysen: {total_analyses_counter['count']}")
        logger.info("")
        logger.info("PORTFOLIO-ANALYSEN:")
        logger.info(f"  Erfolgreich: {portfolio_results['successful']}")
        logger.info(f"  Übersprungen: {portfolio_results['skipped']}")
        logger.info(f"  Fehlgeschlagen: {portfolio_results['failed']}")
        logger.info("")
        logger.info("WATCHLIST-ANALYSEN:")
        logger.info(f"  Erfolgreich: {watchlist_results['successful']} Benutzer")
        logger.info(f"  Analysierte Items: {watchlist_results['total_analyzed']}")
        logger.info(f"  Übersprungene Items: {watchlist_results['total_skipped']}")
        logger.info(f"  Fehlgeschlagen: {watchlist_results['failed']} Benutzer")
        logger.info("")
        
        if portfolio_results['errors'] or watchlist_results['errors']:
            logger.warning(f"FEHLER ({len(portfolio_results['errors']) + len(watchlist_results['errors'])}):")
            for error in portfolio_results['errors'][:10]:  # Nur erste 10 Fehler
                logger.warning(f"  - {error}")
            for error in watchlist_results['errors'][:10]:
                logger.warning(f"  - {error}")
            if len(portfolio_results['errors']) + len(watchlist_results['errors']) > 20:
                logger.warning(f"  ... und {len(portfolio_results['errors']) + len(watchlist_results['errors']) - 20} weitere Fehler")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"KRITISCHER FEHLER bei täglichen Analysen: {e}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Führe das Hauptprogramm aus
    asyncio.run(main())
