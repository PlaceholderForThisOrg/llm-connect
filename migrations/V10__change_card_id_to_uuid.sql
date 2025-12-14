-- drop the primary constrain
ALTER TABLE srs.card
DROP CONSTRAINT card_pkey;

-- drop the column
ALTER TABLE srs.card
DROP COLUMN id;

-- add new id
ALTER TABLE srs.card
ADD COLUMN id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY;