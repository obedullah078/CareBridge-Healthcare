# Medical Appointment System - Backend

This is the backend API for the Medical Appointment System, a web application that allows patients to book appointments with doctors.

## Technology Stack

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: Authentication with JWT tokens
- **PostgreSQL**: Database
- **Flask-Migrate**: Database migrations
- **Flask-CORS**: Cross-Origin Resource Sharing

## Features

- User authentication and authorization (patients and doctors)
- JWT token-based authentication
- Doctor availability management
- Appointment booking and management
- RESTful API endpoints

## API Endpoints

### Authentication
- `POST /api/register`: Register a new user (patient or doctor)
- `POST /api/login`: Login and get JWT tokens
- `POST /api/refresh`: Refresh access token
- `GET /api/user`: Get current user details
- `POST /api/logout`: Logout (client-side token removal)

### Doctors
- `GET /api/doctors`: Get all doctors
- `GET /api/doctors/<id>/availability`: Get a doctor's availability
- `POST /api/doctors/<id>/availability`: Add or update a doctor's availability

### Appointments
- `POST /api/appointments`: Create a new appointment
- `GET /api/appointments/doctor`: Get all appointments for the current doctor
- `GET /api/appointments/patient`: Get all appointments for the current patient
- `PUT /api/appointments/<id>`: Update an appointment

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a `.env` file):
   ```
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   DATABASE_URL=postgresql://username:password@hostname:port/database
   ```

4. Initialize the database:
   ```
   flask db upgrade
   ```

5. Run the development server:
   ```
   python run.py
   ```

## Database Schema

- **Users**: Stores user information (doctors and patients)
- **Appointments**: Stores appointment details
- **Availabilities**: Stores doctors' available time slots

## Frontend Repository

The frontend code for this application is available at: [Medical Appointment System Frontend](https://github.com/VivekMalipatel/shoaib-frontend)