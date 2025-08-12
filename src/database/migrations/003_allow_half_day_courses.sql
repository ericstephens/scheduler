-- Migration: Allow half-day courses
-- Change duration_days from INTEGER to FLOAT to support half-day durations like 0.5, 1.5, etc.

BEGIN;

-- Change duration_days column type from INTEGER to FLOAT
-- PostgreSQL allows this conversion since all existing integers can be represented as floats
ALTER TABLE courses ALTER COLUMN duration_days TYPE REAL;

COMMIT;