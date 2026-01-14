# Hospital Management System (HMS)

A comprehensive web-based Hospital Management System built with Flask for Cure One Hospital project.

## Features

### Role-Based Access Control
- **Admin**: Manage doctors, patients, appointments, and departments
- **Doctor**: View appointments, add treatment records, manage patient consultations
- **Patient**: Book appointments, view doctors, update profile, view medical history

### Core Functionalities
- User authentication with bcrypt password hashing
- Department management
- Doctor scheduling with availability slots
- Appointment booking with double-booking prevention
- Treatment and prescription management
- CSV export for appointments
- Medical history tracking

### Key Features
- **Smart Email Notifications**: Automated emails for registration, booking confirmations, cancellations,Treatment Completion & Prescription.


## Technology Stack

- **Backend**: Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-Security-Too 5.3.2
- **Database**: SQLite
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0, Jinja2
- **Security**: bcrypt, email-validator, bleach

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access at http://127.0.0.1:5000

## Default Admin Credentials

- **Email**: admin@hospital.com
- **Password**: admin123

## Database Models

1. **User**: Authentication and user management
2. **Role**: Role-based access control (admin, doctor, patient)
3. **Department**: Medical departments
4. **Doctor**: Doctor profiles and availability
5. **Patient**: Patient profiles and medical history
6. **Appointment**: Appointment scheduling
7. **Treatment**: Diagnosis and prescription records

## Project Structure

```
Cure One Hospital-Project/
├── app.py                    # Main application
├── models.py                 # Database models
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── instance/                 # Database folder
├── templates/                # HTML templates
│   ├── admin/               # Admin templates
│   ├── doctor/              # Doctor templates
│   ├── patient/             # Patient templates
│   └── security/            # Auth templates
└── static/                   # CSS and assets
```

## License

Educational project for Cure One Hospital course.
