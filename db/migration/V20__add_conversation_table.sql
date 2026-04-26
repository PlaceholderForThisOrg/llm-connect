CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    learner_id VARCHAR NOT NULL,

    type VARCHAR NULL,
    title VARCHAR NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ad TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_conversation_learner
        FOREIGN KEY (learner_id)
        REFERENCES learner(user_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_conversation_learner_id
    ON conversation (learner_id);

CREATE INDEX idx_conversation_created_at
    ON conversation (created_at DESC);