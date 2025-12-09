"""
Test-Script für daily_analysis_job.py
Führt einen Testlauf mit limitierter Anzahl von Analysen durch
"""
import os
import sys

# Setze Test-Modus
os.environ["DAILY_ANALYSIS_TEST_MODE"] = "true"

# Importiere und modifiziere die Konfiguration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Überschreibe Konfiguration für Test
import backend.jobs.daily_analysis_job as job_module

# Test-Konfiguration
job_module.BATCH_SIZE = 2  # Kleine Batches für Tests
job_module.DELAY_BETWEEN_BATCHES = 10  # Kürzere Pausen
job_module.DELAY_BETWEEN_ANALYSES = 2
job_module.MAX_ANALYSES_PER_DAY = 5  # Sehr niedriges Limit für Tests
job_module.SKIP_RECENT_ANALYSES_HOURS = 0  # Keine Skip-Logik im Test

import asyncio
from backend.jobs.daily_analysis_job import main

if __name__ == "__main__":
    print("=" * 80)
    print("TEST-MODUS: Tägliche Analyse-Job")
    print("=" * 80)
    print("Hinweis: Dies ist ein Test-Lauf mit limitierten Analysen")
    print(f"Batch Size: {job_module.BATCH_SIZE}")
    print(f"Max Analysen: {job_module.MAX_ANALYSES_PER_DAY}")
    print("=" * 80)
    
    asyncio.run(main())

