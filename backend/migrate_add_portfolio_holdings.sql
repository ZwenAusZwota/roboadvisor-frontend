-- Migration Script: Add portfolio_holdings table
-- Run this if the portfolio_holdings table is missing

-- For PostgreSQL
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL,
    isin VARCHAR(12),
    ticker VARCHAR(20),
    name VARCHAR(255) NOT NULL,
    purchase_date TIMESTAMP NOT NULL,
    quantity NUMERIC(15, 6) NOT NULL,
    purchase_price VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_portfolio_holdings_userId ON portfolio_holdings("userId");
CREATE INDEX IF NOT EXISTS ix_portfolio_holdings_isin ON portfolio_holdings(isin);
CREATE INDEX IF NOT EXISTS ix_portfolio_holdings_ticker ON portfolio_holdings(ticker);

