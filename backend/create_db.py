#!/usr/bin/env python

"""
Create/reset database script.
Use this to initialize the database with tables that match our models.
"""

import os
import pathlib

# Manually read the .env file
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key] = value

# Now import the app modules after environment variables are loaded
from app import create_app, db

def create_database():
    # Create a Flask app context
    app = create_app()
    
    # Print which database we're using
    print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    with app.app_context():
        print("Dropping all tables (if they exist)...")
        db.drop_all()
        
        print("Creating all tables based on defined models...")
        db.create_all()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    create_database()