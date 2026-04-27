CREATE TABLE interaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    progress_id UUID NOT NULL,

    attempt INTEGER NOT NULL,

    input JSONB,
    output JSONB,

    is_correct BOOLEAN NOT NULL,
    score DOUBLE PRECISION,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    meta JSONB,

    CONSTRAINT fk_interaction_progress
        FOREIGN KEY (progress_id)
        REFERENCES progress(id)
        ON DELETE CASCADE
);

-- Index for fast lookup of interactions per progress
CREATE INDEX idx_interaction_progress_id
    ON interaction(progress_id);

-- Ensure attempt is unique within a progress (VERY important)
CREATE UNIQUE INDEX uq_interaction_progress_attempt
    ON interaction(progress_id, attempt);

-- Optional: index for analytics / filtering
CREATE INDEX idx_interaction_created_at
    ON interaction(created_at DESC);