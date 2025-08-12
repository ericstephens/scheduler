-- Migration: Rename class_sessions table to course_sessions
-- This migration renames the class_sessions table to course_sessions to align with the model naming

BEGIN;

-- Rename the table
ALTER TABLE class_sessions RENAME TO course_sessions;

-- Update foreign key references in session_days table
-- Note: The foreign key constraint name may vary, this is a generic approach
DO $$
DECLARE
    constraint_name text;
BEGIN
    -- Find the foreign key constraint name
    SELECT conname INTO constraint_name
    FROM pg_constraint 
    WHERE conrelid = 'session_days'::regclass 
    AND confrelid = 'course_sessions'::regclass;
    
    -- Drop and recreate the foreign key constraint if it exists
    IF constraint_name IS NOT NULL THEN
        EXECUTE 'ALTER TABLE session_days DROP CONSTRAINT ' || quote_ident(constraint_name);
        ALTER TABLE session_days ADD CONSTRAINT session_days_session_id_fkey 
            FOREIGN KEY (session_id) REFERENCES course_sessions(id);
    END IF;
END $$;

COMMIT;