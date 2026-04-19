#!/bin/bash
set -e

echo "🏥 Starting Schedule API setup..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your database credentials before continuing."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d .venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

echo "✅ Setup complete!"
echo "🚀 Start the server with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "💚 Health check: http://localhost:8000/health"
