-- Create and initialize the gold analytics database
CREATE DATABASE IF NOT EXISTS gold_egypt
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gold_egypt;

-- Drop existing tables in reverse dependency order to prevent foreign key constraint conflicts
DROP TABLE IF EXISTS portfolio_simulation;
DROP TABLE IF EXISTS technical_indicators;
DROP TABLE IF EXISTS karat_prices;
DROP TABLE IF EXISTS crisis_events;
DROP TABLE IF EXISTS gold_prices;

-- Create the primary fact table for daily global market feeds and macro baselines
CREATE TABLE gold_prices (
    trade_date          DATE            NOT NULL,
    gold_usd_oz         DECIMAL(10, 4)  NOT NULL,
    usd_egp_official    DECIMAL(8, 4)   NOT NULL,
    crude_oil           DECIMAL(8, 4)   NOT NULL,
    us_10y_treasury     DECIMAL(6, 4)   NOT NULL,
    sp500               DECIMAL(10, 4)  NOT NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_gold_prices PRIMARY KEY (trade_date),
    CONSTRAINT chk_gold_usd_oz_positive CHECK (gold_usd_oz > 0),
    CONSTRAINT chk_usd_egp_positive CHECK (usd_egp_official > 0),
    CONSTRAINT chk_crude_oil_positive CHECK (crude_oil > 0),
    CONSTRAINT chk_sp500_positive CHECK (sp500 > 0),
    CONSTRAINT chk_treasury_range CHECK (us_10y_treasury >= -5.0 AND us_10y_treasury <= 30.0),
    CONSTRAINT chk_trade_date_baseline CHECK (trade_date >= '2020-01-01')
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create index to optimize date-range filtering on global prices
CREATE INDEX idx_gold_prices_trade_date ON gold_prices (trade_date);

-- Create table for engineered local karat prices and absolute inflation premium decomposition
CREATE TABLE karat_prices (
    trade_date          DATE            NOT NULL,
    price_24k           DECIMAL(12, 4)  NOT NULL,
    price_21k           DECIMAL(12, 4)  NOT NULL,
    price_18k           DECIMAL(12, 4)  NOT NULL,
    theoretical_24k     DECIMAL(12, 4)  NOT NULL,
    value_driven_24k    DECIMAL(12, 4)  NOT NULL,
    infl_prem_24k       DECIMAL(12, 4)  NOT NULL,
    prem_pct_24k        DECIMAL(7, 4)   NOT NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_karat_prices PRIMARY KEY (trade_date),
    CONSTRAINT fk_karat_gold_prices FOREIGN KEY (trade_date) REFERENCES gold_prices (trade_date) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_karat_prices_positive CHECK (price_24k > 0 AND price_21k > 0 AND price_18k > 0),
    -- NOTE: chk_karat_hierarchy intentionally removed.
    -- price_{karat} = spot_price x karat_factor + making_charge_per_karat
    -- Making charges differ per karat (24K=+60, 21K=+150, 18K=+220 EGP/gram),
    -- so retail price ordering does NOT follow karat purity order.
    -- Use theoretical_24k for pure spot hierarchy comparisons.
    CONSTRAINT chk_theoretical_positive CHECK (theoretical_24k > 0)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create index to optimize date joins on local karat prices
CREATE INDEX idx_karat_prices_trade_date ON karat_prices (trade_date);

-- Create table to store pre-computed technical analysis indicators and composite signals
CREATE TABLE technical_indicators (
    trade_date          DATE            NOT NULL,
    sma50_24k           DECIMAL(12, 4)      NULL,
    sma200_24k          DECIMAL(12, 4)      NULL,
    rsi_24k             DECIMAL(6, 4)       NULL,
    macd_24k            DECIMAL(12, 4)      NULL,
    macd_sig_24k        DECIMAL(12, 4)      NULL,
    macd_hist_24k       DECIMAL(12, 4)      NULL,
    bb_upper_24k        DECIMAL(12, 4)      NULL,
    bb_mid_24k          DECIMAL(12, 4)      NULL,
    bb_lower_24k        DECIMAL(12, 4)      NULL,
    signal_24k          ENUM('BUY', 'SELL', 'HOLD')  NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_technical_indicators PRIMARY KEY (trade_date),
    CONSTRAINT fk_tech_gold_prices FOREIGN KEY (trade_date) REFERENCES gold_prices (trade_date) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_rsi_range CHECK (rsi_24k IS NULL OR (rsi_24k >= 0 AND rsi_24k <= 100)),
    CONSTRAINT chk_bb_band_order CHECK (bb_upper_24k IS NULL OR (bb_upper_24k >= bb_mid_24k AND bb_mid_24k >= bb_lower_24k))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create indices to accelerate technical signal filtering and trend lookups
CREATE INDEX idx_tech_trade_date ON technical_indicators (trade_date);
CREATE INDEX idx_tech_signal_24k ON technical_indicators (signal_24k);

-- Create table for multi-asset investment portfolio simulations with realistic transaction frictions
CREATE TABLE portfolio_simulation (
    trade_date          DATE            NOT NULL,
    port_24k_net        DECIMAL(16, 4)  NOT NULL,
    port_21k_net        DECIMAL(16, 4)  NOT NULL,
    port_18k_net        DECIMAL(16, 4)  NOT NULL,
    port_usd            DECIMAL(16, 4)  NOT NULL,
    port_cash           DECIMAL(16, 4)  NOT NULL DEFAULT 100000.0000,
    cum_return_24k      DECIMAL(10, 6)  NOT NULL,
    cum_return_21k      DECIMAL(10, 6)  NOT NULL,
    cum_return_18k      DECIMAL(10, 6)  NOT NULL,
    drawdown_24k        DECIMAL(10, 6)  NOT NULL,
    drawdown_21k        DECIMAL(10, 6)  NOT NULL,
    drawdown_18k        DECIMAL(10, 6)  NOT NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_portfolio_simulation PRIMARY KEY (trade_date),
    CONSTRAINT fk_portfolio_gold_prices FOREIGN KEY (trade_date) REFERENCES gold_prices (trade_date) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_portfolio_positive CHECK (port_24k_net > 0 AND port_21k_net > 0 AND port_18k_net > 0 AND port_usd > 0),
    CONSTRAINT chk_drawdown_non_positive CHECK (drawdown_24k <= 0 AND drawdown_21k <= 0 AND drawdown_18k <= 0)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create index to optimize equity curve performance charting over time
CREATE INDEX idx_portfolio_trade_date ON portfolio_simulation (trade_date);

-- Create standalone dimension table for charting macroeconomic and geopolitical crisis events
CREATE TABLE crisis_events (
    event_date          DATE            NOT NULL,
    label               VARCHAR(120)    NOT NULL,
    category            ENUM('pandemic','war_conflict','fx_devaluation','monetary_policy','commodity_shock','geopolitical','price_milestone') NOT NULL,
    color_hex           CHAR(6)         NOT NULL,
    fill_rgba           VARCHAR(40)     NOT NULL,
    description         TEXT                NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_crisis_events PRIMARY KEY (event_date),
    CONSTRAINT chk_color_hex_format CHECK (color_hex REGEXP '^[0-9A-Fa-f]{6}$'),
    CONSTRAINT chk_fill_rgba_format CHECK (fill_rgba REGEXP '^rgba\\([0-9]{1,3},[0-9]{1,3},[0-9]{1,3},[0-9]*(\\.[0-9]+)?\\)$')
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Create index to accelerate visual grouping of event milestones
CREATE INDEX idx_crisis_events_category ON crisis_events (category);

-- Seed historical crisis timeline records directly into the dimension table
INSERT INTO crisis_events (event_date, label, category, color_hex, fill_rgba, description) VALUES
('2020-03-15', 'COVID-19 Global Shock', 'pandemic', 'FF6B6B', 'rgba(255,107,107,0.06)', 'Global COVID-19 pandemic declared. Flight-to-safety drove gold to then-record highs. Local supply chain disruptions amplified domestic price impact.'),
('2022-02-24', 'Russia–Ukraine War', 'war_conflict', 'FF9F43', 'rgba(255,159,67,0.06)', 'Russian invasion of Ukraine. Energy price shocks, global inflation surge, and safe-haven demand reinforced upward pressure on global gold prices.'),
('2022-03-21', 'EGP Flotation Event 1', 'fx_devaluation', 'EF476F', 'rgba(239,71,111,0.07)', 'CBE first managed devaluation cycle. USD/EGP rate stepped up sharply, transmitting directly into local gold price levels.'),
('2022-10-27', 'EGP Flotation Event 2', 'fx_devaluation', 'EF476F', 'rgba(239,71,111,0.07)', 'Second CBE exchange rate adjustment. Further EGP depreciation accelerated local gold price premiums.'),
('2023-10-07', 'Gaza Conflict Escalation', 'war_conflict', 'FF6B6B', 'rgba(255,107,107,0.07)', 'Hamas attack on Israel triggers regional conflict escalation. Heightened geopolitical risk premium in gold markets.'),
('2024-03-06', 'EGP Full Float — March 2024', 'fx_devaluation', '06D6A0', 'rgba(6,214,160,0.07)', 'CBE comprehensive exchange rate liberalisation. USD/EGP surged from ~30 to ~50+. Most significant single structural break in the dataset.'),
('2024-04-01', 'Gold Hits $2,265/oz', 'price_milestone', 'FFD700', 'rgba(255,215,0,0.05)', 'Global gold spot price reached $2,265/oz — a then-record high driven by safe-haven demand and Fed rate-cut expectations.'),
('2024-09-18', 'Fed Rate Cut Pivot', 'monetary_policy', '4CC9F0', 'rgba(76,201,240,0.06)', 'US Federal Reserve initiates rate-cutting cycle. Lower opportunity cost of holding non-yielding gold provided strong structural support.'),
('2025-01-19', 'Gaza Ceasefire Agreement', 'geopolitical', '06D6A0', 'rgba(6,214,160,0.06)', 'Israel-Hamas ceasefire deal reduces immediate regional risk premium. Gold experienced a brief pullback on reduced safe-haven demand.'),
('2025-04-02', 'Trump Tariff Escalation', 'commodity_shock', 'FF9F43', 'rgba(255,159,67,0.07)', 'Sweeping US tariff announcement triggers global trade war fears. Gold surged as investors fled to safe-haven assets.'),
('2025-04-22', 'Gold Breaks $3,500/oz', 'price_milestone', 'FFD700', 'rgba(255,215,0,0.06)', 'Gold futures breach $3,500/oz for the first time in history — driven by tariff shock, USD weakness, and central bank accumulation.'),
('2025-06-13', 'Iran Strike Event', 'geopolitical', 'EF476F', 'rgba(239,71,111,0.08)', 'Israeli-US military strikes on Iranian nuclear facilities triggered an immediate geopolitical risk spike, driving gold sharply higher.');