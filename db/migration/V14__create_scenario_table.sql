CREATE TABLE IF NOT EXISTS scenario.scenario (
    id SERIAL PRIMARY KEY NOT NULL,
    user_id VARCHAR(50) REFERENCES learner(user_id) ON DELETE CASCADE NULL,
    name TEXT NULL,
    sum_desc TEXT NULL
);