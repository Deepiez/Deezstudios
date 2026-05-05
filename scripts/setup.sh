#!/bin/bash
# AI Content Automation Studio - Development Setup Script

set -e

echo "=== AI Content Automation Studio - Setup ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your actual configuration values."
fi

# Start Docker services
echo ""
echo "Starting Docker services (PostgreSQL, Redis, MinIO)..."
docker compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker compose exec postgres pg_isready -U studio_user -d content_studio > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Setup Python virtual environment
echo ""
echo "Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
echo ""
echo "Running database migrations..."
alembic upgrade head

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Services running:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - MinIO: localhost:9000 (console: localhost:9001)"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
