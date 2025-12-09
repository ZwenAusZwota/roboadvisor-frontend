-- Migration: Füge Branchen-Spalte zur portfolio_holdings Tabelle hinzu
-- Datum: 2024

-- Für MySQL/MariaDB
ALTER TABLE portfolio_holdings 
ADD COLUMN sector VARCHAR(100) NULL 
COMMENT 'Branche des Wertpapiers (z.B. Technologie, Finanzen, etc.)';

-- Für PostgreSQL (falls verwendet)
-- ALTER TABLE portfolio_holdings 
-- ADD COLUMN sector VARCHAR(100) NULL;



