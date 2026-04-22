CREATE TABLE tag (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);

CREATE INDEX idx_tag_name ON tag(name);