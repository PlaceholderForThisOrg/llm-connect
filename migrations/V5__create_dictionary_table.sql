CREATE TABLE dictionary(
    -- basic information using first entry
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL UNIQUE,
    phonetic TEXT,

    -- normalize using first entry
    phonetics JSONB,
    meanings JSONB,

    -- full entries
    raw_payload JSONB NOT NULL,

    last_fetched TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    source TEXT DEFAULT 'https://dictionaryapi.dev/'
);
