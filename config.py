"""
Configuration file for Hospital Management System
Contains Flask and Flask-Security settings
"""
import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-hospital-management-2024'
    
    # Database Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Security Configuration - Use pbkdf2_sha256 (built-in, no external dependencies)
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'super-secret-salt-hospital-2024'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha256'
    SECURITY_PASSWORD_SCHEMES = ['pbkdf2_sha256']
    
    # Explicitly disable deprecated schemes
    SECURITY_DEPRECATED_PASSWORD_SCHEMES = []
    
    # Enable user registration for patients
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    
    # Enable username field for registration
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    
    # Redirect URLs after login/register
    SECURITY_POST_LOGIN_VIEW = '/dashboard'
    SECURITY_POST_REGISTER_VIEW = '/dashboard'
    SECURITY_POST_LOGOUT_VIEW = '/'
    
    # Flash message categories
    SECURITY_FLASH_MESSAGES = True
    
    # Disable some features we don't need
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = False
    SECURITY_CONFIRMABLE = False

    # ==========================
    # EMAIL CONFIGURATION (Ethereal - Testing)
    # ==========================
    MAIL_SERVER = 'smtp.ethereal.email'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'mabelle.grant@ethereal.email' 
    MAIL_PASSWORD = 'xBFzZ8wXabzX4XDfvq'