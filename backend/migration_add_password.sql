-- Migration: Add password_hash column to users table and remove auth.users dependency
-- Run this in Supabase SQL Editor

-- First, drop the foreign key constraint if it exists
ALTER TABLE IF EXISTS public.users DROP CONSTRAINT IF EXISTS users_id_fkey;

-- Add password_hash column if it doesn't exist
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Update the id column to allow it to be auto-generated
ALTER TABLE public.users ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- For existing users without password_hash, set a placeholder
-- (You should reset these passwords properly)
UPDATE public.users 
SET password_hash = '$2b$12$placeholder.hash.for.existing.users' 
WHERE password_hash IS NULL OR password_hash = '';

-- Now make password_hash NOT NULL
ALTER TABLE public.users ALTER COLUMN password_hash SET NOT NULL;
