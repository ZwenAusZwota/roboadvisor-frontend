-- SQL Script zum manuellen Erstellen der Tabellen
-- Für PostgreSQL (DigitalOcean Managed Database)

-- Erstelle Tabellen, falls sie nicht existieren

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

CREATE TABLE IF NOT EXISTS risk_profiles (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER,
    risk_tolerance INTEGER NOT NULL,
    investment_horizon INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS securities (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    recommendation VARCHAR(255) NOT NULL,
    recommendation_time TIMESTAMP NOT NULL,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    language_code VARCHAR(2) NOT NULL,
    username VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL UNIQUE,
    timezone VARCHAR(100) DEFAULT 'Europe/Berlin',
    language VARCHAR(2) DEFAULT 'de',
    currency VARCHAR(3) DEFAULT 'EUR',
    "riskProfile" VARCHAR(50),
    "investmentHorizon" VARCHAR(50),
    notifications JSONB,
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_user_settings_userId ON user_settings("userId");

