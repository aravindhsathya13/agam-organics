"""
Database initialization - Creates tables if they don't exist
"""
from app.db.database import get_admin_db


async def init_database():
    """
    Initialize database tables.
    Note: For Supabase, tables should ideally be created via Supabase dashboard or migrations.
    This function provides the SQL schema for reference.
    """
    db = get_admin_db()
    
    # SQL for creating tables (run these in Supabase SQL Editor)
    tables_sql = """
    -- Users table (extends Supabase auth.users)
    CREATE TABLE IF NOT EXISTS public.users (
        id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
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

    -- Indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
    CREATE INDEX IF NOT EXISTS idx_cart_user ON public.cart(user_id);
    CREATE INDEX IF NOT EXISTS idx_orders_user ON public.orders(user_id);
    CREATE INDEX IF NOT EXISTS idx_reviews_product ON public.reviews(product_id);

    -- Insert sample products
    INSERT INTO public.products (name, description, category, price, discount_price, stock, unit, image_url) VALUES
    ('Organic Turmeric Powder', 'Pure organic turmeric powder from Kerala farms. Known for its anti-inflammatory properties and rich golden color.', 'Spices', 250.00, 199.00, 100, '500g', '/static/images/products/turmeric.jpg'),
    ('Organic Chilli Powder', 'Fiery red chilli powder made from sun-dried organic chillies. Perfect for authentic Indian cuisine.', 'Spices', 180.00, 149.00, 150, '500g', '/static/images/products/chilli.jpg'),
    ('Organic Idli Podi', 'Traditional South Indian idli podi with a perfect blend of lentils and spices. Great with dosa and idli.', 'Spice Mix', 220.00, 189.00, 80, '250g', '/static/images/products/idli-podi.jpg'),
    ('Health Mix Powder', 'Nutritious mix of 12 grains and pulses. Perfect for a healthy breakfast drink for all ages.', 'Health Foods', 350.00, 299.00, 60, '1kg', '/static/images/products/health-mix.jpg'),
    ('Organic Kulambu Powder', 'Authentic Tamil Nadu style kulambu powder with traditional spices. Makes delicious sambar and kuzhambu.', 'Spice Mix', 200.00, 169.00, 90, '250g', '/static/images/products/kulambu.jpg')
    ON CONFLICT DO NOTHING;
    """
    
    print("Database initialization SQL schema prepared.")
    print("\n" + "="*80)
    print("IMPORTANT: Run the above SQL in your Supabase SQL Editor to create tables.")
    print("You can find the SQL Editor at: Project Settings > SQL Editor")
    print("="*80 + "\n")
    
    # Note: Supabase requires tables to be created via SQL editor or migrations
    # The actual table creation should be done manually in Supabase dashboard
    return True
