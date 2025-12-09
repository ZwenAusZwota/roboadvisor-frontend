-- Migration Script: Add watchlist_items and analysis_history tables
-- Run this to add Watchlist and Analysis History functionality

-- Watchlist Items Table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL,
    isin VARCHAR(12),
    ticker VARCHAR(20),
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    region VARCHAR(100),
    asset_class VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_watchlist_items_userId ON watchlist_items("userId");
CREATE INDEX IF NOT EXISTS ix_watchlist_items_isin ON watchlist_items(isin);
CREATE INDEX IF NOT EXISTS ix_watchlist_items_ticker ON watchlist_items(ticker);

-- Analysis History Table
CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL,
    "portfolio_holding_id" INTEGER,
    "watchlist_item_id" INTEGER,
    asset_name VARCHAR(255) NOT NULL,
    asset_isin VARCHAR(12),
    asset_ticker VARCHAR(20),
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY ("portfolio_holding_id") REFERENCES portfolio_holdings(id) ON DELETE CASCADE,
    FOREIGN KEY ("watchlist_item_id") REFERENCES watchlist_items(id) ON DELETE CASCADE,
    -- Constraint: Es muss entweder portfolio_holding_id ODER watchlist_item_id gesetzt sein
    CHECK (
        ("portfolio_holding_id" IS NOT NULL AND "watchlist_item_id" IS NULL) OR
        ("portfolio_holding_id" IS NULL AND "watchlist_item_id" IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS ix_analysis_history_userId ON analysis_history("userId");
CREATE INDEX IF NOT EXISTS ix_analysis_history_portfolio_holding_id ON analysis_history("portfolio_holding_id");
CREATE INDEX IF NOT EXISTS ix_analysis_history_watchlist_item_id ON analysis_history("watchlist_item_id");
CREATE INDEX IF NOT EXISTS ix_analysis_history_created_at ON analysis_history(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_analysis_history_asset_isin ON analysis_history(asset_isin);
CREATE INDEX IF NOT EXISTS ix_analysis_history_asset_ticker ON analysis_history(asset_ticker);
