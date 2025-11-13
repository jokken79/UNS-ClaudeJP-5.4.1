"""
Create default admin user for LolaAppJp

Usage:
    python scripts/create_admin_user.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.models import User, UserRole


def create_admin():
    """Create default admin user"""
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()

        if existing_admin:
            print("⚠️  Admin user already exists")
            print(f"   Username: admin")
            print(f"   Role: {existing_admin.role.value}")

            # Update password if needed
            update = input("\nUpdate password to 'admin123'? (y/n): ").lower()
            if update == 'y':
                existing_admin.hashed_password = get_password_hash("admin123")
                db.commit()
                print("✅ Admin password updated successfully!")
            else:
                print("❌ Skipped password update")

            return

        # Create new admin user
        admin = User(
            username="admin",
            email="admin@lolaappjp.com",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@lolaappjp.com")
        print(f"   Role: {admin.role.value}")
        print("\n⚠️  IMPORTANT: Change this password after first login!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  LolaAppJp - Create Admin User")
    print("=" * 60)
    print()

    create_admin()

    print()
    print("=" * 60)
