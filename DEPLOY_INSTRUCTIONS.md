# Deployment-Anleitung für DigitalOcean App Platform

## Schritt 1: GitHub mit DigitalOcean verbinden

1. Gehe zu https://cloud.digitalocean.com/apps
2. Klicke auf "Create App"
3. Wenn du noch nicht angemeldet bist, wirst du aufgefordert, GitHub zu verbinden
4. Klicke auf "Connect GitHub" und autorisiere DigitalOcean

## Schritt 2: App erstellen

### Option A: Über die Web-Oberfläche (Empfohlen)

1. Gehe zu https://cloud.digitalocean.com/apps
2. Klicke auf "Create App"
3. Wähle "GitHub" als Quelle
4. Wähle das Repository: `ZwenAusZwota/roboadvisor-frontend`
5. DigitalOcean erkennt automatisch die `.do/app.yaml` Datei
6. Überprüfe die Einstellungen:
   - **Region:** Frankfurt (fra1) - Europa
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `dist`
   - **Instance Size:** Basic (kleinste verfügbare Größe)
7. Klicke auf "Create Resources"

### Option B: Über die App-Spezifikation

1. Gehe zu https://cloud.digitalocean.com/apps
2. Klicke auf "Create App"
3. Wähle "App Spec" oder "Upload YAML"
4. Lade die `.do/app.yaml` Datei hoch
5. DigitalOcean erstellt die App automatisch

## Schritt 3: Deployment überwachen

- Das erste Deployment kann 5-10 Minuten dauern
- Du kannst den Fortschritt im Dashboard verfolgen
- Nach erfolgreichem Deployment erhältst du eine Live-URL

## Wichtige Hinweise

- Die App verwendet automatisch die kleinste verfügbare Instanzgröße für statische Sites
- Region ist auf Frankfurt (fra1) gesetzt
- Automatisches Deployment bei jedem Push zu `main` Branch

