DROP TABLE messages;

CREATE TABLE message (
    id BIGSERIAL PRIMARY KEY NOT NULL,
    -- Not reference to a learner, but the scenario that learner joins
    -- user_id VARCHAR(50) REFERENCES learner(user_id) NOT NULL,
    scenario_id INTEGER REFERENCES scenario.scenario(id) NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);