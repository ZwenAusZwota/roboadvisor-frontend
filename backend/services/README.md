# Services Package

Dieses Package enthält Service-Module für verschiedene Backend-Funktionalitäten.

## OpenAI Service

**Datei:** `openai_service.py`

Stellt Funktionen für OpenAI API-Integration bereit, insbesondere für Portfolio-Analysen.

### Verwendung

```python
from services.openai_service import analyze_portfolio

holdings = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "quantity": 10,
        "purchase_price": "150.00",
        # ...
    }
]

analysis = await analyze_portfolio(holdings, user_settings)
```

### Erweiterung

Um neue Analyse-Typen hinzuzufügen:

1. Erweitern Sie `SYSTEM_PROMPT` mit neuen Feldern
2. Aktualisieren Sie `validate_and_normalize_analysis()` für neue Felder
3. Dokumentieren Sie neue Felder in der API-Dokumentation

## Cache Service

**Datei:** `cache_service.py`

Einfacher In-Memory Cache für Analyse-Ergebnisse mit konfigurierbarem TTL.

### Verwendung

```python
from services.cache_service import cache_service

# Cache setzen
cache_service.set(user_id=123, data=analysis_result)

# Cache abrufen
cached_data = cache_service.get(user_id=123)

# Cache löschen
cache_service.invalidate(user_id=123)
```

### Produktions-Erweiterung

Für Produktion sollte Redis verwendet werden:

```python
import redis

class RedisCacheService:
    def __init__(self):
        self.redis_client = redis.Redis(...)
    
    def get(self, user_id, portfolio_id=None):
        key = self._generate_key(user_id, portfolio_id)
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    # ... weitere Methoden
```



