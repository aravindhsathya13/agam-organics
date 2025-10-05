# 🖼️ Product Images Setup Guide

## Current Status
The products are using placeholder URLs. Follow these steps to add real images.

## 📁 Where to Place Images
Put your product images in this folder: `frontend/static/images/products/`

## Required Images (8 files):
1. `turmeric.jpg` - Organic Turmeric Powder
2. `chilli.jpg` - Organic Chilli Powder  
3. `idli-podi.jpg` - Organic Idli Podi
4. `health-mix.jpg` - Health Mix Powder
5. `kulambu.jpg` - Organic Kulambu Powder
6. `coriander.jpg` - Organic Coriander Powder
7. `garam-masala.jpg` - Organic Garam Masala
8. `black-pepper.jpg` - Organic Black Pepper Powder

## 🔄 Update Database URLs

After placing images, run this SQL in Supabase SQL Editor:
(File location: `backend/update_product_images.sql`)

```sql
UPDATE public.products SET image_url = '/static/images/products/turmeric.jpg' WHERE name = 'Organic Turmeric Powder';
UPDATE public.products SET image_url = '/static/images/products/chilli.jpg' WHERE name = 'Organic Chilli Powder';
UPDATE public.products SET image_url = '/static/images/products/idli-podi.jpg' WHERE name = 'Organic Idli Podi';
UPDATE public.products SET image_url = '/static/images/products/health-mix.jpg' WHERE name = 'Health Mix Powder';
UPDATE public.products SET image_url = '/static/images/products/kulambu.jpg' WHERE name = 'Organic Kulambu Powder';
UPDATE public.products SET image_url = '/static/images/products/coriander.jpg' WHERE name = 'Organic Coriander Powder';
UPDATE public.products SET image_url = '/static/images/products/garam-masala.jpg' WHERE name = 'Organic Garam Masala';
UPDATE public.products SET image_url = '/static/images/products/black-pepper.jpg' WHERE name = 'Organic Black Pepper Powder';
```

## 🎨 Free Image Resources

- **Unsplash:** https://unsplash.com/s/photos/spices
- **Pexels:** https://pexels.com/search/organic-spices
- **Pixabay:** https://pixabay.com/images/search/turmeric

## ✅ Test
After setup, visit http://localhost:5000 and images should appear!
