# Tägliche Analyse-Jobs

## Übersicht

Dieses Verzeichnis enthält automatisierte Jobs für regelmäßige Portfolio- und Watchlist-Analysen.

## daily_analysis_job.py

Führt einmal täglich automatisch Analysen für alle Portfolios und Watchlists durch.

### Features

- **Batch-Verarbeitung**: Verarbeitet Analysen in konfigurierbaren Batches
- **Rate Limiting**: Verhindert Überlastung der OpenAI API
- **Intelligente Skip-Logik**: Überspringt Analysen, die bereits in den letzten 12 Stunden erstellt wurden
- **Robuste Fehlerbehandlung**: Einzelne Fehler stoppen nicht die gesamte Verarbeitung
- **Detailliertes Logging**: Umfassende Logs für Monitoring und Debugging
- **Safety Limits**: Verhindert unbeabsichtigte Massen-Analysen

### Konfiguration

Die folgenden Parameter können in `daily_analysis_job.py` angepasst werden:

```python
BATCH_SIZE = 10  # Anzahl der Analysen pro Batch
DELAY_BETWEEN_BATCHES = 60  # Sekunden Pause zwischen Batches
DELAY_BETWEEN_ANALYSES = 5  # Sekunden Pause zwischen einzelnen Analysen
MAX_ANALYSES_PER_DAY = 500  # Maximale Anzahl Analysen pro Tag
SKIP_RECENT_ANALYSES_HOURS = 12  # Überspringe Analysen der letzten X Stunden
```

### Ausführung

#### Lokale Ausführung

```bash
cd backend
python jobs/daily_analysis_job.py
```

#### Als Cron Job (Linux/Mac)

```bash
# Crontab öffnen
crontab -e

# Füge diese Zeile hinzu (führt täglich um 2 Uhr morgens aus):
0 2 * * * cd /path/to/roboadvisor/backend && /usr/bin/python3 jobs/daily_analysis_job.py >> logs/daily_analysis.log 2>&1
```

#### Windows Task Scheduler

1. Task Scheduler öffnen
2. "Create Basic Task" wählen
3. Trigger: "Daily" um gewünschte Zeit
4. Action: "Start a program"
   - Program: `python.exe`
   - Arguments: `jobs/daily_analysis_job.py`
   - Start in: `C:\path\to\roboadvisor\backend`

#### DigitalOcean App Platform Scheduled Job

Füge in `.do/app.yaml` oder App-Spec hinzu:

```yaml
jobs:
  - name: daily-analysis
    github:
      repo: ZwenAusZwota/roboadvisor-frontend
      branch: main
    run_command: python jobs/daily_analysis_job.py
    source_dir: backend
    environment_slug: python
    schedule:
      cron: "0 2 * * *"  # Täglich um 2 Uhr UTC
    envs:
      - key: DATABASE_URL
        value: "${db-postgresql-fra1-80863.DATABASE_URL}"
        scope: RUN_TIME
      - key: OPENAI_SECRET
        value: "${OPENAI_SECRET}"
        scope: RUN_AND_BUILD_TIME
```

### Logging

- **Console Output**: Alle Logs werden auf stdout ausgegeben
- **Log File**: Zusätzlich wird `daily_analysis_job.log` im Backend-Verzeichnis erstellt
- **Log Level**: INFO (kann in der Datei angepasst werden)

### Performance-Optimierungen

1. **Batch-Verarbeitung**: Verarbeitet Benutzer in Batches, nicht einzeln
2. **Skip-Logik**: Überspringt bereits analysierte Assets innerhalb des letzten Zeitfensters
3. **Rate Limiting**: Verhindert API-Überlastung durch Pausen zwischen Analysen
4. **Effiziente DB-Queries**: Verwendet JOINs und distinkte Abfragen
5. **Fehler-Isolation**: Einzelne Fehler stoppen nicht die gesamte Verarbeitung

### Monitoring

Das Script gibt eine detaillierte Zusammenfassung aus:

- Anzahl erfolgreicher/fehlgeschlagener/übersprungener Analysen
- Gesamtdauer der Ausführung
- Fehlerliste (falls vorhanden)
- Performance-Metriken

### Troubleshooting

**Problem: Job läuft zu lange**
- Reduziere `BATCH_SIZE`
- Erhöhe `DELAY_BETWEEN_BATCHES` und `DELAY_BETWEEN_ANALYSES`
- Erhöhe `SKIP_RECENT_ANALYSES_HOURS`

**Problem: Zu viele API-Calls**
- Erhöhe `DELAY_BETWEEN_ANALYSES`
- Erhöhe `SKIP_RECENT_ANALYSES_HOURS`
- Reduziere `MAX_ANALYSES_PER_DAY`

**Problem: Datenbankfehler**
- Prüfe `DATABASE_URL` Environment Variable
- Stelle sicher, dass Datenbank erreichbar ist
- Prüfe Datenbank-Logs

### Erweiterungen

Zukünftige Verbesserungen könnten umfassen:

- **Priorisierung**: Wichtige Portfolios zuerst analysieren
- **Retry-Logik**: Automatische Wiederholung fehlgeschlagener Analysen
- **Metrics Export**: Export von Metriken zu Monitoring-Tools
- **Email-Benachrichtigungen**: Bei kritischen Fehlern
- **Parallele Verarbeitung**: Mehrere Batches gleichzeitig (mit Vorsicht)

