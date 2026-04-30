-- migrate atomic point to uuid
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- drop foreign key
ALTER TABLE mastery
DROP CONSTRAINT IF EXISTS fk_mastery_atomic_point;

ALTER TABLE atomicpoint_tag
DROP CONSTRAINT IF EXISTS fk_atomicpoint;

ALTER TABLE atomic_point_relation
DROP CONSTRAINT IF EXISTS fk_from_atomic_point;

ALTER TABLE atomic_point_relation
DROP CONSTRAINT IF EXISTS fk_to_atomic_point;

-- modify atomic point
ALTER TABLE atomic_point
ALTER COLUMN id TYPE UUID
USING id::uuid;


-- tag relation table
ALTER TABLE atomicpoint_tag
ALTER COLUMN ap_id TYPE UUID
USING ap_id::uuid;

-- graph relation table
ALTER TABLE atomic_point_relation
ALTER COLUMN from_id TYPE UUID
USING from_id::uuid;

ALTER TABLE atomic_point_relation
ALTER COLUMN to_id TYPE UUID
USING to_id::uuid;

-- mastery table
ALTER TABLE mastery
ALTER COLUMN atomic_point_id TYPE UUID
USING atomic_point_id::uuid;


ALTER TABLE atomicpoint_tag
ADD CONSTRAINT fk_atomicpoint
FOREIGN KEY (ap_id)
REFERENCES atomic_point(id)
ON DELETE CASCADE;

-- relation: from_id
ALTER TABLE atomic_point_relation
ADD CONSTRAINT fk_from_atomic_point
FOREIGN KEY (from_id)
REFERENCES atomic_point(id)
ON DELETE CASCADE;

-- relation: to_id
ALTER TABLE atomic_point_relation
ADD CONSTRAINT fk_to_atomic_point
FOREIGN KEY (to_id)
REFERENCES atomic_point(id)
ON DELETE CASCADE;

-- mastery → atomic_point
ALTER TABLE mastery
ADD CONSTRAINT fk_mastery_atomic_point
FOREIGN KEY (atomic_point_id)
REFERENCES atomic_point(id)
ON DELETE CASCADE;