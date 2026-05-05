#!/bin/bash
# ===========================================
# AI Content Automation Studio - Deploy Script
# Run on VPS to deploy or update the application
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== AI Content Studio - Deployment ==="
echo "Project: $PROJECT_DIR"
echo ""

# Check .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: .env file not found!"
    echo "Copy .env.production to .env and fill in your values:"
    echo "  cp .env.production .env"
    echo "  nano .env"
    exit 1
fi

# Pull latest code (if git repo)
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Pulling latest code..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

# Build and start services
echo ""
echo "Building Docker images..."
cd "$PROJECT_DIR"
docker compose -f docker-compose.prod.yml build

echo ""
echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

# Wait for backend to be healthy
echo ""
echo "Waiting for backend to be ready..."
for i in $(seq 1 30); do
    if docker compose -f docker-compose.prod.yml exec backend curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "WARNING: Backend health check timed out"
    fi
    sleep 2
done

# Run database migrations
echo ""
echo "Running database migrations..."
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create initial admin user if needed
echo ""
echo "Checking seed data..."
docker compose -f docker-compose.prod.yml exec backend python -c "
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User

engine = create_engine(settings.DATABASE_URL_SYNC)
with Session(engine) as db:
    user = db.execute(select(User).limit(1)).scalar_one_or_none()
    if not user:
        from app.core.security import hash_password
        admin = User(username='admin', hashed_password=hash_password('admin123'), is_active=True)
        db.add(admin)
        db.commit()
        print('Admin user created: admin / admin123')
        print('IMPORTANT: Change the password after first login!')
    else:
        print('Users already exist, skipping seed.')
" 2>/dev/null || echo "Seed check skipped (run manually if needed)"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Services:"
docker compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Access:"
echo "  App:     http://$(hostname -I | awk '{print $1}')"
echo "  API:     http://$(hostname -I | awk '{print $1}')/api/v1"
echo "  Docs:    http://$(hostname -I | awk '{print $1}')/docs"
echo "  MinIO:   http://$(hostname -I | awk '{print $1}'):9001"
echo ""
echo "Logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "Stop:"
echo "  docker compose -f docker-compose.prod.yml down"
echo ""
