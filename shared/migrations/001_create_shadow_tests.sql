-- Create shadow_tests table for storing parity test results
CREATE TABLE IF NOT EXISTS shadow_tests (
    id BIGSERIAL PRIMARY KEY,
    test_id TEXT UNIQUE NOT NULL,
    merchant_id TEXT NOT NULL,
    
    -- Input data
    diff_report JSONB NOT NULL,
    legacy_response JSONB NOT NULL,
    headless_response JSONB NOT NULL,
    
    -- Council deliberation
    council_opinions JSONB[] DEFAULT '{}',
    
    -- Execution tracking
    active_provider TEXT,
    providers_attempted TEXT[] DEFAULT '{}',
    
    -- Results
    is_mitigated BOOLEAN DEFAULT FALSE,
    risk_score NUMERIC(3, 2),
    final_verdict TEXT CHECK (final_verdict IN ('PASS', 'FAIL', 'NEEDS_REVIEW')),
    mitigation_recommendation TEXT,
    
    -- Status
    status TEXT NOT NULL CHECK (status IN ('pending', 'analyzing', 'complete', 'failed')),
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on test_id for fast lookups
CREATE INDEX idx_shadow_tests_test_id ON shadow_tests(test_id);

-- Create index on merchant_id for filtering
CREATE INDEX idx_shadow_tests_merchant_id ON shadow_tests(merchant_id);

-- Create index on status for real-time feed
CREATE INDEX idx_shadow_tests_status ON shadow_tests(status);

-- Create index on created_at for chronological ordering
CREATE INDEX idx_shadow_tests_created_at ON shadow_tests(created_at DESC);

-- Enable realtime for this table
ALTER PUBLICATION supabase_realtime ADD TABLE shadow_tests;

COMMENT ON TABLE shadow_tests IS 'Stores parity test results from Shadow Twin Guardian council';
