-- Agam Organics - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    date_of_birth DATE,
    date_of_anniversary DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Addresses table
CREATE TABLE IF NOT EXISTS public.addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    pincode TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    discount_price DECIMAL(10,2),
    stock INTEGER NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,
    image_url TEXT,
    additional_images TEXT[],
    rating DECIMAL(3,2) DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cart table
CREATE TABLE IF NOT EXISTS public.cart (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_address JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES public.orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id),
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Reviews table
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title TEXT NOT NULL,
    comment TEXT NOT NULL,
    images TEXT[],
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_rating ON public.products(rating DESC);
CREATE INDEX IF NOT EXISTS idx_cart_user ON public.cart(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_user ON public.orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders(status);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON public.reviews(product_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON public.products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_updated_at BEFORE UPDATE ON public.cart
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON public.orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RPC functions for stock management
CREATE OR REPLACE FUNCTION decrement_stock(product_id UUID, quantity INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE public.products
    SET stock = stock - quantity
    WHERE id = product_id;
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

CREATE POLICY "Users can view own order items" ON public.order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.orders
            WHERE orders.id = order_items.order_id
            AND orders.user_id = auth.uid()
        )
    );

-- RLS Policies for reviews
CREATE POLICY "Anyone can view reviews" ON public.reviews
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own reviews" ON public.reviews
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reviews" ON public.reviews
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reviews" ON public.reviews
    FOR DELETE USING (auth.uid() = user_id);

-- Products table is publicly readable (no RLS needed for SELECT)
-- But you can add policies for INSERT/UPDATE/DELETE for admin users

-- Insert sample products
INSERT INTO public.products (name, description, category, price, discount_price, stock, unit, image_url) VALUES
('Organic Turmeric Powder', 'Pure organic turmeric powder sourced from Kerala farms. Known for its anti-inflammatory properties, rich golden color, and authentic taste. Perfect for daily cooking and health benefits.', 'Spices', 250.00, 199.00, 100, '500g', 'https://via.placeholder.com/800x800/1B5E20/FFFFFF?text=Turmeric'),
('Organic Chilli Powder', 'Fiery red chilli powder made from sun-dried organic chillies. Perfect for authentic Indian cuisine. Rich in vitamins and adds the perfect kick to your dishes.', 'Spices', 180.00, 149.00, 150, '500g', 'https://via.placeholder.com/800x800/DC143C/FFFFFF?text=Chilli'),
('Organic Idli Podi', 'Traditional South Indian idli podi with a perfect blend of lentils and spices. Great with dosa, idli, and uttapam. Made from authentic recipe passed through generations.', 'Spice Mix', 220.00, 189.00, 80, '250g', 'https://via.placeholder.com/800x800/8B4513/FFFFFF?text=Idli+Podi'),
('Health Mix Powder', 'Nutritious mix of 12 grains and pulses including ragi, wheat, barley, and more. Perfect for a healthy breakfast drink for all ages. Rich in protein and fiber.', 'Health Foods', 350.00, 299.00, 60, '1kg', 'https://via.placeholder.com/800x800/228B22/FFFFFF?text=Health+Mix'),
('Organic Kulambu Powder', 'Authentic Tamil Nadu style kulambu powder with traditional spices. Makes delicious sambar and kuzhambu. The secret to restaurant-style South Indian curries.', 'Spice Mix', 200.00, 169.00, 90, '250g', 'https://via.placeholder.com/800x800/CD853F/FFFFFF?text=Kulambu'),
('Organic Coriander Powder', 'Fresh ground coriander powder from organic farms. Essential for Indian cooking with a distinct aroma and taste. Stone ground to preserve natural oils.', 'Spices', 160.00, 135.00, 120, '500g', 'https://via.placeholder.com/800x800/2E7D32/FFFFFF?text=Coriander'),
('Organic Garam Masala', 'Premium blend of whole spices roasted and ground to perfection. Adds warmth and depth to your dishes. Made fresh in small batches.', 'Spice Mix', 280.00, 239.00, 70, '250g', 'https://via.placeholder.com/800x800/8B4513/FFFFFF?text=Garam+Masala'),
('Organic Black Pepper Powder', 'Freshly ground organic black pepper from Malabar region. Known as the king of spices. Perfect for seasoning and health benefits.', 'Spices', 320.00, 279.00, 50, '250g', 'https://via.placeholder.com/800x800/000000/FFFFFF?text=Pepper')
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Sample products have been inserted.';
    RAISE NOTICE 'Row Level Security policies have been configured.';
END $$;
