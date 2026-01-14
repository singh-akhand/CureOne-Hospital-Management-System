"""
Hospital Management System - Main Application
Flask application with Flask-Security for authentication and role-based access control
"""
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_required, current_user, hash_password, user_registered
from models import db, User, Role, Department, Doctor, Patient, Appointment, Treatment
from config import Config
import os
from datetime import datetime, timedelta, date
import csv
from io import StringIO, BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from weasyprint import HTML
from flask import Flask, render_template, redirect, url_for, request, flash, send_file, make_response
import google.generativeai as genai

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
# Configure Gemini API
# REPLACE 'YOUR_API_KEY_HERE' with the actual key you copied from Google AI Studio
os.environ["GEMINI_API_KEY"] = "AIzaSyAmlnO1QKmsDcMqwPnUn5jA7QWktWB-Rd8"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize database
db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# EMAIL FUNCTIONALITY USING SMTP
def send_email_background(subject, recipient, body, config):
    """Background task to send email via SMTP"""
    try:
        sender_email = config.get('MAIL_USERNAME')
        sender_password = config.get('MAIL_PASSWORD')
        # Default to Gmail if not provided in config
        smtp_server = config.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = config.get('MAIL_PORT', 587)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient, text)
        server.quit()
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def send_async_email(subject, recipient, body):
    """Helper to start email thread without freezing UI"""
    # Pass current app config to thread
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("Mail credentials not configured. Skipping email.")
        return

    # Extract needed config headers to pass to thread safely
    # (Flask app context isn't available inside the raw thread easily)
    mail_config = {
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': app.config.get('MAIL_PASSWORD'),
        'MAIL_SERVER': app.config.get('MAIL_SERVER', 'smtp.gmail.com'),
        'MAIL_PORT': app.config.get('MAIL_PORT', 587)
    }

    thread = threading.Thread(target=send_email_background, args=(subject, recipient, body, mail_config))
    thread.daemon = True
    thread.start()

# Signal handler for patient registration
@user_registered.connect_via(app)
def user_registered_sighandler(sender, user, **extra):
    """
    Automatically assign patient role and create patient profile
    when a new user registers through Flask-Security registration form
    """
    patient_role = Role.query.filter_by(name='patient').first()
    user_datastore.add_role_to_user(user, patient_role)
    patient = Patient(user_id=user.id)
    db.session.add(patient)
    db.session.commit()
    
    # --- ADD ASYNC EMAIL CALL HERE ---
    subject = "Welcome to Hospital Management System"
    body = f"""Hello {user.username},

Welcome to our hospital! Your patient account has been successfully created.
You can now log in to book appointments and view your medical history.

Best Regards,
Hospital Admin Team"""
    send_async_email(subject, user.email, body)

    flash('Patient account created successfully!', 'success')

