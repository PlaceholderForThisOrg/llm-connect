CREATE TABLE IF NOT EXISTS vocab (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL UNIQUE,
    phonetic TEXT,
    phonetics JSONB,
    meanings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
