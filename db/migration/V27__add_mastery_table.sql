-- mastery table

CREATE TABLE mastery (
    learner_id TEXT NOT NULL,
    atomic_point_id TEXT NOT NULL,

    -- probability of mastery
    p_L DOUBLE PRECISION NOT NULL,

    -- for tracking progress
    attempts INTEGER NOT NULL DEFAULT 0,
    correct_attempts INTEGER NOT NULL DEFAULT 0,

    -- for tracking time
    first_attempt_at TIMESTAMP,
    last_attempt_at TIMESTAMP,

    -- for showing the level
    mastery_level TEXT,

    -- composite key learner-atomic point
    PRIMARY KEY (learner_id, atomic_point_id),

    -- constraint foreign keys
    CONSTRAINT fk_mastery_learner
        FOREIGN KEY (learner_id)
        REFERENCES learner(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_mastery_atomic_point
        FOREIGN KEY (atomic_point_id)
        REFERENCES atomic_point(id)
        ON DELETE CASCADE,

    -- constraint for the probability
    CONSTRAINT chk_p_L_range CHECK (p_L >= 0 AND p_L <= 1)
);