#!/bin/bash

# Agam Organics - Quick Setup Script
# This script helps you set up the development environment quickly

echo "🌿 Agam Organics - Setup Script"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 is installed"
echo ""

# Generate secret keys
echo "🔐 Generating secret keys..."
BACKEND_SECRET=$(openssl rand -hex 32)
FLASK_SECRET=$(openssl rand -hex 24)
echo "✓ Secret keys generated"
echo ""

# Setup Backend
echo "🚀 Setting up Backend..."
cd backend || exit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Update secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-here-use-openssl-rand-hex-32/$BACKEND_SECRET/" .env
    else
        sed -i "s/your-secret-key-here-use-openssl-rand-hex-32/$BACKEND_SECRET/" .env
    fi
    
    echo "✓ Backend .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please update the following in backend/.env:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo "   - SUPABASE_SERVICE_KEY"
    echo ""
else
    echo "✓ Backend .env already exists"
fi

cd ..

# Setup Frontend
echo "🎨 Setting up Frontend..."
cd frontend || exit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Update secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-flask-secret-key-here/$FLASK_SECRET/" .env
    else
        sed -i "s/your-flask-secret-key-here/$FLASK_SECRET/" .env
    fi
    
    echo "✓ Frontend .env file created"
else
    echo "✓ Frontend .env already exists"
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Create a Supabase project at https://supabase.com"
echo "2. Run the SQL schema in backend/schema.sql in Supabase SQL Editor"
echo "3. Update backend/.env with your Supabase credentials"
echo "4. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "5. Start the frontend: cd frontend && source venv/bin/activate && python app.py"
echo ""
echo "📚 Documentation: See README.md for detailed instructions"
echo ""
