import os
import secrets
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

class Config:
    # Generate a secret key if it doesn't exist
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        # If no environment variable, try to read from file
        secret_file = os.path.join(os.path.dirname(__file__), 'secret_key')
        try:
            if os.path.exists(secret_file):
                with open(secret_file, 'r') as f:
                    SECRET_KEY = f.read().strip()
            if not SECRET_KEY:  # File empty or doesn't exist
                SECRET_KEY = secrets.token_hex(32)
                # Try to save it for future runs
                try:
                    with open(secret_file, 'w') as f:
                        f.write(SECRET_KEY)
                except:
                    pass  # Fail silently if we can't write the file
        except:
            SECRET_KEY = secrets.token_hex(32)  # Final fallback
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin user configuration
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join('app', 'uploads')
    SOURCE_FOLDER = os.path.join('data', 'source')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # Twilio configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # SMS configuration
    SMS_RATE_LIMIT = int(os.getenv('SMS_RATE_LIMIT', '1'))  # messages per second
    SMS_MAX_LENGTH = int(os.getenv('SMS_MAX_LENGTH', '1600'))  # characters
    SMS_BATCH_SIZE = int(os.getenv('SMS_BATCH_SIZE', '50'))  # messages per batch 