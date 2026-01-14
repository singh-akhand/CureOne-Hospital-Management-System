"""
Database Models for Hospital Management System
Defines 7 models: User, Role, Department, Doctor, Patient, Appointment, Treatment
"""
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Many-to-Many relationship table for User and Role
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    """
    Role model for role-based access control
    Roles: admin, doctor, patient
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    """
    User model for authentication
    Integrated with Flask-Security for authentication and authorization
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Department(db.Model):
    """
    Department model to categorize doctors by specialization
    Examples: Cardiology, Pediatrics, Orthopedics, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    doctors = db.relationship('Doctor', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class Doctor(db.Model):
    """
    Doctor model - stores doctor-specific information
    Only admin can create doctor accounts
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    qualification = db.Column(db.String(255), nullable=False)
    experience_years = db.Column(db.Integer, nullable=False)
    consultation_fee = db.Column(db.Float, nullable=False)
    available_days = db.Column(db.String(100))  # e.g., "Monday, Wednesday, Friday"
    available_time = db.Column(db.String(50))   # e.g., "09:00 to 17:00"
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Doctor {self.user.username}>'


class Patient(db.Model):
    """
    Patient model - stores patient-specific information
    Automatically created when a user registers as patient
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    blood_group = db.Column(db.String(5))
    medical_history = db.Column(db.Text)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.user.username}>'


class Appointment(db.Model):
    """
    Appointment model - manages patient-doctor appointments
    Status can be: Booked, Completed, Cancelled
    """
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)  # e.g., "09:00 AM"
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Booked')  # Booked, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'


class Treatment(db.Model):
    """
    Treatment model - stores diagnosis and prescription for completed appointments
    Created by doctor after appointment completion
    """
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, unique=True)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Treatment for Appointment {self.appointment_id}>'
