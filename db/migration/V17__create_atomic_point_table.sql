CREATE TABLE atomic_point (
    id VARCHAR PRIMARY KEY,
    type VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    examples TEXT,
    level VARCHAR NOT NULL,
    popularity FLOAT
);