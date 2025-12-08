-- Migration Script: Add user_settings table
-- Run this if the user_settings table is missing

-- For PostgreSQL
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL UNIQUE,
    timezone VARCHAR(100) DEFAULT 'Europe/Berlin',
    language VARCHAR(2) DEFAULT 'de',
    currency VARCHAR(3) DEFAULT 'EUR',
    "riskProfile" VARCHAR(50),
    "investmentHorizon" VARCHAR(50),
    notifications JSONB DEFAULT '{"dailyMarket": false, "weeklySummary": false, "aiRecommendations": false, "riskWarnings": true}'::jsonb,
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_user_settings_userId ON user_settings("userId");

