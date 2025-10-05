#!/bin/bash

# Agam Organics Backend Startup Script
# This script sets up SSL certificates and starts the FastAPI backend

# Get the directory where this script is located
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set SSL certificate path using the Supabase certificate
CERT_FILE="$(pwd)/app/resources/prod-ca.crt"
export SSL_CERT_FILE="$CERT_FILE"
export REQUESTS_CA_BUNDLE="$CERT_FILE"

echo "🔐 SSL Certificate: $SSL_CERT_FILE"
echo "🚀 Starting Agam Organics Backend..."
echo ""

# Start uvicorn
uvicorn main:app --reload --port 8000
