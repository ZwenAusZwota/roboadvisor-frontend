# RoboAdvisor Backend API

FastAPI-Backend für die RoboAdvisor-Anwendung.

## Lokale Entwicklung

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Server starten
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /` - API Status
- `GET /health` - Health Check
- `POST /api/auth/register` - Benutzer registrieren
- `POST /api/auth/login-json` - Login (JSON)
- `POST /api/auth/login` - Login (OAuth2 Form)
- `GET /api/auth/me` - Aktueller Benutzer (authentifiziert)

## API Dokumentation

FastAPI stellt automatisch interaktive API-Dokumentation bereit:

- **Swagger UI**: `http://localhost:8000/docs` (lokal) oder `https://deine-app-url.ondigitalocean.app/docs`
- **ReDoc**: `http://localhost:8000/redoc` (lokal) oder `https://deine-app-url.ondigitalocean.app/redoc`

Hier kannst du alle Endpoints testen, Requests senden und Responses sehen!

## API Testing

Siehe `API_TESTING.md` für detaillierte Anleitung zum Testen der API.

Schnelltest mit Python:
```bash
cd backend
pip install requests
python test_api.py
```

## Environment Variables

- `SECRET_KEY` - Secret Key für JWT (in Produktion setzen!)



