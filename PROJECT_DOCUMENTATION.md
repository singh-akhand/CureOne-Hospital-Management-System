# Hospital Management System - Complete Documentation

## Project Overview

A comprehensive web-based Hospital Management System built with Flask for Cure One Hospital project. The system supports three user roles (Admin, Doctor, Patient) with complete CRUD operations, appointment management, and treatment tracking.

## Features Implemented

### 1. Authentication & Authorization ✓
- **Flask-Security-Too** integration with bcrypt password hashing
- Role-based access control (Admin, Doctor, Patient)
- User registration with automatic patient role assignment
- Protected routes with `@login_required` and `@roles_required` decorators
- Automatic redirect to role-specific dashboards after login

### 2. Database Models (7 Models) ✓
1. **User** - UserMixin with email, username, password, phone, address
2. **Role** - RoleMixin for role-based access
3. **Department** - Medical departments (Cardiology, Pediatrics, etc.)
4. **Doctor** - Doctor profiles with availability and qualifications
5. **Patient** - Patient profiles with medical history
6. **Appointment** - Appointment booking and tracking
7. **Treatment** - Treatment records with diagnosis and prescriptions

### 3. Admin Functionalities ✓
- Dashboard with statistics (doctors, patients, appointments, departments)
- **Doctor Management**:
  - Add new doctors with department, qualification, experience
  - Edit doctor details and availability
  - Delete doctors with confirmation
  - Search doctors by name/department
  - Time slot management (6 AM - 10 PM)
- **Patient Management**:
  - View all patients
  - Search patients by name/email
  - Remove/blacklist patients
- **Appointment Management**:
  - View all appointments
  - Filter by status (Booked/Completed/Cancelled)
  - Export appointments to CSV

### 4. Doctor Functionalities ✓
- Dashboard with today's appointments and statistics
- View all appointments with filtering
- Appointment details with patient history
- Complete appointments with:
  - Diagnosis entry
  - Treatment plan
  - Prescription details
  - Additional notes
- Cancel appointments
- View patient's complete medical history

### 5. Patient Functionalities ✓
- Dashboard with upcoming appointments count
- **Profile Management**:
  - Update phone, address
  - Update blood group
  - Update medical history
