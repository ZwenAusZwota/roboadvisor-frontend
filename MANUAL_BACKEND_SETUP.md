# Manuelle Backend-Komponente hinzufügen

## Schritt-für-Schritt Anleitung

### 1. DigitalOcean Dashboard öffnen
- Gehe zu: https://cloud.digitalocean.com/apps
- Wähle deine App: `roboadvisor-frontend`

### 2. Neue Komponente hinzufügen

#### Schritt 1: Settings öffnen
- Klicke auf den Tab **"Settings"** (oben in der Navigation)

#### Schritt 2: Components-Bereich
- Scrolle zu **"Components"**
- Klicke auf **"Add Component"** oder **"Edit Components"**

#### Schritt 3: Service-Komponente erstellen
Wähle **"Service"** als Component Type und konfiguriere:

**Basic Settings:**
- **Name:** `api`
- **Source:** GitHub
- **Repository:** `ZwenAusZwota/roboadvisor-frontend`
- **Branch:** `main`
- **Source Directory:** `backend`

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment:** `Python`

**Runtime Settings:**
- **HTTP Port:** `8000`
- **Instance Size:** `Basic XXS` (kleinste verfügbare Größe)
- **Instance Count:** `1`

**Routes:**
- **Path:** `/api`

**Environment Variables:**
- `SECRET_KEY` (bereits vorhanden, wird automatisch übernommen)

### 3. Speichern und Deployment
- Klicke auf **"Save"** oder **"Update Component"**
- DigitalOcean startet automatisch ein neues Deployment
- Das Deployment kann 5-10 Minuten dauern

### 4. Überprüfung

Nach dem Deployment:
1. **Backend-URL prüfen:**
   - Im Dashboard unter "Components" → `api`
   - Die URL sollte sein: `https://deine-app-url.ondigitalocean.app/api`

2. **Health Check:**
   ```bash
   curl https://deine-app-url.ondigitalocean.app/api/health
   ```

3. **Logs prüfen:**
   - Im Dashboard: Runtime Logs → Component `api`
   - Prüfe auf Fehler oder Erfolgsmeldungen

## Alternative: App Spec aktualisieren

Falls die manuelle Komponente nicht funktioniert:

1. Gehe zu **Settings → App Spec**
2. Ersetze den Inhalt mit folgendem:

```yaml
name: roboadvisor-app
region: fra1

services:
  - name: api
    github:
      repo: ZwenAusZwota/roboadvisor-frontend
      branch: main
      deploy_on_push: true
    source_dir: backend
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 8000
    routes:
      - path: /api
    envs:
      - key: SECRET_KEY
        value: ${SECRET_KEY}
        type: SECRET
        scope: RUN_TIME

static_sites:
  - name: web
    github:
      repo: ZwenAusZwota/roboadvisor-frontend
      branch: main
      deploy_on_push: true
    build_command: npm ci && npm run build
    output_dir: dist
    index_document: index.html
    error_document: index.html
    routes:
      - path: /
```

3. Klicke auf **"Save"**
4. DigitalOcean erstellt automatisch beide Komponenten

## Troubleshooting

### Backend startet nicht
- Prüfe die Logs im Dashboard
- Stelle sicher, dass `requirements.txt` im `backend/` Verzeichnis ist
- Prüfe, ob `SECRET_KEY` als Environment Variable gesetzt ist

### CORS-Fehler
- Das Backend erlaubt aktuell alle Origins
- In Produktion sollten spezifische Domains gesetzt werden

### Route nicht erreichbar
- Prüfe die Ingress-Konfiguration
- Stelle sicher, dass `/api` als Route konfiguriert ist



