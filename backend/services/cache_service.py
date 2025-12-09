"""
Cache Service für Portfolio-Analysen
Implementiert einen In-Memory Cache mit 12 Stunden TTL
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """
    Einfacher In-Memory Cache für Portfolio-Analysen.
    In Produktion sollte Redis oder ein ähnlicher Cache verwendet werden.
    """
    
    def __init__(self, ttl_hours: int = 12):
        """
        Initialisiert den Cache Service
        
        Args:
            ttl_hours: Time-to-Live in Stunden (Standard: 12)
        """
        self.cache: dict = {}
        self.ttl_hours = ttl_hours
    
    def _generate_key(self, user_id: int, portfolio_id: Optional[int] = None, cache_type: str = "portfolio") -> str:
        """
        Generiert einen eindeutigen Cache-Key für einen Benutzer
        
        Args:
            user_id: Benutzer-ID
            portfolio_id: Optionale Portfolio-ID
            cache_type: Art des Caches ("portfolio" oder "watchlist")
            
        Returns:
            Cache-Key als String
        """
        key_data = f"{cache_type}_analysis_{user_id}"
        if portfolio_id:
            key_data += f"_{portfolio_id}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, user_id: int, portfolio_id: Optional[int] = None, cache_type: str = "portfolio") -> Optional[dict]:
        """
        Holt eine gecachte Analyse aus dem Cache
        
        Args:
            user_id: Benutzer-ID
            portfolio_id: Optionale Portfolio-ID
            cache_type: Art des Caches ("portfolio" oder "watchlist")
            
        Returns:
            Gecachte Analyse oder None wenn nicht vorhanden/abgelaufen
        """
        key = self._generate_key(user_id, portfolio_id, cache_type)
        
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        expires_at = cached_item.get('expires_at')
        
        # Prüfe ob Cache abgelaufen ist
        if expires_at and datetime.utcnow() > expires_at:
            del self.cache[key]
            logger.info(f"Cache abgelaufen für User {user_id} ({cache_type})")
            return None
        
        logger.info(f"Cache Hit für User {user_id} ({cache_type})")
        return cached_item.get('data')
    
    def set(self, user_id: int, data: dict, portfolio_id: Optional[int] = None, cache_type: str = "portfolio") -> None:
        """
        Speichert eine Analyse im Cache
        
        Args:
            user_id: Benutzer-ID
            data: Zu cachende Daten
            portfolio_id: Optionale Portfolio-ID
            cache_type: Art des Caches ("portfolio" oder "watchlist")
        """
        key = self._generate_key(user_id, portfolio_id, cache_type)
        expires_at = datetime.utcnow() + timedelta(hours=self.ttl_hours)
        
        self.cache[key] = {
            'data': data,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        
        logger.info(f"Cache gespeichert für User {user_id} ({cache_type}), läuft ab um {expires_at}")
    
    def invalidate(self, user_id: int, portfolio_id: Optional[int] = None, cache_type: str = "portfolio") -> None:
        """
        Invalidiert den Cache für einen Benutzer
        
        Args:
            user_id: Benutzer-ID
            portfolio_id: Optionale Portfolio-ID
            cache_type: Art des Caches ("portfolio" oder "watchlist")
        """
        key = self._generate_key(user_id, portfolio_id, cache_type)
        if key in self.cache:
            del self.cache[key]
            logger.info(f"Cache invalidiert für User {user_id}")
    
    def clear(self) -> None:
        """Löscht den gesamten Cache"""
        self.cache.clear()
        logger.info("Cache geleert")


# Globale Cache-Instanz
cache_service = CacheService(ttl_hours=12)





