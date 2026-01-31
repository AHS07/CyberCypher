-- Create reliability_logs table for tracking provider failures and failovers
CREATE TABLE IF NOT EXISTS reliability_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('success', 'failure', 'failover')),
    
    -- Error details (for failures)
    error_code TEXT,
    error_message TEXT,
    
    -- Failover tracking
    failover_to TEXT,
    
    -- Performance metrics
    response_time_ms NUMERIC(10, 2),
    
    -- Timestamp
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for analytics
CREATE INDEX idx_reliability_logs_test_id ON reliability_logs(test_id);
CREATE INDEX idx_reliability_logs_provider ON reliability_logs(provider);
CREATE INDEX idx_reliability_logs_event_type ON reliability_logs(event_type);
CREATE INDEX idx_reliability_logs_timestamp ON reliability_logs(timestamp DESC);

-- Create composite index for provider health queries
CREATE INDEX idx_reliability_logs_provider_event ON reliability_logs(provider, event_type, timestamp DESC);

COMMENT ON TABLE reliability_logs IS 'Tracks LLM provider reliability, failures, and failover events';