def create_initial_data():
    """
    Create initial data: roles, admin user, and departments
    Called only once when database is first created
    """
    # Create roles
    roles = ['admin', 'doctor', 'patient']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=f'{role_name.capitalize()} role')
            db.session.add(role)
    
    db.session.commit()
    
    # Create admin user
    if not User.query.filter_by(email='admin@hospital.com').first():
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = user_datastore.create_user(
            email='admin@hospital.com',
            username='admin',
            password=hash_password('admin123'),
            active=True,
            roles=[admin_role]
        )
        db.session.commit()
    
    # Create sample departments
    departments = [
        {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
        {'name': 'Pediatrics', 'description': 'Medical care for children'},
        {'name': 'Orthopedics', 'description': 'Bones, joints, and muscles'},
        {'name': 'Neurology', 'description': 'Nervous system disorders'},
        {'name': 'Dermatology', 'description': 'Skin conditions and treatment'},
        {'name': 'General Medicine', 'description': 'General health and wellness'}
    ]
    
    for dept_data in departments:
        if not Department.query.filter_by(name=dept_data['name']).first():
            dept = Department(**dept_data)
            db.session.add(dept)
    
    db.session.commit()


# Create database and initial data before first request
with app.app_context():
    # Create instance folder if it doesn't exist
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Create all tables
    db.create_all()
    
    # Create initial data
    create_initial_data()


# ========== PUBLIC ROUTES ==========

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard - redirects to role-specific dashboard
    """
    # Check user role and redirect accordingly
    if current_user.has_role('admin'):
        return redirect(url_for('admin_dashboard'))
    elif current_user.has_role('doctor'):
        return redirect(url_for('doctor_dashboard'))
    elif current_user.has_role('patient'):
        return redirect(url_for('patient_dashboard'))
    else:
        flash('No role assigned. Please contact administrator.', 'danger')
        return redirect(url_for('index'))


# ========== ADMIN ROUTES ==========

@app.route('/admin/dashboard')
@login_required
@roles_required('admin')
def admin_dashboard():
    """Admin dashboard with statistics and recent appointments"""
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    total_departments = Department.query.count()
    
    # Get recent 10 appointments
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         total_departments=total_departments,
                         recent_appointments=recent_appointments)


@app.route('/admin/doctors')
@login_required
@roles_required('admin')
def admin_doctors():
    """View all doctors"""
    search_query = request.args.get('search', '')
    
    if search_query:
        doctors = Doctor.query.join(User).filter(
            User.username.contains(search_query) | 
            Department.name.contains(search_query)
        ).all()
    else:
        doctors = Doctor.query.all()
    
    return render_template('admin/doctors.html', doctors=doctors, search_query=search_query)


@app.route('/admin/doctor/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_add_doctor():
    """Add new doctor"""
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        department_id = request.form.get('department_id')
        qualification = request.form.get('qualification')
        experience_years = request.form.get('experience_years')
        consultation_fee = request.form.get('consultation_fee')
        available_days = request.form.get('available_days')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin_add_doctor'))
        
        # Create user account
        doctor_role = Role.query.filter_by(name='doctor').first()
        user = user_datastore.create_user(
            email=email,
            username=username,
            password=hash_password(password),
            phone=phone,
            address=address,
            active=True,
            roles=[doctor_role]
        )
        db.session.flush()
        
        # Create doctor profile
        available_time = f"{start_time} to {end_time}"
        doctor = Doctor(
            user_id=user.id,
            department_id=department_id,
            qualification=qualification,
            experience_years=experience_years,
            consultation_fee=consultation_fee,
            available_days=available_days,
            available_time=available_time
        )
        db.session.add(doctor)
        db.session.commit()

        try:
            email_body = f"""Welcome Dr. {username},

You have been registered as a Doctor in our Hospital Management System.

Here are your login credentials:
📧 Email: {email}
🔑 Password: {password}

Please login and check your dashboard.
"""
            send_async_email(
                subject="Doctor Account Credentials 🔐",
                recipient=email,
                body=email_body
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('admin_doctors'))
    
    departments = Department.query.all()
    
    # Generate time options (6 AM to 10 PM)
    time_options = []
    for hour in range(6, 23):  # 6 AM to 10 PM
        time_options.append(f"{hour:02d}:00")
    
    return render_template('admin/add_doctor.html', departments=departments, time_options=time_options)


@app.route('/admin/doctor/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_edit_doctor(doctor_id):
    """Edit doctor details"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        # Update user information
        doctor.user.username = request.form.get('username')
        doctor.user.email = request.form.get('email')
        doctor.user.phone = request.form.get('phone')
        doctor.user.address = request.form.get('address')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            doctor.user.password = hash_password(new_password)
        
        # Update doctor information
        doctor.department_id = request.form.get('department_id')
        doctor.qualification = request.form.get('qualification')
        doctor.experience_years = request.form.get('experience_years')
        doctor.consultation_fee = request.form.get('consultation_fee')
        doctor.available_days = request.form.get('available_days')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        doctor.available_time = f"{start_time} to {end_time}"
        
        db.session.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('admin_doctors'))
    
    departments = Department.query.all()
    
    # Generate time options
    time_options = []
    for hour in range(6, 23):
        time_options.append(f"{hour:02d}:00")
    
    # Parse current availability
    start_time, end_time = '', ''
    if doctor.available_time:
        parts = doctor.available_time.split(' to ')
        if len(parts) == 2:
            start_time, end_time = parts[0], parts[1]
    
    return render_template('admin/edit_doctor.html', 
                         doctor=doctor, 
                         departments=departments, 
                         time_options=time_options,
                         start_time=start_time,
                         end_time=end_time)


