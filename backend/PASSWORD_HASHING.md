# Passwort-Hashing

## Übersicht

Die Anwendung verwendet **Argon2** für die Passwort-Verschlüsselung.

## Warum Argon2?

- **Modern und sicher**: Gewinner des Password Hashing Competition 2015
- **Kein Passwort-Limit**: Im Gegensatz zu bcrypt (72 Bytes) unterstützt Argon2 Passwörter beliebiger Länge
- **OWASP empfohlen**: Wird von OWASP als moderne Alternative zu bcrypt empfohlen
- **Resistent gegen GPU-Angriffe**: Besser geschützt gegen moderne Angriffsmethoden

## Technische Details

### Passwort-Längenlimits

- **Minimum**: 6 Zeichen
- **Maximum**: 128 Zeichen (praktisches Limit, kein technisches)
- **Kein Byte-Limit**: Argon2 hat kein 72-Byte-Limit wie bcrypt

### Migration

Die `verify_password()` Funktion unterstützt sowohl:
- **Argon2**: Für neue Passwörter (Standard)
- **bcrypt**: Für bestehende Passwörter (Migration)

Bestehende Benutzer können sich weiterhin anmelden. Beim nächsten Passwort-Reset wird das Passwort mit Argon2 gehasht.

## Implementierung

```python
# Passwort hashen
hashed_password = get_password_hash(password)

# Passwort verifizieren
is_valid = verify_password(plain_password, hashed_password)
```

## Abhängigkeiten

- `passlib[argon2]==1.7.4` - Passwort-Hashing-Bibliothek mit Argon2-Unterstützung

## Sicherheit

Argon2 verwendet standardmäßig sichere Parameter:
- **Memory Cost**: 65536 KB (64 MB)
- **Time Cost**: 2 Iterationen
- **Parallelism**: 1 Thread

Diese Parameter können bei Bedarf angepasst werden, sind aber für die meisten Anwendungen ausreichend.





