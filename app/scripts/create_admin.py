from app.app import app, db
from app.models.user import User
from app.config import Config
import sys

def create_admin_user():
    """Create admin user from environment variables"""
    with app.app_context():
        # Check if admin credentials are set
        if not Config.ADMIN_EMAIL or not Config.ADMIN_PASSWORD:
            print("Error: ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment variables")
            sys.exit(1)
            
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        if existing_admin:
            print(f"Admin user {Config.ADMIN_EMAIL} already exists")
            return
            
        # Create new admin user
        admin = User(
            email=Config.ADMIN_EMAIL,
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print(f"Created admin user: {Config.ADMIN_EMAIL}")

if __name__ == "__main__":
    create_admin_user() 