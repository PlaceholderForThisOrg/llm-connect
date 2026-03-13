-- schema for SRS
CREATE SCHEMA srs;

-- deck table for SRS
CREATE TABLE srs.deck (
    id SERIAL PRIMARY KEY,
    -- can be null, decks belong to the system
    user_id VARCHAR(50) REFERENCES learner(user_id) ON DELETE CASCADE NULL,
    name TEXT NOT NULL,
    description TEXT NULL,
    is_shared BOOLEAN NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);