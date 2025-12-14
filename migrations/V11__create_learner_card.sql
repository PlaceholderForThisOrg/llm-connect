-- core SRS
CREATE TABLE srs.learner_card (
    -- ref
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES learner(user_id),
    card_id UUID NOT NULL REFERENCES srs.card(id),
    state TEXT CHECK (state IN ('NEW', 'LEARNING', 'REVIEW')) DEFAULT 'NEW',

    -- core SRS logic
    interval INT DEFAULT 0,
    repetitions INT DEFAULT 0,
    ease_factor FLOAT DEFAULT 2.5, -- SM-2
    next_review TIMESTAMP,
    last_reviewed TIMESTAMP,
    
    -- each learner is learner different cards
    UNIQUE(user_id, card_id)
);