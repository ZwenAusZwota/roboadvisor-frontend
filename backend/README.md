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

## Environment Variables

- `SECRET_KEY` - Secret Key für JWT (in Produktion setzen!)

