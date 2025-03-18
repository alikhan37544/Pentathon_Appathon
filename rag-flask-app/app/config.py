import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    UPLOAD_FOLDER = 'data/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit upload size to 16 MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

    # Database configuration (example)
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///instance/app.db'
    TRACK_MODIFICATIONS = False

    # Other configuration settings can be added here as needed
