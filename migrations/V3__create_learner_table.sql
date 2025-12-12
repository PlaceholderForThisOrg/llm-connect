CREATE TABLE IF NOT EXISTS learner (
    user_id VARCHAR(50) PRIMARY KEY NOT NULL,
    name VARCHAR(100),
    nickname VARCHAR(100),
    avatar_url TEXT,
    date_of_birth DATE,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
