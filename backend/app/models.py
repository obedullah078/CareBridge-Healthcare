from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='patient', nullable=False)  # 'doctor' or 'patient'
    
    # Common profile fields
    phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    zip_code = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    profile_picture = db.Column(db.String(256))  # URL to profile picture
    
    # Doctor-specific fields
    specialization = db.Column(db.String(128))
    license_number = db.Column(db.String(128))
    education = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    hospital_affiliation = db.Column(db.String(256))
    board_certification = db.Column(db.String(256))
    bio = db.Column(db.Text)
    consultation_fee = db.Column(db.Float)
    
    # Patient-specific fields
    insurance_provider = db.Column(db.String(128))
    insurance_id = db.Column(db.String(128))
    emergency_contact_name = db.Column(db.String(128))
    emergency_contact_phone = db.Column(db.String(20))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    blood_type = db.Column(db.String(10))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationships
    doctor_appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy='dynamic')
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy='dynamic')
    availabilities = db.relationship('Availability', backref='doctor', lazy='dynamic')
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'fullName': self.full_name,
            'role': self.role,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipCode': self.zip_code,
            'dateOfBirth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'profilePicture': self.profile_picture
        }
        
        # Add role-specific fields
        if self.role == 'doctor':
            data.update({
                'specialization': self.specialization,
                'licenseNumber': self.license_number,
                'education': self.education,
                'experienceYears': self.experience_years,
                'hospitalAffiliation': self.hospital_affiliation,
                'boardCertification': self.board_certification,
                'bio': self.bio,
                'consultationFee': self.consultation_fee
            })
        elif self.role == 'patient':
            data.update({
                'insuranceProvider': self.insurance_provider,
                'insuranceId': self.insurance_id,
                'emergencyContactName': self.emergency_contact_name,
                'emergencyContactPhone': self.emergency_contact_phone,
                'medicalHistory': self.medical_history,
                'allergies': self.allergies,
                'currentMedications': self.current_medications,
                'bloodType': self.blood_type
            })
            
        return data

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)  # Changed from Date to DateTime
    duration = db.Column(db.Integer, default=30, nullable=False)  # Added to match schema
    type = db.Column(db.String(50), nullable=False)  # Changed from appointment_type to match schema
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        import pytz
        
        # Convert UTC date to Chicago timezone for consistent handling with frontend
        chicago_tz = pytz.timezone('America/Chicago')
        utc_date = pytz.utc.localize(self.date) if self.date.tzinfo is None else self.date
        chicago_date = utc_date.astimezone(chicago_tz)
        
        return {
            'id': self.id,
            'patientId': self.patient_id,
            'doctorId': self.doctor_id,
            'date': chicago_date.isoformat(),
            'duration': self.duration,
            'type': self.type,
            'status': self.status,
            'notes': self.notes
        }

class Availability(db.Model):
    __tablename__ = 'availability'  # Changed to match schema
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # Changed from date to match schema
    date = db.Column(db.Date, nullable=True)  # New field for specific date
    start_time = db.Column(db.String(10), nullable=False)  # Changed from time_slots to match schema
    end_time = db.Column(db.String(10), nullable=False)  # Added to match schema
    is_available = db.Column(db.Boolean, default=True, nullable=False)  # Added to match schema
    
    def to_dict(self):
        return {
            'id': self.id,
            'doctorId': self.doctor_id,
            'dayOfWeek': self.day_of_week,
            'date': self.date.isoformat() if self.date else None,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'isAvailable': self.is_available
        }