-- BKT added

ALTER TABLE atomic_point
ADD COLUMN p_init DOUBLE PRECISION DEFAULT 0.2 NOT NULL,
ADD COLUMN p_learn DOUBLE PRECISION DEFAULT 0.1 NOT NULL,
ADD COLUMN p_guess DOUBLE PRECISION DEFAULT 0.2 NOT NULL,
ADD COLUMN p_slip DOUBLE PRECISION DEFAULT 0.1 NOT NULL;

-- simple constraints for parameters
ALTER TABLE atomic_point
ADD CONSTRAINT chk_p_init_range CHECK (p_init >= 0 AND p_init <= 1),
ADD CONSTRAINT chk_p_learn_range CHECK (p_learn >= 0 AND p_learn <= 1),
ADD CONSTRAINT chk_p_guess_range CHECK (p_guess >= 0 AND p_guess <= 1),
ADD CONSTRAINT chk_p_slip_range CHECK (p_slip >= 0 AND p_slip <= 1);