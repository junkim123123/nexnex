-- Analysis Logs Table for PostgreSQL
-- This table stores analysis execution logs for audit and monitoring purposes
-- 
-- Usage: Run this SQL script on your PostgreSQL database before deploying the app
-- 
-- Example connection:
--   psql -h your-host -U your-user -d your-database -f analysis_logs.sql
-- 
-- Or via pgAdmin / DBeaver / etc.

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Logs Table
-- Stores detailed logs of each analysis execution
CREATE TABLE IF NOT EXISTS analysis_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
            -- Analysis metadata
            user_input TEXT,                    -- Original user input text
            user_email VARCHAR(255),            -- User email address (collected for beta)
            product_name VARCHAR(255),           -- Detected/extracted product name
    origin_country VARCHAR(100),         -- Origin country
    destination_country VARCHAR(100),    -- Destination country
    quantity INTEGER,                    -- Quantity/volume
    target_retail_price DECIMAL(10, 2),  -- Target retail price
    target_retail_currency VARCHAR(10) DEFAULT 'USD', -- Currency (USD, EUR, JPY, etc.)
    
    -- Analysis results
    landed_cost_per_unit DECIMAL(10, 4), -- Calculated landed cost per unit
    net_margin_percent DECIMAL(5, 2),    -- Net profit margin percentage
    success_probability DECIMAL(5, 4),    -- Success probability (0.0-1.0)
    overall_risk_score INTEGER,          -- Overall risk score (0-100)
    
    -- Risk breakdown
    price_risk INTEGER DEFAULT 0,        -- Price volatility risk (0-100)
    lead_time_risk INTEGER DEFAULT 0,    -- Lead time risk (0-100)
    compliance_risk INTEGER DEFAULT 0,   -- Compliance risk (0-100)
    reputation_risk INTEGER DEFAULT 0,   -- Reputation risk (0-100)
    
    -- Verdict
    verdict VARCHAR(50),                 -- Final verdict (Go, Conditional Go, No-Go, Strong Go)
    
    -- Data quality flags
    used_fallbacks TEXT[],               -- Array of fallback types used (e.g., ['freight', 'duty'])
    reference_transaction_count INTEGER DEFAULT 0, -- Number of reference transactions used
    
    -- Full analysis result (JSONB for flexibility)
    full_result JSONB,                   -- Complete analysis result as JSON
    
    -- Status and error handling
    status VARCHAR(20) DEFAULT 'success', -- 'success', 'failed', 'partial'
    error_message TEXT,                   -- Error message if failed
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON analysis_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_product_name ON analysis_logs(product_name);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_origin_destination ON analysis_logs(origin_country, destination_country);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_verdict ON analysis_logs(verdict);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_status ON analysis_logs(status);

-- JSONB index for full_result queries (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_analysis_logs_full_result ON analysis_logs USING GIN (full_result);

-- Comments for documentation
COMMENT ON TABLE analysis_logs IS 'Stores detailed logs of analysis executions for audit and monitoring';
COMMENT ON COLUMN analysis_logs.full_result IS 'Complete analysis result stored as JSONB for flexible querying';
COMMENT ON COLUMN analysis_logs.used_fallbacks IS 'Array of fallback types used when real data was unavailable';

