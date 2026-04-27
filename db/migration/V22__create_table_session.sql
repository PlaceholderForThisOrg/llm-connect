CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE session (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    learner_id VARCHAR NOT NULL,
    activity_id VARCHAR NOT NULL,

    status VARCHAR NOT NULL,
    progress DOUBLE PRECISION,

    started_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    current_task VARCHAR NOT NULL,

    meta JSONB,

    score DOUBLE PRECISION,

    CONSTRAINT fk_session_learner
        FOREIGN KEY (learner_id)
        REFERENCES learner(user_id)
        ON DELETE CASCADE
);

-- Index for faster lookup by learner
CREATE INDEX idx_session_learner_id
    ON session(learner_id);

-- Optional: index for activity-based queries
CREATE INDEX idx_session_activity_id
    ON session(activity_id);

-- Optional: index for status filtering
CREATE INDEX idx_session_status
    ON session(status);