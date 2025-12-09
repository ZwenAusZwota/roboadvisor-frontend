-- Migration: Füge Region und Assetklasse-Spalten zur portfolio_holdings Tabelle hinzu
-- Datum: 2024

-- Für MySQL/MariaDB
ALTER TABLE portfolio_holdings 
ADD COLUMN region VARCHAR(100) NULL 
COMMENT 'Region des Wertpapiers (z.B. Nordamerika, Europa, etc.)',
ADD COLUMN asset_class VARCHAR(100) NULL 
COMMENT 'Assetklasse des Wertpapiers (z.B. Aktien, Anleihen, etc.)';

-- Für PostgreSQL (falls verwendet)
-- ALTER TABLE portfolio_holdings 
-- ADD COLUMN region VARCHAR(100) NULL,
-- ADD COLUMN asset_class VARCHAR(100) NULL;





