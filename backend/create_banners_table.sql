-- Create banners table for homepage carousel
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

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_banners_active_order ON public.banners(is_active, display_order);

-- Add trigger for updated_at
CREATE TRIGGER update_banners_updated_at BEFORE UPDATE ON public.banners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample banners
INSERT INTO public.banners (title, subtitle, image_url, link_url, button_text, display_order, is_active) VALUES
('Organic Masalas', 'Pure, Natural, and Authentic - Straight from Kerala Farms', 'https://images.unsplash.com/photo-1596040033229-a0b3b46ecb84?w=1920&h=600&fit=crop', '/products?category=Spices', 'Shop Spices', 1, true),
('Health Mix Collection', 'Nutritious Blends for Your Daily Wellness', 'https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=1920&h=600&fit=crop', '/products?category=Health Foods', 'Explore Health Foods', 2, true),
('Traditional Spice Mixes', 'Authentic Recipes Passed Through Generations', 'https://images.unsplash.com/photo-1599909533652-d526b0df8fa9?w=1920&h=600&fit=crop', '/products?category=Spice Mix', 'Browse Spice Mixes', 3, true)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Banners table created successfully!';
    RAISE NOTICE 'Sample banners have been inserted.';
END $$;
