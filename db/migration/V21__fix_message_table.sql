DROP TABLE message;

CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    conversation_id UUID NOT NULL,

    role TEXT NOT NULL,
    content TEXT NOT NULL,

    meta JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_message_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversation(id)
        ON DELETE CASCADE
);