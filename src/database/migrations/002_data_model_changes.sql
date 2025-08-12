-- Migration: Data model changes
-- 1. Add call_sign to instructors
-- 2. Remove location_type and capacity from locations
-- 3. Remove total_students from course_sessions  
-- 4. Remove pay_eligible from instructor_assignments

BEGIN;

-- 1. Add call_sign field to instructors table
ALTER TABLE instructors ADD COLUMN call_sign VARCHAR(50);

-- 2. Remove location_type and capacity from locations table
ALTER TABLE locations DROP COLUMN IF EXISTS location_type;
ALTER TABLE locations DROP COLUMN IF EXISTS capacity;

-- 3. Remove total_students from course_sessions table
ALTER TABLE course_sessions DROP COLUMN IF EXISTS total_students;

-- 4. Remove pay_eligible from instructor_assignments table
ALTER TABLE instructor_assignments DROP COLUMN IF EXISTS pay_eligible;

COMMIT;