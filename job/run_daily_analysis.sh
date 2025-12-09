#!/bin/bash
# Shell-Script zum Ausführen des täglichen Analyse-Jobs
# Für manuelle Ausführung oder Cron-Jobs

# Wechsle ins Backend-Verzeichnis
cd "$(dirname "$0")/.."

# Aktiviere virtuelle Umgebung falls vorhanden
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Führe den Job aus
python3 jobs/daily_analysis_job.py

# Exit Code für Monitoring
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Job erfolgreich abgeschlossen"
else
    echo "Job mit Fehler beendet (Exit Code: $exit_code)"
fi

exit $exit_code

