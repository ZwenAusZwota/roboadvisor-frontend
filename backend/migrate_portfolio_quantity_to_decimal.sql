-- Migration Script: Change quantity from INTEGER to NUMERIC(15, 6)
-- Run this if the portfolio_holdings table exists with INTEGER quantity

-- For PostgreSQL
ALTER TABLE portfolio_holdings 
ALTER COLUMN quantity TYPE NUMERIC(15, 6) USING quantity::numeric(15, 6);



