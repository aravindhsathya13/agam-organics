-- Update product images to use local static files
-- Run this in Supabase SQL Editor after placing images in frontend/static/images/products/

UPDATE public.products 
SET image_url = '/static/images/products/turmeric.jpg'
WHERE name = 'Organic Turmeric Powder';

UPDATE public.products 
SET image_url = '/static/images/products/chilli.jpg'
WHERE name = 'Organic Chilli Powder';

UPDATE public.products 
SET image_url = '/static/images/products/idli-podi.jpg'
WHERE name = 'Organic Idli Podi';

UPDATE public.products 
SET image_url = '/static/images/products/health-mix.jpg'
WHERE name = 'Health Mix Powder';

UPDATE public.products 
SET image_url = '/static/images/products/kulambu.jpg'
WHERE name = 'Organic Kulambu Powder';

UPDATE public.products 
SET image_url = '/static/images/products/coriander.jpg'
WHERE name = 'Organic Coriander Powder';

UPDATE public.products 
SET image_url = '/static/images/products/garam-masala.jpg'
WHERE name = 'Organic Garam Masala';

UPDATE public.products 
SET image_url = '/static/images/products/black-pepper.jpg'
WHERE name = 'Organic Black Pepper Powder';
