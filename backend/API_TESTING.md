# API Testing Guide

## Verfügbare Endpoints

### 1. Health Check
- **GET** `/health` oder `/api/health`
- Keine Authentifizierung erforderlich

### 2. Registrierung
- **POST** `/api/auth/register`
- Body: `{ "name": "Max Mustermann", "email": "max@example.com", "password": "securepassword" }`

### 3. Login (JSON)
- **POST** `/api/auth/login-json`
- Body: `{ "email": "max@example.com", "password": "securepassword" }`
- Response: `{ "access_token": "...", "token_type": "bearer" }`

### 4. Aktueller Benutzer
- **GET** `/api/auth/me`
- Header: `Authorization: Bearer <token>`
- Authentifizierung erforderlich

## Test-Methoden

### 1. Mit curl (Command Line)

#### Health Check
```bash
curl https://deine-app-url.ondigitalocean.app/api/health
```

#### Registrierung
```bash
curl -X POST https://deine-app-url.ondigitalocean.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Max Mustermann", "email": "max@example.com", "password": "test123"}'
```

#### Login
```bash
curl -X POST https://deine-app-url.ondigitalocean.app/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "max@example.com", "password": "test123"}'
```

#### Aktueller Benutzer (mit Token)
```bash
curl -X GET https://deine-app-url.ondigitalocean.app/api/auth/me \
  -H "Authorization: Bearer DEIN_TOKEN_HIER"
```

### 2. Mit Python requests

Siehe `test_api.py` für ein vollständiges Beispiel.

### 3. Mit Postman/Insomnia

1. **Postman**: https://www.postman.com/
2. **Insomnia**: https://insomnia.rest/

Importiere die folgenden Requests:

#### Registrierung
- Method: POST
- URL: `https://deine-app-url.ondigitalocean.app/api/auth/register`
- Headers: `Content-Type: application/json`
- Body (JSON):
```json
{
  "name": "Max Mustermann",
  "email": "max@example.com",
  "password": "test123"
}
```

#### Login
- Method: POST
- URL: `https://deine-app-url.ondigitalocean.app/api/auth/login-json`
- Headers: `Content-Type: application/json`
- Body (JSON):
```json
{
  "email": "max@example.com",
  "password": "test123"
}
```

#### Aktueller Benutzer
- Method: GET
- URL: `https://deine-app-url.ondigitalocean.app/api/auth/me`
- Headers: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`

### 4. Im Browser (nur GET-Requests)

Öffne im Browser:
- Health Check: `https://deine-app-url.ondigitalocean.app/api/health`
- Root: `https://deine-app-url.ondigitalocean.app/`

### 5. Mit HTTPie (einfacher als curl)

```bash
# Installieren: pip install httpie

# Registrierung
http POST https://deine-app-url.ondigitalocean.app/api/auth/register \
  name="Max Mustermann" email="max@example.com" password="test123"

# Login
http POST https://deine-app-url.ondigitalocean.app/api/auth/login-json \
  email="max@example.com" password="test123"

# Aktueller Benutzer
http GET https://deine-app-url.ondigitalocean.app/api/auth/me \
  Authorization:"Bearer DEIN_TOKEN"
```

## Lokale Tests

Für lokale Tests ersetze die URL mit:
- `http://localhost:8000` (wenn Backend lokal läuft)

## Beispiel-Workflow

1. **Registriere einen Benutzer**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "password123"}'
```

2. **Login und Token speichern**
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | jq -r '.access_token')
```

3. **Benutzerdaten abrufen**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Fehlerbehandlung

### 400 Bad Request
- Email bereits registriert
- Ungültige Daten

### 401 Unauthorized
- Falsches Passwort
- Fehlender oder ungültiger Token

### 405 Method Not Allowed
- Falsche HTTP-Methode
- Route nicht gefunden

### 500 Internal Server Error
- Datenbankfehler
- Serverfehler

## Tipps

1. **Token speichern**: Nach dem Login den `access_token` speichern für weitere Requests
2. **Content-Type**: Immer `application/json` im Header setzen
3. **Token-Format**: `Bearer <token>` (mit Leerzeichen!)
4. **Debugging**: Prüfe die Backend-Logs in DigitalOcean Dashboard

