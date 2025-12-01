-- NexSupply Database Schema (PostgreSQL)
-- Enterprise-grade schema for production use

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (for Phase 2 - Multi-user support)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analysis requests table (Audit Trail)
CREATE TABLE IF NOT EXISTS analysis_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    raw_input TEXT,
    detected_market VARCHAR(50),
    detected_volume INTEGER,
    detected_channel VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending', -- 'success', 'failed', 'pending'
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analysis results table (Core Data)
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES analysis_requests(id) ON DELETE CASCADE,
    product_name VARCHAR(255),
    target_market VARCHAR(50),
    volume INTEGER,
    unit_ddp_usd DECIMAL(10, 2),
    total_project_cost_usd DECIMAL(12, 2),
    margin_rate DECIMAL(5, 2),
    risk_level VARCHAR(20),
    raw_json JSONB, -- AI 응답 원본 저장 (Schema-less 유연성)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leads table (Sales Pipeline)
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    result_id UUID REFERENCES analysis_results(id) ON DELETE SET NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'closed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_analysis_requests_user_id ON analysis_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_requests_created_at ON analysis_requests(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_request_id ON analysis_results(request_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_leads_result_id ON leads(result_id);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

-- JSONB index for raw_json queries (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_analysis_results_raw_json ON analysis_results USING GIN (raw_json);