@app.route('/admin/doctor/delete/<int:doctor_id>', methods=['POST'])
@login_required
@roles_required('admin')
def admin_delete_doctor(doctor_id):
    """Delete doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    
    flash('Doctor deleted successfully!', 'success')
    return redirect(url_for('admin_doctors'))


@app.route('/admin/patients')
@login_required
@roles_required('admin')
def admin_patients():
    """View all patients"""
    search_query = request.args.get('search', '')
    
    if search_query:
        patients = Patient.query.join(User).filter(
            User.username.contains(search_query) | 
            User.email.contains(search_query)
        ).all()
    else:
        patients = Patient.query.all()
    
    return render_template('admin/patients.html', patients=patients, search_query=search_query)


@app.route('/admin/patient/delete/<int:patient_id>', methods=['POST'])
@login_required
@roles_required('admin')
def admin_delete_patient(patient_id):
    """Delete/blacklist patient"""
    patient = Patient.query.get_or_404(patient_id)
    user = patient.user
    
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    
    flash('Patient removed successfully!', 'success')
    return redirect(url_for('admin_patients'))


@app.route('/admin/appointments')
@login_required
@roles_required('admin')
def admin_appointments():
    """View all appointments with filtering"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    else:
        appointments = Appointment.query.filter_by(status=status_filter).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('admin/appointments.html', 
                         appointments=appointments, 
                         status_filter=status_filter)


@app.route('/admin/appointments/export')
@login_required
@roles_required('admin')
def admin_export_appointments():
    """Export appointments to CSV"""
    appointments = Appointment.query.all()
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    
    # Write header
    writer.writerow(['Date', 'Time', 'Patient Name', 'Doctor Name', 'Department', 'Status'])
    
    # Write data
    for apt in appointments:
        writer.writerow([
            apt.appointment_date.strftime('%Y-%m-%d'),
            apt.appointment_time,
            apt.patient.user.username,
            apt.doctor.user.username,
            apt.doctor.department.name,
            apt.status
        ])
    
    # Create response
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'appointments_{datetime.now().strftime("%Y%m%d")}.csv'
    )


# ========== DOCTOR ROUTES ==========

@app.route('/doctor/dashboard')
@login_required
@roles_required('doctor')
def doctor_dashboard():
    """Doctor dashboard with today's appointments"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if not doctor:
        flash('Doctor profile not found!', 'danger')
        return redirect(url_for('index'))
    
    today = date.today()
    
    # Get today's appointments
    todays_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=today
    ).all()
    
    # Count by status
    total_today = len(todays_appointments)
    pending_count = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').count()
    completed_count = Appointment.query.filter_by(doctor_id=doctor.id, status='Completed').count()
    cancelled_count = Appointment.query.filter_by(doctor_id=doctor.id, status='Cancelled').count()
    
    return render_template('doctor/dashboard.html',
                         doctor=doctor,
                         todays_appointments=todays_appointments,
                         total_today=total_today,
                         pending_count=pending_count,
                         completed_count=completed_count,
                         cancelled_count=cancelled_count)


@app.route('/doctor/appointments')
@login_required
@roles_required('doctor')
def doctor_appointments():
    """View all appointments for doctor"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_date.desc()).all()
    else:
        appointments = Appointment.query.filter_by(doctor_id=doctor.id, status=status_filter).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/appointments.html', 
                         appointments=appointments, 
                         status_filter=status_filter)


