-- drop the column of reference
ALTER TABLE srs.card
DROP COLUMN deck_id;

-- enable UUID creation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- drop constrain
ALTER TABLE srs.deck
DROP CONSTRAINT deck_pkey;

ALTER TABLE srs.deck
DROP COLUMN id;

-- change deck_id
ALTER TABLE srs.deck
ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid();

-- create reference again
ALTER TABLE srs.card
ADD COLUMN deck_id UUID NOT NULL REFERENCES srs.deck(id) ON DELETE CASCADE;