- **Doctor Search & Booking**:
  - View all doctors
  - Filter by department
  - Search by name
  - View doctor profiles (qualification, experience, fees, availability)
  - Book appointments with:
    - Date selection (next 7 days)
    - Time slot selection (based on doctor's availability)
    - Reason for visit
- **Appointment Management**:
  - View all appointments
  - Cancel booked appointments
  - View treatment records for completed appointments

### 6. Key Technical Features ✓
- **Double Booking Prevention**: Checks if doctor is already booked at selected time
- **Dynamic Time Slots**: Generates hourly slots from doctor's availability
- **Status Tracking**: Booked → Completed/Cancelled
- **CSV Export**: Admin can export appointment data
- **Patient Registration Hook**: Automatic patient profile creation
- **Role-based Navigation**: Dynamic navbar based on user role

### 7. Communication & Notification Module (New) ✓
- **Asynchronous Email System**: Built using Python `smtplib` and `threading` for non-blocking performance.
- **Smart Notifications**:
  - **Welcome Email**: Sent immediately upon patient registration.
  - **Booking Confirmation**: Sent to patient with Doctor name and Time slot details.
  - **Treatment Completion & Prescription**: Auto-email sent to patient when Doctor completes checkup (includes Diagnosis summary).
  - **Cancellation Alerts**: 
    - Patient notified if Doctor cancels.
    - Doctor notified if Patient cancels.
  - **Credential Delivery**: Auto-email with login details when Admin creates a new Doctor account.
- **Testing Environment**: Integrated with Ethereal Email for safe testing without spamming real inboxes.

## Technology Stack

```
Backend:
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Security-Too 5.3.2
- bcrypt (password hashing)
- SQLite database

Frontend:
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Jinja2 templates
- Custom CSS with gradients and animations

Additional:
- email-validator
- bleach
- CSV export functionality
```

## Project Structure

```
Cure One Hospital-Project/
├── app.py                          # Main application with all routes
├── models.py                       # Database models
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # Project description
├── .gitignore                      # Git ignore file
├── instance/
│   └── hospital.db                 # SQLite database (auto-created)
├── templates/
│   ├── base.html                   # Base template with navbar
│   ├── index.html                  # Landing page
│   ├── security/
│   │   ├── login_user.html         # Login form
│   │   └── register_user.html      # Registration form
│   ├── admin/
│   │   ├── dashboard.html          # Admin dashboard
│   │   ├── doctors.html            # Doctor list
│   │   ├── add_doctor.html         # Add doctor form
│   │   ├── edit_doctor.html        # Edit doctor form
│   │   ├── patients.html           # Patient list
│   │   └── appointments.html       # Appointment list
│   ├── doctor/
│   │   ├── dashboard.html          # Doctor dashboard
│   │   ├── appointments.html       # Doctor's appointments
│   │   └── appointment_detail.html # Appointment details & treatment
│   └── patient/
│       ├── dashboard.html          # Patient dashboard
│       ├── profile.html            # Profile update form
│       ├── doctors.html            # Doctor search & browse
│       ├── doctor_detail.html      # Doctor profile view
│       ├── book_appointment.html   # Appointment booking
│       └── appointments.html       # Patient's appointments
└── static/
    └── css/
        └── custom.css              # Custom styling
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Access Application
- URL: http://127.0.0.1:5000
- Admin Login: admin@hospital.com / admin123

## Default Credentials

### Admin Account (Pre-created)
- **Email**: admin@hospital.com
- **Password**: admin123

### Patient Account (Self-registration)
- Patients can register via the registration page
- Automatic patient role assignment
- Username field is required

### Doctor Account (Created by Admin)
- Doctors cannot self-register
- Admin creates doctor accounts
- Credentials provided by admin

## Database Schema

### User Table
- id (Primary Key)
- email (Unique, Required)
- username (Unique, Required)
- password (Hashed with bcrypt)
- active (Boolean)
- phone
- address
- created_at (Timestamp)
- fs_uniquifier (Flask-Security unique identifier)

### Role Table
- id (Primary Key)
- name (admin/doctor/patient)
- description

### Department Table
- id (Primary Key)
- name (Unique)
- description

### Doctor Table
- id (Primary Key)
- user_id (Foreign Key → User)
- department_id (Foreign Key → Department)
- qualification
- experience_years
- consultation_fee
- available_days
- available_time (Format: "09:00 to 17:00")

### Patient Table
- id (Primary Key)
- user_id (Foreign Key → User)
- blood_group
- medical_history

### Appointment Table
- id (Primary Key)
- patient_id (Foreign Key → Patient)
- doctor_id (Foreign Key → Doctor)
- appointment_date
- appointment_time (12-hour format with AM/PM)
- reason
- status (Booked/Completed/Cancelled)
- created_at (Timestamp)

### Treatment Table
- id (Primary Key)
- appointment_id (Foreign Key → Appointment, Unique)
- diagnosis
- treatment
- prescription
- notes
- created_at (Timestamp)

## Key Implementation Details

### 1. Patient Registration Hook
```python
@user_registered.connect_via(app)
def user_registered_sighandler(sender, user, **extra):
    patient_role = Role.query.filter_by(name='patient').first()
    user_datastore.add_role_to_user(user, patient_role)
    patient = Patient(user_id=user.id)
    db.session.add(patient)
    db.session.commit()
```

### 2. Time Slot Generation
- Doctor's availability stored as "09:00 to 17:00"
- System generates hourly slots dynamically
- Converts to 12-hour format for display
- Prevents double booking

### 3. Role-Based Dashboard Routing
```python
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.has_role('admin'):
        return redirect(url_for('admin_dashboard'))
    elif current_user.has_role('doctor'):
        return redirect(url_for('doctor_dashboard'))
    elif current_user.has_role('patient'):
        return redirect(url_for('patient_dashboard'))
```

### 4. CSV Export Implementation
- Uses StringIO and BytesIO for in-memory CSV creation
- Includes appointment date, time, patient name, doctor name, status
- Downloads as `appointments_YYYYMMDD.csv`

## Configuration Settings

### Flask Configuration
- SECRET_KEY: Used for session security
- SQLALCHEMY_DATABASE_URI: Points to SQLite database
- SQLALCHEMY_TRACK_MODIFICATIONS: False (performance)

### Flask-Security Configuration
- SECURITY_PASSWORD_SALT: For password hashing
- SECURITY_PASSWORD_HASH: bcrypt
- SECURITY_REGISTERABLE: True (allows patient registration)
- SECURITY_USERNAME_ENABLE: True (username field required)
- SECURITY_POST_LOGIN_VIEW: '/dashboard'
- SECURITY_POST_REGISTER_VIEW: '/dashboard'

## UI/UX Features

### Design Elements
- Modern gradient cards for dashboards
- Responsive Bootstrap 5 design
- Font Awesome icons throughout
- Clean color-coded status badges
- Hover effects and animations
- Shadow effects for depth
- Mobile-responsive layout

### Color Coding
- **Primary (Blue)**: Booked appointments
- **Success (Green)**: Completed appointments
- **Danger (Red)**: Cancelled appointments
- **Warning (Yellow)**: Pending actions
- **Info (Cyan)**: Information displays

## Security Features

1. **Password Hashing**: All passwords hashed with bcrypt
2. **Role-Based Access**: Protected routes with decorators
3. **CSRF Protection**: Flask-WTF CSRF tokens
4. **SQL Injection Prevention**: SQLAlchemy ORM
5. **XSS Protection**: Bleach for sanitization
6. **Session Security**: Secure session management

## Testing Guide

### Test Admin Features
1. Login as admin (admin@hospital.com / admin123)
2. Add a new doctor with availability
3. View patient list
4. View all appointments
5. Export appointments to CSV

### Test Doctor Features
1. Admin creates doctor account
2. Login as doctor
3. View today's appointments
4. Open appointment and add treatment
5. Mark appointment as completed
6. View patient medical history

### Test Patient Features
1. Register new patient account
2. Update profile with blood group and medical history
3. Search for doctors by department
4. Book appointment with available time slot
5. View booked appointments
6. Cancel an appointment

## Common Issues & Solutions

### Issue: Database not created
**Solution**: The database is automatically created on first run. Check the `instance/` folder.

### Issue: Cannot login after registration
**Solution**: Make sure you're using the correct email/password. Check database for user entry.

### Issue: Time slots not showing
**Solution**: Verify doctor's `available_time` is in format "HH:MM to HH:MM" (24-hour format).

### Issue: Appointment booking fails
**Solution**: Check for existing appointments at the same date/time (double booking prevention).

## License
Educational project for Cure One Hospital course.

