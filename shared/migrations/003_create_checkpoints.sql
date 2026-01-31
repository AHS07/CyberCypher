-- Create checkpoints table for LangGraph state persistence
CREATE TABLE IF NOT EXISTS checkpoints (
    id BIGSERIAL PRIMARY KEY,
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(thread_id, checkpoint_id)
);

-- Create indexes for efficient checkpoint retrieval
CREATE INDEX idx_checkpoints_thread_id ON checkpoints(thread_id);
CREATE INDEX idx_checkpoints_created_at ON checkpoints(created_at DESC);

COMMENT ON TABLE checkpoints IS 'Stores LangGraph checkpoint data for state persistence and replay';
