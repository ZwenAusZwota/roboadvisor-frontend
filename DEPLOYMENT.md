# Deployment-Anleitung für DigitalOcean App Platform

## Option 1: Über GitHub (Empfohlen)

1. **GitHub-Repository erstellen:**
   - Gehe zu GitHub und erstelle ein neues Repository namens `roboadvisor-app`
   - Kopiere die Repository-URL

2. **Code zu GitHub pushen:**
   ```bash
   git remote add origin https://github.com/DEIN_USERNAME/roboadvisor-app.git
   git branch -M main
   git push -u origin main
   ```

3. **App auf DigitalOcean erstellen:**
   - Gehe zu https://cloud.digitalocean.com/apps
   - Klicke auf "Create App"
   - Wähle "GitHub" als Quelle
   - Wähle dein Repository `roboadvisor-app`
   - DigitalOcean erkennt automatisch die `.do/app.yaml` Datei
   - Oder konfiguriere manuell:
     - **Build Command:** `npm install && npm run build`
     - **Output Directory:** `dist`
     - **Environment:** Static Site

## Option 2: Über DigitalOcean CLI

1. **DigitalOcean CLI installieren:**
   ```bash
   npm install -g doctl
   doctl auth init
   ```

2. **App erstellen:**
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

## Option 3: Über die DigitalOcean API

Die App kann auch direkt über die API erstellt werden, sobald ein GitHub-Repository vorhanden ist.



