# Logging-Anleitung für RoboAdvisor

## Übersicht

Das Backend loggt alle wichtigen Ereignisse und Fehler. Diese Anleitung zeigt dir, wie du die Logs einsehen kannst.

## Logs auf DigitalOcean App Platform einsehen

### Methode 1: Über das DigitalOcean Dashboard

1. Gehe zu [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Wähle deine App (`roboadvisor-app`) aus
3. Klicke auf den Tab **"Runtime Logs"** oder **"Logs"**
4. Wähle die Komponente **"backend"** aus
5. Die Logs werden in Echtzeit angezeigt

### Methode 2: Über die DigitalOcean CLI (doctl)

```bash
# Installiere doctl falls noch nicht vorhanden
# Windows: choco install doctl
# Mac: brew install doctl
# Linux: siehe https://docs.digitalocean.com/reference/doctl/how-to/install/

# Login
doctl auth init

# Logs anzeigen (ersetzte APP_ID mit deiner App-ID)
doctl apps logs <APP_ID> --component backend --type run --follow
```

### Methode 3: Über die DigitalOcean API

```bash
# Hole deine App-ID
curl -X GET "https://api.digitalocean.com/v2/apps" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Hole Logs
curl -X GET "https://api.digitalocean.com/v2/apps/<APP_ID>/logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Methode 4: Über MCP-Tools (in Cursor)

Wenn du MCP-Tools in Cursor verwendest:

```javascript
// Hole die letzten 100 Log-Zeilen
mcp_digitalocean_apps-get-logs({
  AppID: "deine-app-id",
  DeploymentID: "latest",
  Component: "backend",
  LogType: "RUN",
  TailLines: 100,
  Follow: false
})
```

## Lokale Entwicklung

### Logs während lokaler Entwicklung

Wenn du das Backend lokal startest:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Die Logs werden direkt in der Konsole ausgegeben. Du siehst:
- INFO: Normale Operationen (z.B. "User registered successfully")
- WARNING: Warnungen (z.B. "Email already registered")
- ERROR: Fehler mit vollständigem Traceback

### Log-Level anpassen

Um mehr Details zu sehen, kannst du das Log-Level ändern:

```python
# In backend/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Statt INFO für mehr Details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
```

## Was wird geloggt?

### Erfolgreiche Operationen
- `INFO`: User-Registrierung erfolgreich
- `INFO`: Datenbank initialisiert
- `INFO`: Application Startup

### Warnungen
- `WARNING`: Email bereits registriert
- `WARNING`: Datenbank-Verbindungsprobleme

### Fehler
- `ERROR`: 500 Internal Server Errors mit vollständigem Traceback
- `ERROR`: Datenbankfehler
- `ERROR`: Unerwartete Exceptions

## Beispiel-Logs

### Erfolgreiche Registrierung
```
2024-01-15 10:30:45 - __main__ - INFO - Registration attempt for email: test@example.com
2024-01-15 10:30:45 - __main__ - INFO - User registered successfully: test@example.com (ID: 1)
```

### Fehlerhafte Registrierung
```
2024-01-15 10:31:20 - __main__ - INFO - Registration attempt for email: test@example.com
2024-01-15 10:31:20 - __main__ - WARNING - Registration failed: Email already registered - test@example.com
```

### 500 Internal Server Error
```
2024-01-15 10:32:10 - __main__ - INFO - Registration attempt for email: newuser@example.com
2024-01-15 10:32:10 - __main__ - ERROR - Registration failed for newuser@example.com: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
2024-01-15 10:32:10 - __main__ - ERROR - Traceback (most recent call last):
  File "/app/backend/main.py", line 189, in register
    db.commit()
  ...
```

## Tipps

1. **Logs filtern**: In DigitalOcean kannst du nach Log-Level filtern (INFO, WARNING, ERROR)
2. **Logs exportieren**: Du kannst Logs aus dem DigitalOcean Dashboard exportieren
3. **Alerts einrichten**: DigitalOcean kann dich bei bestimmten Fehlern benachrichtigen
4. **Log-Retention**: DigitalOcean speichert Logs für eine begrenzte Zeit (meist 7-30 Tage)

## Troubleshooting

### Keine Logs sichtbar?
- Prüfe, ob die App läuft: `doctl apps get <APP_ID>`
- Prüfe, ob das Deployment erfolgreich war
- Warte ein paar Sekunden, Logs können verzögert sein

### Logs zu unübersichtlich?
- Filtere nach Log-Level (nur ERROR)
- Suche nach spezifischen Begriffen (z.B. "Registration failed")
- Verwende Zeitstempel, um bestimmte Zeiträume zu untersuchen



