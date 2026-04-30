-- Table to represent the relationship between atomic points

CREATE TABLE atomic_point_relation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    from_id VARCHAR NOT NULL,
    to_id VARCHAR NOT NULL,

    relation_type VARCHAR(50) NOT NULL,

    weight DOUBLE PRECISION DEFAULT 1.0,

    created_at TIMESTAMP DEFAULT NOW(),

    -- foreignkey to atomic_point
    CONSTRAINT fk_from_atomic_point
        FOREIGN KEY (from_id)
        REFERENCES atomic_point(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_to_atomic_point
        FOREIGN KEY (to_id)
        REFERENCES atomic_point(id)
        ON DELETE CASCADE
);

ALTER TABLE atomic_point_relation
ADD CONSTRAINT uq_atomic_relation
UNIQUE (from_id, to_id, relation_type);

CREATE INDEX idx_atomic_point_relation_from
ON atomic_point_relation(from_id);

CREATE INDEX idx_atomic_point_relation_to
ON atomic_point_relation(to_id);

CREATE INDEX idx_atomic_point_relation_type
ON atomic_point_relation(relation_type);