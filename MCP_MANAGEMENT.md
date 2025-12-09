# DigitalOcean Backend-Verwaltung über MCP

## Übersicht

Das Python-Backend kann über die DigitalOcean MCP-Tools verwaltet werden. Hier sind die wichtigsten Befehle:

## Verfügbare MCP-Tools für Backend-Verwaltung

### 1. App-Informationen abrufen
```javascript
// App-Status prüfen
mcp_digitalocean_apps-get-info({ AppID: "deine-app-id" })

// Deployment-Status prüfen
mcp_digitalocean_apps-get-deployment-status({ AppID: "deine-app-id" })
```

### 2. Logs anzeigen
```javascript
// Backend-Logs abrufen
mcp_digitalocean_apps-get-logs({
  AppID: "deine-app-id",
  DeploymentID: "deployment-id",
  Component: "api",
  LogType: "RUN",
  TailLines: 100
})
```

### 3. App aktualisieren
```javascript
// App-Spezifikation aktualisieren
mcp_digitalocean_apps-update({
  app_id: "deine-app-id",
  update: {
    spec: {
      // Aktualisierte Spezifikation
    }
  }
})
```

### 4. Environment-Variablen verwalten
Über die App-Spezifikation in `.do/app.yaml` können Environment-Variablen gesetzt werden.

## Praktische Beispiele

### Backend-Logs in Echtzeit anzeigen
```javascript
// Letzte 50 Zeilen der Backend-Logs
mcp_digitalocean_apps-get-logs({
  AppID: "deine-app-id",
  DeploymentID: "latest",
  Component: "api",
  LogType: "RUN",
  TailLines: 50,
  Follow: true
})
```

### Health Check des Backends
```bash
# Über die API
curl https://deine-app-url.ondigitalocean.app/health
```

### Backend neu starten
```javascript
// Über App-Update (triggert neues Deployment)
mcp_digitalocean_apps-update({
  app_id: "deine-app-id",
  update: {
    spec: {
      // Gleiche Spezifikation, aber triggert Restart
    }
  }
})
```

## Lokale Entwicklung

### Backend lokal starten
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend mit Backend verbinden
```bash
# .env Datei erstellen
VITE_API_URL=http://localhost:8000
```

## Deployment-Workflow

1. **Code ändern** → Committen und Pushen zu GitHub
2. **Automatisches Deployment** → DigitalOcean erkennt Änderungen
3. **Logs prüfen** → Über MCP-Tools oder Dashboard
4. **Health Check** → `/health` Endpoint prüfen

## Wichtige Endpoints

- `GET /health` - Backend Health Check
- `POST /api/auth/register` - Benutzer registrieren
- `POST /api/auth/login-json` - Login
- `GET /api/auth/me` - Aktueller Benutzer (authentifiziert)

## Troubleshooting

### Backend startet nicht
1. Logs prüfen: `mcp_digitalocean_apps-get-logs`
2. Environment-Variablen prüfen
3. Build-Command prüfen

### CORS-Fehler
- Backend erlaubt aktuell alle Origins (`allow_origins=["*"]`)
- In Produktion spezifische Domains setzen

### Database-Fehler
- Aktuell In-Memory Storage (fake_users_db)
- Für Produktion: PostgreSQL oder MySQL über DigitalOcean Database hinzufügen







