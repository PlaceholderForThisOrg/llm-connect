CREATE TABLE atomicpoint_tag (
    ap_id VARCHAR NOT NULL,
    tag_id VARCHAR NOT NULL,

    PRIMARY KEY (ap_id, tag_id),

    CONSTRAINT fk_atomicpoint
        FOREIGN KEY (ap_id)
        REFERENCES atomic_point(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_tag
        FOREIGN KEY (tag_id)
        REFERENCES tag(id)
        ON DELETE CASCADE
);