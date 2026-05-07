CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE atomic_point_embedding (
    atomic_point_id UUID PRIMARY KEY
        REFERENCES atomic_point(id)
        ON DELETE CASCADE,
    embedding_model VARCHAR(64) NOT NULL,
    embedding_dims  SMALLINT NOT NULL,
    semantic_text   TEXT NOT NULL,
    content_hash    VARCHAR(64),
    embedding       vector(768) NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_atomic_point_embedding_hnsw
    ON atomic_point_embedding
    USING hnsw (embedding vector_cosine_ops);
