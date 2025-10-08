-- Agam Organics - Complete Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users table with password support
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Addresses table with phone support
CREATE TABLE IF NOT EXISTS public.addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id),
    full_name TEXT NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'India',
    phone TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON COLUMN public.addresses.phone IS 'Contact phone number for this address';

-- Products table
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    discount_price DECIMAL(10,2),
    stock INTEGER NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,
    image_url TEXT NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cart table
CREATE TABLE IF NOT EXISTS public.cart (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id),
    product_id UUID NOT NULL REFERENCES public.products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id),
    address_id UUID NOT NULL REFERENCES public.addresses(id),
    status TEXT NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    payment_id TEXT,
    payment_status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders(id),
    product_id UUID NOT NULL REFERENCES public.products(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews table
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id),
    product_id UUID NOT NULL REFERENCES public.products(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Banners table for homepage carousel
CREATE TABLE IF NOT EXISTS public.banners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    subtitle TEXT,
    image_url TEXT NOT NULL,
    link_url TEXT,
    button_text TEXT DEFAULT 'Shop Now',
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_rating ON public.products(rating DESC);
CREATE INDEX IF NOT EXISTS idx_cart_user ON public.cart(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_user ON public.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON public.reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_banners_active_order ON public.banners(is_active, display_order);

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_addresses_updated_at 
    BEFORE UPDATE ON public.addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_updated_at 
    BEFORE UPDATE ON public.cart
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON public.orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at 
    BEFORE UPDATE ON public.reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_banners_updated_at 
    BEFORE UPDATE ON public.banners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RPC functions for stock management
CREATE OR REPLACE FUNCTION decrement_stock(product_id UUID, quantity INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE public.products
    SET stock = stock - quantity
    WHERE id = product_id AND stock >= quantity;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_stock(product_id UUID, quantity INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE public.products
    SET stock = stock + quantity
    WHERE id = product_id;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cart ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users
CREATE POLICY "Users can view own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- RLS Policies for addresses
CREATE POLICY "Users can view own addresses" ON public.addresses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own addresses" ON public.addresses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own addresses" ON public.addresses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own addresses" ON public.addresses
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for cart
CREATE POLICY "Users can view own cart" ON public.cart
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cart" ON public.cart
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cart" ON public.cart
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own cart" ON public.cart
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for orders
CREATE POLICY "Users can view own orders" ON public.orders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own orders" ON public.orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- RLS Policies for order items
CREATE POLICY "Users can view own order items" ON public.order_items
    FOR SELECT USING (EXISTS (
        SELECT 1 FROM public.orders
        WHERE orders.id = order_items.order_id
        AND orders.user_id = auth.uid()
    ));

-- RLS Policies for reviews
CREATE POLICY "Anyone can view reviews" ON public.reviews
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own reviews" ON public.reviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reviews" ON public.reviews
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reviews" ON public.reviews
    FOR DELETE USING (auth.uid() = user_id);

-- Insert sample banners
INSERT INTO public.banners (title, subtitle, image_url, link_url, button_text, display_order, is_active) VALUES
('Organic Masalas', 'Pure, Natural, and Authentic - Straight from Kerala Farms', '/static/images/banners/spices-banner.jpg', '/products?category=Spices', 'Shop Spices', 1, true),
('Health Mix Collection', 'Nutritious Blends for Your Daily Wellness', '/static/images/banners/health-banner.jpg', '/products?category=Health Foods', 'Explore Health Foods', 2, true),
('Traditional Spice Mixes', 'Authentic Recipes Passed Through Generations', '/static/images/banners/spice-mix-banner.jpg', '/products?category=Spice Mix', 'Browse Spice Mixes', 3, true)
ON CONFLICT DO NOTHING;

-- Insert sample products
INSERT INTO public.products (name, description, category, price, discount_price, stock, unit, image_url) VALUES
('Organic Turmeric Powder', 'Pure organic turmeric powder sourced from Kerala farms. Known for its anti-inflammatory properties, rich golden color, and authentic taste.', 'Spices', 250.00, 199.00, 100, '500g', '/static/images/products/turmeric.jpg'),
('Organic Chilli Powder', 'Fiery red chilli powder made from sun-dried organic chillies. Perfect for authentic Indian cuisine.', 'Spices', 180.00, 149.00, 150, '500g', '/static/images/products/chilli.jpg'),
('Organic Idli Podi', 'Traditional South Indian idli podi with a perfect blend of lentils and spices. Great with dosa, idli, and uttapam.', 'Spice Mix', 220.00, 189.00, 80, '250g', '/static/images/products/idli-podi.jpg'),
('Health Mix Powder', 'Nutritious mix of 12 grains and pulses including ragi, wheat, barley, and more. Perfect for a healthy breakfast drink.', 'Health Foods', 350.00, 299.00, 60, '1kg', '/static/images/products/health-mix.jpg')
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Sample products and banners have been inserted.';
    RAISE NOTICE 'Row Level Security policies have been configured.';
END $$;
