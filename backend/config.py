import os
from datetime import timedelta
from dotenv import load_dotenv
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    load_dotenv()
    
    # Get PostgreSQL connection URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set. PostgreSQL connection is required.")
    
    # Adjust PostgreSQL connection format if needed
    if db_url.startswith('postgres://'):
        # Heroku-style URL
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = "Lax"
    
    # Server configuration
    PORT = int(os.environ.get('PORT', 5000))