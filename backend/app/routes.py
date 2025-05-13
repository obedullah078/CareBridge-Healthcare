from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Appointment, Availability
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from datetime import datetime, timedelta
import pytz  # Add pytz for timezone handling

bp = Blueprint('api', __name__)

# Set Chicago timezone for consistent handling with frontend
CHICAGO_TZ = pytz.timezone('America/Chicago')

# Helper functions for timezone handling
def utc_to_chicago(utc_dt):
    """Convert UTC datetime to Chicago timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(CHICAGO_TZ)

def chicago_to_utc(chicago_dt):
    """Convert Chicago datetime to UTC timezone"""
    if chicago_dt.tzinfo is None:
        chicago_dt = CHICAGO_TZ.localize(chicago_dt)
    return chicago_dt.astimezone(pytz.utc)

def parse_iso_in_chicago(iso_string):
    """Parse ISO string into a UTC datetime, interpreting offsets correctly and assuming Chicago local time when no offset is present"""
    # Handle ISO strings ending with 'Z' (UTC)
    if iso_string.endswith('Z'):
        # Convert 'Z' to +00:00 for fromisoformat
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        # Already in UTC, return as-is
        return dt.astimezone(pytz.utc)
    # Parse with possible offset
    dt = datetime.fromisoformat(iso_string)
    # If no tzinfo, assume it's in Chicago local time
    if dt.tzinfo is None:
        dt = CHICAGO_TZ.localize(dt)
    # Convert to UTC for storage
    return dt.astimezone(pytz.utc)

# Create a separate blueprint for availability routes
availability_routes = Blueprint('availability', __name__)
bp.register_blueprint(availability_routes)

# Create a separate blueprint for profile routes - FIX: removed url_prefix to match API_ENDPOINTS.profile
profile_routes = Blueprint('profile', __name__)
bp.register_blueprint(profile_routes)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    
    # Check required fields
    if not all(k in data for k in ('username', 'email', 'password', 'role', 'fullName')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role'],
        full_name=data['fullName'],
        specialization=data.get('specialization', ''),
        license_number=data.get('licenseNumber', ''),
        phone=data.get('phone', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Set session cookie
    session['user_id'] = user.id
    
    # Create response with user data and tokens
    user_data = user.to_dict()
    response_data = {
        **user_data,
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    
    # Set JWT cookies
    resp = jsonify(response_data)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    
    return resp, 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user is None or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Set session cookie
    session['user_id'] = user.id
    
    # Create response with user data and tokens
    user_data = user.to_dict()
    response_data = {
        **user_data,
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    
    # Set JWT cookies
    resp = jsonify(response_data)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    
    return resp, 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    
    return jsonify({
        'access_token': access_token
    }), 200

@bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/logout', methods=['POST'])
def logout():
    # Clear session
    session.clear()
    
    # Clear JWT cookies
    resp = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(resp)
    
    return resp, 200

@bp.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = User.query.filter_by(role='doctor').all()
    return jsonify([doctor.to_dict() for doctor in doctors]), 200

@availability_routes.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
def get_doctor_availability(doctor_id):
    availabilities = Availability.query.filter_by(doctor_id=doctor_id).all()
    return jsonify([a.to_dict() for a in availabilities]), 200

@availability_routes.route('/doctors/<int:doctor_id>/availability', methods=['POST'])
def add_doctor_availability(doctor_id):
    # Get user from session instead of JWT
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user = User.query.get(user_id)
    
    if not user or user.role != 'doctor' or user.id != doctor_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    
    if not all(k in data for k in ('dayOfWeek', 'startTime', 'endTime', 'isAvailable')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # If date is provided, we're dealing with a specific date availability
    specific_date = None
    if 'date' in data and data['date']:
        try:
            specific_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Check if availability already exists for this specific date
        existing = Availability.query.filter_by(
            doctor_id=doctor_id, 
            date=specific_date
        ).first()
    else:
        # Check if availability already exists for this day of week
        existing = Availability.query.filter_by(
            doctor_id=doctor_id, 
            day_of_week=data['dayOfWeek'],
            date=None  # No specific date
        ).first()
    
    if existing:
        # Update existing availability
        existing.start_time = data['startTime']
        existing.end_time = data['endTime']
        existing.is_available = data['isAvailable']
        db.session.commit()
        return jsonify(existing.to_dict()), 200
    else:
        # Create new availability
        availability = Availability(
            doctor_id=doctor_id,
            day_of_week=data['dayOfWeek'],
            date=specific_date,
            start_time=data['startTime'],
            end_time=data['endTime'],
            is_available=data['isAvailable']
        )
        db.session.add(availability)
        db.session.commit()
        return jsonify(availability.to_dict()), 201

@bp.route('/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json() or {}
    
    if not all(k in data for k in ('doctorId', 'date', 'type')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # If a doctor is creating the appointment, they need to provide a patientId
    if user.role == 'doctor':
        if 'patientId' not in data:
            return jsonify({'error': 'Doctor must provide a patientId to create appointment'}), 400
        patient_id = data['patientId']
        
        # Verify the patient exists
        patient = User.query.get(patient_id)
        if not patient or patient.role != 'patient':
            return jsonify({'error': 'Patient not found'}), 404
            
    elif user.role == 'patient':
        # Patient is creating their own appointment
        patient_id = user.id
    else:
        return jsonify({'error': 'Only patients and doctors can book appointments'}), 403
    
    # Validate doctor exists
    doctor = User.query.get(data['doctorId'])
    if not doctor or doctor.role != 'doctor':
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Convert date string to datetime object
    try:
        appointment_date = parse_iso_in_chicago(data['date'])
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
    
    # Create new appointment
    appointment = Appointment(
        doctor_id=data['doctorId'],
        patient_id=patient_id,
        date=appointment_date,
        duration=data.get('duration', 30),
        type=data['type'],
        status='scheduled',
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201

@bp.route('/appointments/doctor', methods=['GET'])
@jwt_required()
def get_doctor_appointments():
    identity = get_jwt_identity()
    doctor = User.query.get(int(identity))
    
    if not doctor or doctor.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    
    # Include patient name in response
    results = []
    for appointment in appointments:
        data = appointment.to_dict()
        patient = User.query.get(appointment.patient_id)
        data['patientName'] = patient.full_name if patient else "Unknown"
        results.append(data)
    
    return jsonify(results), 200

@bp.route('/appointments/patient', methods=['GET'])
@jwt_required()
def get_patient_appointments():
    identity = get_jwt_identity()
    patient = User.query.get(int(identity))
    
    if not patient or patient.role != 'patient':
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    
    # Include doctor name and specialization in response
    results = []
    for appointment in appointments:
        data = appointment.to_dict()
        doctor = User.query.get(appointment.doctor_id)
        data['doctorName'] = doctor.full_name if doctor else "Unknown"
        data['doctorSpecialization'] = doctor.specialization if doctor else ""
        results.append(data)
    
    return jsonify(results), 200

@bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check permissions - only the doctor or patient involved can update
    if user.id != appointment.doctor_id and user.id != appointment.patient_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    
    # Update fields
    if 'status' in data:
        appointment.status = data['status']
    
    if 'notes' in data:
        appointment.notes = data['notes']
    
    # Only allow rescheduling if status is still "scheduled"
    if appointment.status == 'scheduled':
        if 'date' in data:
            try:
                appointment.date = parse_iso_in_chicago(data['date'])
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        if 'duration' in data:
            appointment.duration = data['duration']
        
        if 'type' in data:
            appointment.type = data['type']
    
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 200

@profile_routes.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@profile_routes.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json() or {}
    
    # Common fields that can be updated for any user
    common_fields = {
        'fullName': 'full_name',
        'phone': 'phone',
        'address': 'address',
        'city': 'city',
        'state': 'state',
        'zipCode': 'zip_code',
        'gender': 'gender',
        'profilePicture': 'profile_picture'
    }
    
    # Fields specific to doctors
    doctor_fields = {
        'specialization': 'specialization',
        'licenseNumber': 'license_number',
        'education': 'education',
        'experienceYears': 'experience_years',
        'hospitalAffiliation': 'hospital_affiliation',
        'boardCertification': 'board_certification',
        'bio': 'bio',
        'consultationFee': 'consultation_fee'
    }
    
    # Fields specific to patients
    patient_fields = {
        'insuranceProvider': 'insurance_provider',
        'insuranceId': 'insurance_id',
        'emergencyContactName': 'emergency_contact_name',
        'emergencyContactPhone': 'emergency_contact_phone',
        'medicalHistory': 'medical_history',
        'allergies': 'allergies',
        'currentMedications': 'current_medications',
        'bloodType': 'blood_type'
    }
    
    # Update common fields
    for json_field, db_field in common_fields.items():
        if json_field in data:
            setattr(user, db_field, data[json_field])
    
    # Update role-specific fields
    if user.role == 'doctor':
        for json_field, db_field in doctor_fields.items():
            if json_field in data:
                setattr(user, db_field, data[json_field])
    elif user.role == 'patient':
        for json_field, db_field in patient_fields.items():
            if json_field in data:
                setattr(user, db_field, data[json_field])
    
    # Handle date of birth separately due to format conversion
    if 'dateOfBirth' in data and data['dateOfBirth']:
        try:
            user.date_of_birth = datetime.fromisoformat(data['dateOfBirth'].replace('Z', '+00:00')).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format for date of birth. Use ISO format'}), 400
    
    # Update the timestamp
    user.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@bp.route('/doctor-slots/<int:doctor_id>', methods=['GET'])
def get_doctor_booked_slots(doctor_id):
    """Public endpoint to get a doctor's booked slots without sensitive information"""
    date_filter = request.args.get('date')
    
    # Query for scheduled appointments for this doctor
    query = Appointment.query.filter_by(doctor_id=doctor_id, status='scheduled')
    
    # Apply date filter if provided
    if date_filter:
        try:
            # Parse the date in Chicago timezone
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            
            # Create datetime objects representing the start and end of the day in Chicago timezone
            # These will be converted to UTC for the database query
            start_datetime = CHICAGO_TZ.localize(
                datetime.combine(filter_date, datetime.min.time())
            )
            end_datetime = CHICAGO_TZ.localize(
                datetime.combine(filter_date + timedelta(days=1), datetime.min.time())
            )
            
            # Convert to UTC for the database query
            start_datetime_utc = start_datetime.astimezone(pytz.utc)
            end_datetime_utc = end_datetime.astimezone(pytz.utc)
            
            # Filter appointments for the specific date in UTC
            query = query.filter(
                Appointment.date >= start_datetime_utc,
                Appointment.date < end_datetime_utc
            )
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    appointments = query.all()
    
    # Return only time slot information, no personal data
    slots = []
    for appointment in appointments:
        # Get the date in Chicago timezone
        utc_date = pytz.utc.localize(appointment.date) if appointment.date.tzinfo is None else appointment.date
        chicago_date = utc_date.astimezone(CHICAGO_TZ)
        
        slots.append({
            'date': chicago_date.isoformat(),
            'status': appointment.status
        })
    
    return jsonify(slots), 200