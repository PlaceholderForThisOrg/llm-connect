CREATE TABLE IF NOT EXISTS scenario.scenario_template (
    id BIGSERIAL PRIMARY KEY,
    metadata JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sum_desc TEXT NULL
);