@app.route('/doctor/appointment/<int:appointment_id>')
@login_required
@roles_required('doctor')
def doctor_appointment_detail(appointment_id):
    """View appointment details and patient history"""
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Verify this appointment belongs to logged-in doctor
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Get patient's all appointments with treatments
    patient_history = Appointment.query.filter_by(
        patient_id=appointment.patient_id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('doctor/appointment_detail.html', 
                         appointment=appointment,
                         patient_history=patient_history)


@app.route('/doctor/appointment/<int:appointment_id>/complete', methods=['POST'])
@login_required
@roles_required('doctor')
def doctor_complete_appointment(appointment_id):
    """Mark appointment as completed and add treatment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    # Get treatment details
    diagnosis = request.form.get('diagnosis')
    treatment_text = request.form.get('treatment')
    prescription = request.form.get('prescription')
    notes = request.form.get('notes')
    
    # Update appointment status
    appointment.status = 'Completed'
    
    # Create treatment record
    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=diagnosis,
        treatment=treatment_text,
        prescription=prescription,
        notes=notes
    )
    db.session.add(treatment)
    db.session.commit()

    # EMAIL CODE HERE TO NOTIFY PATIENT
    try:
        send_async_email(
            subject="Checkup Completed & Prescription Ready 💊",
            recipient=appointment.patient.user.email,
            body=f"Hello {appointment.patient.user.username},\n\nYour checkup with Dr. {doctor.user.username} is complete.\n\nDiagnosis: {diagnosis}\n\nYou can login to the portal to download your prescription PDF.\n\nTake Care!"
        )
    except:
        pass
    
    flash('Appointment completed and treatment recorded!', 'success')
    return redirect(url_for('doctor_appointments'))


@app.route('/doctor/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@roles_required('doctor')
def doctor_cancel_appointment(appointment_id):
    """Cancel appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if appointment.doctor_id != doctor.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()

    try:
        send_async_email(
            subject="Appointment Cancelled ❌",
            recipient=appointment.patient.user.email,
            body=f"Dear {appointment.patient.user.username},\n\nYour appointment with Dr. {doctor.user.username} on {appointment.appointment_date} has been cancelled by the doctor.\n\nPlease reschedule."
        )
    except:
        pass
    
    flash('Appointment cancelled!', 'warning')
    return redirect(url_for('doctor_appointments'))


# ========== PATIENT ROUTES ==========

@app.route('/patient/dashboard')
@login_required
@roles_required('patient')
def patient_dashboard():
    """Patient dashboard"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient:
        flash('Patient profile not found!', 'danger')
        return redirect(url_for('index'))
    
    # Get upcoming appointments count
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == 'Booked',
        Appointment.appointment_date >= date.today()
    ).count()
    
    return render_template('patient/dashboard.html', 
                         patient=patient,
                         upcoming_appointments=upcoming_appointments)


@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
@roles_required('patient')
def patient_profile():
    """Update patient profile"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        patient.medical_history = request.form.get('medical_history')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient_profile'))
    
    return render_template('patient/profile.html', patient=patient)


@app.route('/patient/doctors')
@login_required
@roles_required('patient')
def patient_doctors():
    """View all doctors with search and filter"""
    search_query = request.args.get('search', '')
    department_id = request.args.get('department', '')
    
    query = Doctor.query.join(User)
    
    if search_query:
        query = query.filter(User.username.contains(search_query))
    
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    
    doctors = query.all()
    departments = Department.query.all()
    
    return render_template('patient/doctors.html', 
                         doctors=doctors, 
                         departments=departments,
                         search_query=search_query,
                         selected_department=department_id)


@app.route('/patient/doctor/<int:doctor_id>')
@login_required
@roles_required('patient')
def patient_doctor_detail(doctor_id):
    """View doctor details"""
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('patient/doctor_detail.html', doctor=doctor)


@app.route('/patient/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
@roles_required('patient')
def patient_book_appointment(doctor_id):
    """Book appointment with doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date()
        appointment_time = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        # Check for double booking
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='Booked'
        ).first()
        
        if existing:
            flash('This time slot is already booked. Please select another time.', 'danger')
            return redirect(url_for('patient_book_appointment', doctor_id=doctor_id))
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            status='Booked'
        )
        db.session.add(appointment)
        db.session.commit()
        
        # ASYNC EMAIL CALL HERE TO CONFIRM APPOINTMENT
        email_subject = "Appointment Confirmation - ID #" + str(appointment.id)
        email_body = f"""Hello {patient.user.username},

Your appointment has been confirmed!

Doctor: Dr. {doctor.user.username}
Date: {appointment_date}
Time: {appointment_time}
Reason: {reason}

Please arrive 10 minutes early.

Best Regards,
Hospital Admin Team"""
        
        send_async_email(email_subject, patient.user.email, email_body)
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient_appointments'))
    
    # Generate next 7 days for date selection
    today = date.today()
    available_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    
    # Generate time slots from doctor's availability
    time_slots = []
    if doctor.available_time:
        parts = doctor.available_time.split(' to ')
        if len(parts) == 2:
            start_hour = int(parts[0].split(':')[0])
            end_hour = int(parts[1].split(':')[0])
            
            for hour in range(start_hour, end_hour):
                # Convert to 12-hour format
                am_pm = 'AM' if hour < 12 else 'PM'
                display_hour = hour if hour <= 12 else hour - 12
                if display_hour == 0:
                    display_hour = 12
                time_slots.append(f"{display_hour:02d}:00 {am_pm}")
    
    return render_template('patient/book_appointment.html', 
                         doctor=doctor,
                         available_dates=available_dates,
                         time_slots=time_slots)


@app.route('/patient/appointments')
@login_required
@roles_required('patient')
def patient_appointments():
    """View all patient appointments"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/appointments.html', appointments=appointments)


@app.route('/patient/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@roles_required('patient')
def patient_cancel_appointment(appointment_id):
    """Cancel appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if appointment.patient_id != patient.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    appointment.status = 'Cancelled'
    db.session.commit()

    try:
        doctor_email = appointment.doctor.user.email
        send_async_email(
            subject="Appointment Cancelled by Patient ⚠️",
            recipient=doctor_email,
            body=f"Dr. {appointment.doctor.user.username},\n\nPatient {appointment.patient.user.username} has cancelled their appointment scheduled for {appointment.appointment_date} at {appointment.appointment_time}."
        )
    except:
        pass
    
    flash('Appointment cancelled!', 'warning')
    return redirect(url_for('patient_appointments'))

@app.route('/patient/appointment/<int:appointment_id>/download_prescription')
@login_required
@roles_required('patient')
def download_prescription(appointment_id):
    """Generate and download PDF prescription"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Security check: Ensure the appointment belongs to the current user
    if appointment.patient.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('patient_dashboard'))
    
    # Check if treatment exists (cannot generate prescription if not treated)
    if not appointment.treatment:
        flash('Prescription not available yet.', 'warning')
        return redirect(url_for('patient_appointments'))
    
    # Render the HTML template
    html_content = render_template('pdf/prescription.html', appointment=appointment)
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()
    
    # Create response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=prescription_{appointment.id}.pdf'
    
    return response

@app.route('/patient/symptom-checker', methods=['GET', 'POST'])
@login_required
@roles_required('patient')
def symptom_checker():
    """Smart AI Symptom Checker (Gemini + Local Fallback)"""
    recommendation = None
    symptoms_input = ''
    
    if request.method == 'POST':
        symptoms_input = request.form.get('symptoms', '')
        
        # --- ATTEMPT 1: GOOGLE GEMINI API ---
        try:
            # Get list of departments from DB to guide the AI
            departments = Department.query.with_entities(Department.name).all()
            dept_list = [d.name for d in departments]
            dept_string = ", ".join(dept_list)
            
            prompt = f"""
            Act as a medical receptionist. 
            Patient symptoms: "{symptoms_input}".
            Available Departments: {dept_string}.
            
            Task: Return ONLY the exact name of the one best department from the list.
            If unclear, return "General Medicine".
            Do not write sentences, just the name.
            """
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            suggested_dept = response.text.strip()
            
            # Verify AI response against DB
            dept_obj = Department.query.filter_by(name=suggested_dept).first()
            
            if dept_obj:
                recommendation = {
                    'department': suggested_dept,
                    'dept_id': dept_obj.id,
                    'confidence': 'High (AI Analysis)'
                }
        
        except Exception as e:
            # --- ATTEMPT 2: LOCAL FALLBACK (If API fails/no internet) ---
            print(f"Gemini API Error: {e}") # Print error to terminal for debugging
            
            # Your original dictionary logic serves as the backup
            symptoms_lower = symptoms_input.lower()
            knowledge_base = {
                'Cardiology': ['heart', 'chest', 'pain', 'pressure', 'stroke', 'cardiac', 'pulse', 'breath'],
                'Pediatrics': ['child', 'baby', 'infant', 'growth', 'vaccination', 'kids', 'toddler'],
                'Orthopedics': ['bone', 'joint', 'fracture', 'knee', 'back', 'muscle', 'arthritis', 'leg', 'arm'],
                'Neurology': ['headache', 'migraine', 'dizzy', 'seizure', 'numbness', 'brain', 'faint'],
                'Dermatology': ['skin', 'rash', 'acne', 'itching', 'hair', 'nail', 'spots', 'burn'],
                'General Medicine': ['fever', 'cold', 'flu', 'weakness', 'fatigue', 'cough', 'vomit', 'stomach']
            }
            
            scores = {dept: 0 for dept in knowledge_base}
            for dept, keywords in knowledge_base.items():
                for word in keywords:
                    if word in symptoms_lower:
                        scores[dept] += 1
            
            best_match = max(scores, key=scores.get)
            
            if scores[best_match] > 0:
                dept_obj = Department.query.filter_by(name=best_match).first()
                if dept_obj:
                    recommendation = {
                        'department': best_match,
                        'dept_id': dept_obj.id,
                        'confidence': 'Moderate (Local Backup)'
                    }
            else:
                # Absolute fallback
                gen_med = Department.query.filter_by(name='General Medicine').first()
                if gen_med:
                    recommendation = {
                        'department': 'General Medicine',
                        'dept_id': gen_med.id,
                        'confidence': 'Low (Default)'
                    }

    return render_template('patient/symptom_checker.html', 
                         recommendation=recommendation, 
                         symptoms_input=symptoms_input)

# ========== RUN APPLICATION ==========

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
