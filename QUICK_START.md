# 🏥 Hospital Management System - Quick Start Guide

## 🚀 Getting Started (3 Easy Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open in Browser
Navigate to: **http://127.0.0.1:5000**

---

## 🔐 Login Credentials

### 👨‍💼 Admin Account (Pre-created)
- **Email**: `admin@hospital.com`
- **Password**: `admin123`
- **Can do**: Manage doctors, patients, appointments, export data

### 🩺 Doctor Account (Created by Admin)
- **Note**: Doctors cannot self-register
- Admin must create doctor accounts
- Login with credentials provided by admin

### 🤕 Patient Account (Self-Registration)
1. Click "Register" on the homepage
2. Fill in: Username, Email, Password
3. Login and start booking appointments!

---

## 📋 Quick Demo Workflow

### As Admin:
1. Login as admin
2. Go to "Doctors" → Click "Add Doctor"
3. Fill doctor details (Dr. Smith, Cardiology, etc.)
4. Set availability (e.g., 09:00 to 17:00)
5. View all patients and appointments
6. Export appointments to CSV

### As Doctor:
1. Login with credentials from admin
2. View today's appointments on dashboard
3. Click "View" on any appointment
4. Fill treatment details and mark as completed
5. View patient's complete medical history

### As Patient:
1. Register or login
2. Update profile (blood group, medical history)
3. Browse doctors by department
4. Book appointment with available time slot
5. View your appointments
6. See treatment records after completion

---

## 📁 Project Structure

```
Cure One Hospital-Project/
├── app.py                    # Main application (all routes)
├── models.py                 # 7 database models
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── templates/                # HTML templates
│   ├── admin/               # Admin pages (6 files)
│   ├── doctor/              # Doctor pages (3 files)
│   ├── patient/             # Patient pages (6 files)
│   └── security/            # Login/Register
└── static/css/              # Custom styling
```

---

## ✨ Key Features

### 🔒 Security
- Bcrypt password hashing
- Role-based access control
- CSRF protection
- Session management

### 📊 Admin Panel
- Complete dashboard with statistics
- Doctor management (add/edit/delete)
- Patient management
- Appointment tracking
- CSV export

### 🩺 Doctor Portal
- Today's appointments dashboard
- Patient history viewer
- Treatment record creation
- Appointment status management

### 🏥 Patient Portal
- Easy appointment booking
- Doctor search & filter
- Profile management
- Medical history tracking
- Appointment cancellation

---

## 🎨 UI Highlights

- **Modern Design**: Bootstrap 5 with custom gradients
- **Responsive**: Works on desktop, tablet, and mobile
- **Icons**: Font Awesome 6.4.0 throughout
- **Color-Coded**: Status badges for quick identification
- **Smooth**: Animations and hover effects

---

## ⚡ Advanced Features

1. **Double Booking Prevention**: System checks availability automatically
2. **Dynamic Time Slots**: Generated from doctor's schedule
3. **Auto Patient Creation**: Patient profile created on registration
4. **Medical History**: Complete treatment records maintained
5. **Department Filter**: Find doctors by specialization

---

## 🔧 Configuration

### Database
- **Type**: SQLite
- **Location**: `instance/hospital.db`
- **Auto-created**: On first run

### Departments (Pre-loaded)
- Cardiology
- Pediatrics
- Orthopedics
- Neurology
- Dermatology
- General Medicine

---


## 🐛 Troubleshooting

### Database Issues
- Delete `instance/hospital.db` and restart app
- Database will be recreated automatically

### Login Issues
- Make sure email is correct (case-sensitive)
- Check if user exists in database
- Admin account is pre-created on first run

### Time Slot Issues
- Ensure doctor availability is set in 24-hour format
- Example: "09:00 to 17:00" not "9 AM to 5 PM"

### Appointment Booking Issues
- Check if time slot is already booked
- Select date within next 7 days only
- Ensure doctor has availability set

---

