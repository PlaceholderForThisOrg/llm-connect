CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    session_id UUID NOT NULL,
    task_id VARCHAR NOT NULL,

    status VARCHAR NOT NULL,
    num_attempts INTEGER DEFAULT 0,

    score DOUBLE PRECISION,

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    meta JSONB,

    CONSTRAINT fk_progress_session
        FOREIGN KEY (session_id)
        REFERENCES session(id)
        ON DELETE CASCADE
);

-- Index for session lookup (very important)
CREATE INDEX idx_progress_session_id
    ON progress(session_id);

-- Optional: query by task inside session
CREATE INDEX idx_progress_session_task
    ON progress(session_id, task_id);

-- Optional: filter by status
CREATE INDEX idx_progress_status
    ON progress(status);