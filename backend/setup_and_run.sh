#!/bin/bash

# Exit on error
set -e

echo "===== Backend Setup and Deployment Script ====="
echo "Setting up environment in backend folder..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists, if not create a basic one
if [ ! -f ".env" ]; then
    echo "Creating .env file with default settings..."
    cat > .env << EOL
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/docdb
SECRET_KEY=production-secret-key
JWT_SECRET_KEY=production-jwt-secret-key
EOL
    echo ".env file created. Please update it with your actual database credentials."
    echo "Edit the .env file before proceeding."
    exit 1
fi

# Test database connection using test_db.py script
echo "Testing database connection..."
python test_db.py

# Check if test was successful (ignoring the specific exit code check that was unnecessarily complex)
if [ $? -ne 0 ]; then
    echo "Database connection failed. Please check your .env file and ensure PostgreSQL is running."
    exit 1
fi

# Check if tables exist using a simplified approach
echo "Checking if database tables exist..."
python - << EOF
import os
from sqlalchemy import inspect

# Load env vars
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key] = value

from app import db, create_app

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'users' in tables:
        print("Database tables already exist.")
        exit(0)
    else:
        print("Tables do not exist. Need to create them.")
        exit(2)
EOF

# Capture the exit code
DB_STATUS=$?

# If tables don't exist (exit code 2), run create_db.py
if [ $DB_STATUS -eq 2 ]; then
    echo "Creating database tables..."
    python create_db.py
    
    echo "Would you like to seed the database with sample data? (y/n)"
    read -r answer
    if [ "$answer" == "y" ] || [ "$answer" == "Y" ]; then
        echo "Seeding database with sample data..."
        python seed_db.py
    fi
fi

# Start the server
echo "Starting the Flask application server..."
export FLASK_APP=run.py
export FLASK_ENV=production

# Check if port is provided as argument
if [ -n "$1" ]; then
    export PORT=$1
fi

echo "Server is starting on port ${PORT:-5001}..."
python run.py