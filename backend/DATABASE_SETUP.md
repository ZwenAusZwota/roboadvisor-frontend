# Datenbank Setup

## DigitalOcean Database Einrichtung

### 1. Datenbank in DigitalOcean erstellen

1. Gehe zu **DigitalOcean Dashboard** → **Databases**
2. Klicke auf **Create Database Cluster**
3. Wähle:
   - **Engine**: MySQL (oder MariaDB)
   - **Region**: Frankfurt (fra1) - sollte mit deiner App übereinstimmen
   - **Plan**: Basic (kleinste Größe für Entwicklung)
4. Erstelle den Cluster

### 2. Datenbank an App binden

1. Gehe zu deiner App im **DigitalOcean Dashboard**
2. Klicke auf **Settings** → **Components**
3. Klicke auf deine `api` Komponente
4. Scrolle zu **Environment Variables**
5. DigitalOcean sollte automatisch `DATABASE_URL` hinzufügen, wenn die Datenbank mit dem gleichen Tag versehen ist
6. Falls nicht, füge manuell hinzu:
   - **Key**: `DATABASE_URL`
   - **Value**: Die Connection String von der Datenbank (Format: `mysql+pymysql://user:password@host:port/database`)

### 3. Datenbank-Tag setzen

Wenn du ein Database Tag hinterlegt hast:
1. Gehe zu deiner Datenbank im Dashboard
2. Klicke auf **Settings**
3. Füge das Tag hinzu (z.B. `roboadvisor-db`)
4. Stelle sicher, dass deine App das gleiche Tag hat

### 4. Tabellen erstellen

**WICHTIG**: Bei DigitalOcean Managed PostgreSQL-Datenbanken hat der Standard-Benutzer oft keine Berechtigung, Tabellen zu erstellen. Du musst die Tabellen manuell erstellen.

#### Option 1: Über DigitalOcean Console (Empfohlen)

1. Gehe zu deiner Datenbank im **DigitalOcean Dashboard**
2. Klicke auf **"Console"** oder **"Query"**
3. Kopiere den Inhalt von `backend/create_tables.sql`
4. Führe das SQL-Script in der Console aus

#### Option 2: Über psql (Command Line)

```bash
# Verbinde dich mit der Datenbank
psql "postgresql://user:password@host:port/database?sslmode=require"

# Führe das SQL-Script aus
\i backend/create_tables.sql
```

Oder direkt:

```bash
psql "postgresql://user:password@host:port/database?sslmode=require" -f backend/create_tables.sql
```

#### Option 3: Über Python Script (wenn Berechtigungen vorhanden)

```bash
cd backend
python init_db.py
```

**Hinweis**: Die App startet auch ohne Tabellen, aber API-Endpoints werden fehlschlagen, bis die Tabellen existieren.

## Datenbankstruktur

### Tabellen

1. **users**
   - `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
   - `email` (VARCHAR(120), UNIQUE, NOT NULL)
   - `password` (VARCHAR(128), NOT NULL)

2. **risk_profiles**
   - `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
   - `userId` (INT, FOREIGN KEY → users.id)
   - `risk_tolerance` (INT, NOT NULL)
   - `investment_horizon` (INT, NOT NULL)
   - `created_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

3. **securities**
   - `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
   - `userId` (INT, FOREIGN KEY → users.id, NOT NULL)
   - `name` (VARCHAR(255), NOT NULL)
   - `quantity` (INT, NOT NULL)
   - `recommendation` (VARCHAR(255), NOT NULL)
   - `recommendation_time` (DATETIME, NOT NULL)

4. **telegram_users**
   - `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
   - `first_name` (VARCHAR(255), NOT NULL)
   - `language_code` (VARCHAR(2), NOT NULL)
   - `username` (VARCHAR(255), NOT NULL)
   - `active` (BOOLEAN, DEFAULT TRUE)
   - `admin` (BOOLEAN, DEFAULT FALSE)

## Lokale Entwicklung

Für lokale Entwicklung kannst du eine lokale MySQL/MariaDB Datenbank verwenden:

```bash
# .env Datei erstellen
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=dein_passwort
DB_NAME=roboadvisor
```

Oder setze `DATABASE_URL` direkt:

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/roboadvisor?charset=utf8mb4
```

## Troubleshooting

### Verbindungsfehler

- Prüfe, ob `DATABASE_URL` korrekt gesetzt ist
- Stelle sicher, dass die Datenbank-Firewall-Regeln die App-IP erlauben
- Prüfe die Logs: `backend/main.py` loggt Datenbankfehler

### Tabellen werden nicht erstellt (Permission Denied)

**Problem**: `permission denied for schema public`

**Lösung**: Bei DigitalOcean Managed PostgreSQL-Datenbanken hat der Standard-Benutzer keine CREATE-Berechtigung. Du musst die Tabellen manuell erstellen:

1. **Über DigitalOcean Console** (einfachste Methode):
   - Gehe zu deiner Datenbank → **Console**
   - Kopiere den Inhalt von `backend/create_tables.sql`
   - Führe das Script aus

2. **Über psql**:
   ```bash
   psql "postgresql://user:password@host:port/database?sslmode=require" -f backend/create_tables.sql
   ```

3. **Berechtigungen prüfen**:
   - Die App prüft beim Start, ob Tabellen existieren
   - Wenn Tabellen existieren, startet die App normal
   - Wenn nicht, siehst du eine Warnung in den Logs

**Nach dem Erstellen der Tabellen**: Die App funktioniert normal, auch wenn beim Start eine Warnung erscheint.

### Migrationen

Aktuell werden Tabellen automatisch erstellt. Für Produktion sollte ein Migrations-Tool wie Alembic verwendet werden.

