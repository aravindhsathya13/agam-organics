# Agam Organics - E-Commerce Platform

A modern e-commerce platform for selling organic masala products, inspired by Meesho's design and user experience.

## 🌿 About Agam Organics

Agam Organics specializes in authentic organic masala products including:

- Turmeric Powder
- Chilli Powder
- Idli Podi
- Health Mix
- Kulambu Powder

## 🏗️ Architecture

### Backend (FastAPI)

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT-based authentication
- **Payment Integration**: Ready for Razorpay/Stripe integration
- **API Documentation**: Auto-generated Swagger UI at `/docs`

### Frontend (Flask + Jinja2)

- **Framework**: Flask with Jinja2 templates
- **Styling**: Custom CSS with dark green theme
- **JavaScript**: Vanilla JS for interactivity (no Node.js required)
- **Design**: Meesho-inspired responsive design

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account (free tier works)
- pip (Python package manager)

## 🚀 Quick Start

### 1. Setup Supabase

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy your project URL and API keys (found in Settings > API)
4. The database tables will be created automatically on first run

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Create .env file with your Supabase credentials
cp .env.example .env
# Edit .env and add your Supabase URL and keys

# Run the backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env if needed (default backend URL is already set)

# Run the frontend
python app.py
```

Frontend will be available at: `http://localhost:5000`

## 📁 Project Structure

```
agam-organics/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core functionality (config, security)
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   └── db/           # Database operations
│   ├── main.py           # Application entry point
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/             # Flask frontend
    ├── static/           # CSS, JS, images
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── templates/        # HTML templates
    ├── app.py           # Flask application
    ├── requirements.txt
    └── .env.example
```

## 🔑 Key Features

### Implemented

- ✅ User authentication (signup, login, logout)
- ✅ Product catalog with search and filters
- ✅ Product details with images and descriptions
- ✅ Shopping cart functionality
- ✅ User profile management
- ✅ Order management
- ✅ Product reviews and ratings
- ✅ Responsive design (mobile & desktop)
- ✅ Dark green theme (Agam Organics branding)

### Ready for Integration

- 🔄 Payment gateway (Razorpay/Stripe)
- 🔄 Email notifications
- 🔄 Order tracking
- 🔄 Admin dashboard

## 🎨 Design System

- **Primary Color**: Dark Green (#1B5E20, #2E7D32)
- **Accent Color**: Light Green (#66BB6A)
- **Typography**: Similar to Meesho (System fonts for optimal performance)
- **Layout**: Grid-based responsive design

## 🔐 Security Features

- JWT-based authentication
- Password hashing (bcrypt)
- CORS configuration
- SQL injection prevention (parameterized queries)
- XSS protection
- CSRF tokens for forms

## 📝 API Endpoints

### Authentication

- POST `/api/auth/signup` - User registration
- POST `/api/auth/login` - User login
- POST `/api/auth/refresh` - Refresh token

### Products

- GET `/api/products` - List all products
- GET `/api/products/{id}` - Get product details
- GET `/api/products/search` - Search products

### Cart

- GET `/api/cart` - Get user cart
- POST `/api/cart/add` - Add item to cart
- PUT `/api/cart/update` - Update cart item
- DELETE `/api/cart/remove/{id}` - Remove item

### Orders

- POST `/api/orders` - Create order
- GET `/api/orders` - Get user orders
- GET `/api/orders/{id}` - Get order details

### User Profile

- GET `/api/profile` - Get user profile
- PUT `/api/profile` - Update user profile

### Reviews

- POST `/api/reviews` - Add product review
- GET `/api/reviews/{product_id}` - Get product reviews

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Check API health
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Backend won't start

- Ensure Supabase credentials are correct in `.env`
- Check if port 8000 is available
- Verify Python version (3.8+)

### Frontend won't start

- Check if backend is running
- Ensure port 5000 is available
- Verify backend URL in frontend `.env`

### Database connection issues

- Verify Supabase project is active
- Check API keys and project URL
- Ensure internet connection

## 📞 Support

For issues or questions, please check the code comments or refer to:

- FastAPI docs: https://fastapi.tiangolo.com/
- Supabase docs: https://supabase.com/docs
- Flask docs: https://flask.palletsprojects.com/

## 📄 License

Proprietary - Agam Organics © 2025
