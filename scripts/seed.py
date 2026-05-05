"""
Seed script to create initial user and sample data for development.
Run: python scripts/seed.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password
from app.core.database import Base
from app.models.user import User
from app.models.brand import Brand

engine = create_engine(settings.DATABASE_URL_SYNC)


def seed():
    with Session(engine) as session:
        # Check if user already exists
        existing_user = session.query(User).filter_by(username="admin").first()
        if existing_user:
            print("Admin user already exists. Skipping seed.")
            return

        # Create admin user
        admin = User(
            username="admin",
            hashed_password=hash_password("admin123"),  # Change in production!
            is_active=True,
        )
        session.add(admin)
        session.flush()

        # Create sample brand
        brand = Brand(
            user_id=admin.id,
            name="My Content Brand",
            description="Personal content brand for YouTube and social media",
            niche="Technology & Productivity",
            target_audience="Indonesian tech enthusiasts aged 18-35",
        )
        session.add(brand)

        session.commit()
        print("Seed completed successfully!")
        print(f"  Admin user: admin / admin123")
        print(f"  Sample brand: {brand.name}")


if __name__ == "__main__":
    seed()
