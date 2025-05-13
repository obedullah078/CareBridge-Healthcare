#!/usr/bin/env python

"""
Seed script to create test doctors and patients in the database.
Run this script after initializing the database to have test accounts ready.
"""

import os

# Manually read the .env file
if os.path.exists('.env'):
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("Checking for existing users...")
        
        # Only seed if the database is empty or missing our test users
        doctor_user = User.query.filter_by(username='doctor').first()
        patient_user = User.query.filter_by(username='patient').first()
        
        if doctor_user and patient_user:
            print("Test users already exist in the database.")
            return
        
        print("Creating test users...")
        
        # Create test doctor
        if not doctor_user:
            doctor = User(
                username='doctor',
                email='doctor@example.com',
                password=generate_password_hash('doctor123'),
                full_name='Dr. John Smith',
                role='doctor',
                specialization='Cardiology',
                license_number='MD12345',
                phone='555-123-4567'
            )
            db.session.add(doctor)
            print("Created test doctor: username=doctor, password=doctor123")
        
        # Create test patient
        if not patient_user:
            patient = User(
                username='patient',
                email='patient@example.com',
                password=generate_password_hash('patient123'),
                full_name='Jane Doe',
                role='patient',
                phone='555-987-6543'
            )
            db.session.add(patient)
            print("Created test patient: username=patient, password=patient123")
        
        # Add more test users if needed
        # Create another doctor
        if not User.query.filter_by(username='doctor2').first():
            doctor2 = User(
                username='doctor2',
                email='doctor2@example.com',
                password=generate_password_hash('doctor123'),
                full_name='Dr. Sarah Johnson',
                role='doctor',
                specialization='Dermatology',
                license_number='MD67890',
                phone='555-222-3333'
            )
            db.session.add(doctor2)
            print("Created test doctor: username=doctor2, password=doctor123")
        
        # Create another patient
        if not User.query.filter_by(username='patient2').first():
            patient2 = User(
                username='patient2',
                email='patient2@example.com',
                password=generate_password_hash('patient123'),
                full_name='Bob Johnson',
                role='patient',
                phone='555-444-5555'
            )
            db.session.add(patient2)
            print("Created test patient: username=patient2, password=patient123")
        
        # Commit the changes to the database
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()