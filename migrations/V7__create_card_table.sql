CREATE TABLE srs.card (
    -- basic
    id SERIAL PRIMARY KEY,
    deck_id INT NOT NULL REFERENCES srs.deck(id) ON DELETE CASCADE,

    -- raw knowledge
    front TEXT NOT NULL,
    back TEXT NOT NULL,

    -- optional information
    dictionary_id INT REFERENCES dictionary(id) ON DELETE SET NULL,
    image_url TEXT NULL,
    audio_url TEXT NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);