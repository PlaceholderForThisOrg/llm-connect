ALTER TABLE session
ADD COLUMN conversation_id UUID;

-- Add foreign key constraint
ALTER TABLE session
ADD CONSTRAINT fk_session_conversation
FOREIGN KEY (conversation_id)
REFERENCES conversation(id)
ON DELETE SET NULL;
-- unique to ensure one session, is linked with one conversation
CREATE UNIQUE INDEX ux_session_conversation_id
ON session(conversation_id);