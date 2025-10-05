-- Fix Row-Level Security for development
-- Run this in Supabase SQL Editor

-- Disable RLS temporarily for development (re-enable for production)
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.addresses DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.products DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.cart DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.cart_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews DISABLE ROW LEVEL SECURITY;

-- Alternative: Enable RLS with permissive policies (recommended for production)
-- Uncomment these lines if you want to keep RLS enabled:

/*
-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Allow anyone to insert (signup)
CREATE POLICY "Allow public signup" ON public.users
FOR INSERT WITH CHECK (true);

-- Allow users to read their own data
CREATE POLICY "Users can read own data" ON public.users
FOR SELECT USING (auth.uid() = id);

-- Allow users to update their own data
CREATE POLICY "Users can update own data" ON public.users
FOR UPDATE USING (auth.uid() = id);

-- Similar policies for other tables...
*/
