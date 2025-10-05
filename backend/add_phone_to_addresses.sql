-- Migration: Add phone field to addresses table
-- This allows each address to have its own contact number

-- Add phone column to addresses table
ALTER TABLE public.addresses 
ADD COLUMN IF NOT EXISTS phone TEXT;

-- Add comment
COMMENT ON COLUMN public.addresses.phone IS 'Contact phone number for this address';

-- You can run this in Supabase SQL Editor to update the schema
