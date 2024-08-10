# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'skin_care.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # Add these lines for additional configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit for file uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}